from typing import List, Optional, Tuple, Dict
from datetime import datetime
from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.models.models import Producto, ItemCarrito, Venta, DetalleVenta


class VentaService:
    """Lógica de negocio para ventas, carrito y actualización atómica de inventario."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def calcular_totales(self, items: List[ItemCarrito], porcentaje_impuesto: float = 18.0, descuento: float = 0.0) -> Dict[str, float]:
        """Calcula subtotal, impuestos y total para una lista de items de carrito."""
        subtotal = round(sum(item.subtotal for item in items), 2)
        descuento = max(0.0, round(float(descuento), 2))
        base_imponible = max(0.0, subtotal - descuento)
        impuesto = round(base_imponible * (porcentaje_impuesto / 100.0), 2)
        total = round(base_imponible + impuesto, 2)

        return {
            "subtotal": subtotal,
            "descuento": descuento,
            "impuesto": impuesto,
            "total": total
        }

    def generar_siguiente_codigo(self) -> str:
        """Genera un código consecutivo único para la venta."""
        anio_actual = datetime.now().year
        prefijo = f"VNT-{anio_actual}-"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT codigo_venta FROM ventas 
                WHERE codigo_venta LIKE ?
                ORDER BY id DESC LIMIT 1;
            """, (f"{prefijo}%",))
            row = cursor.fetchone()

            if row:
                ultimo_codigo = row["codigo_venta"]
                try:
                    num_str = ultimo_codigo.split("-")[-1]
                    siguiente_num = int(num_str) + 1
                except Exception:
                    siguiente_num = 1
            else:
                siguiente_num = 1

            return f"{prefijo}{siguiente_num:04d}"

    def procesar_venta(
        self,
        cliente_id: int,
        usuario_id: int,
        items: List[ItemCarrito],
        metodo_pago: str = "EFECTIVO",
        porcentaje_impuesto: float = 18.0,
        descuento: float = 0.0,
        notas: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Venta]]:
        """
        Registra la venta y descuenta el stock de manera atómica (transacción SQLite).
        Si falta stock de algún producto, aborta la transacción y devuelve error explicativo.
        """
        if not cliente_id:
            return False, "Debe seleccionar un cliente para la venta.", None

        if not items:
            return False, "El carrito de compras está vacío.", None

        totales = self.calcular_totales(items, porcentaje_impuesto, descuento)
        codigo_venta = self.generar_siguiente_codigo()

        conn = self.db.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION;")
            cursor = conn.cursor()

            # 1. Validar stock de todos los productos antes de insertar
            for item in items:
                cursor.execute("SELECT nombre, stock_actual, is_active FROM productos WHERE id = ?;", (item.producto.id,))
                prod_row = cursor.fetchone()

                if not prod_row or not prod_row["is_active"]:
                    conn.rollback()
                    return False, f"El producto '{item.producto.nombre}' ya no está disponible.", None

                if prod_row["stock_actual"] < item.cantidad:
                    conn.rollback()
                    return False, (
                        f"Stock insuficiente para '{prod_row['nombre']}'. "
                        f"Disponible: {prod_row['stock_actual']}, Solicitado: {item.cantidad}."
                    ), None

            # 2. Insertar cabecera de venta
            cursor.execute("""
                INSERT INTO ventas (codigo_venta, cliente_id, usuario_id, metodo_pago, subtotal, impuesto, descuento, total, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                codigo_venta,
                cliente_id,
                usuario_id,
                metodo_pago,
                totales["subtotal"],
                totales["impuesto"],
                totales["descuento"],
                totales["total"],
                notas
            ))
            venta_id = cursor.lastrowid

            # 3. Insertar detalles y descontar stock
            detalles_venta: List[DetalleVenta] = []
            for item in items:
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                """, (
                    venta_id,
                    item.producto.id,
                    item.cantidad,
                    item.precio_unitario,
                    item.subtotal
                ))
                detalle_id = cursor.lastrowid

                # Descontar stock
                cursor.execute("""
                    UPDATE productos
                    SET stock_actual = stock_actual - ?
                    WHERE id = ?;
                """, (item.cantidad, item.producto.id))

                detalles_venta.append(DetalleVenta(
                    id=detalle_id,
                    venta_id=venta_id,
                    producto_id=item.producto.id,
                    producto_nombre=item.producto.nombre,
                    producto_codigo=item.producto.codigo,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.subtotal
                ))

            # 4. Obtener información de cliente y usuario para el comprobante
            cursor.execute("SELECT nombre_razon_social, numero_documento FROM clientes WHERE id = ?;", (cliente_id,))
            c_row = cursor.fetchone()
            cliente_nombre = c_row["nombre_razon_social"] if c_row else "Cliente"
            cliente_doc = c_row["numero_documento"] if c_row else ""

            cursor.execute("SELECT nombre_completo FROM usuarios WHERE id = ?;", (usuario_id,))
            u_row = cursor.fetchone()
            usuario_nombre = u_row["nombre_completo"] if u_row else "Cajero"

            conn.commit()

            venta_completada = Venta(
                id=venta_id,
                codigo_venta=codigo_venta,
                cliente_id=cliente_id,
                cliente_nombre=cliente_nombre,
                cliente_documento=cliente_doc,
                usuario_id=usuario_id,
                usuario_nombre=usuario_nombre,
                metodo_pago=metodo_pago,
                subtotal=totales["subtotal"],
                impuesto=totales["impuesto"],
                descuento=totales["descuento"],
                total=totales["total"],
                notas=notas,
                fecha_venta=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                detalles=detalles_venta
            )

            return True, f"¡Venta {codigo_venta} completada exitosamente!", venta_completada

        except Exception as e:
            conn.rollback()
            return False, f"Error en la transacción de venta: {str(e)}", None
        finally:
            conn.close()

    def listar_ventas(self, limite: int = 50) -> List[Venta]:
        """Obtiene las ventas recientes con sus datos asociados."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    v.id, v.codigo_venta, v.cliente_id, v.usuario_id, v.metodo_pago,
                    v.subtotal, v.impuesto, v.descuento, v.total, v.notas, v.fecha_venta,
                    c.nombre_razon_social as cliente_nombre, c.numero_documento as cliente_doc,
                    u.nombre_completo as usuario_nombre
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                JOIN usuarios u ON v.usuario_id = u.id
                ORDER BY v.fecha_venta DESC
                LIMIT ?;
            """, (limite,))
            rows = cursor.fetchall()

            ventas = []
            for r in rows:
                ventas.append(Venta(
                    id=r["id"],
                    codigo_venta=r["codigo_venta"],
                    cliente_id=r["cliente_id"],
                    cliente_nombre=r["cliente_nombre"],
                    cliente_documento=r["cliente_doc"],
                    usuario_id=r["usuario_id"],
                    usuario_nombre=r["usuario_nombre"],
                    metodo_pago=r["metodo_pago"],
                    subtotal=float(r["subtotal"]),
                    impuesto=float(r["impuesto"]),
                    descuento=float(r["descuento"]),
                    total=float(r["total"]),
                    notas=r["notas"],
                    fecha_venta=str(r["fecha_venta"])
                ))
            return ventas

    def obtener_detalle_venta(self, venta_id: int) -> List[DetalleVenta]:
        """Obtiene las líneas de producto de una venta."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dv.id, dv.venta_id, dv.producto_id, dv.cantidad, dv.precio_unitario, dv.subtotal,
                       p.nombre as producto_nombre, p.codigo as producto_codigo
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?;
            """, (venta_id,))
            rows = cursor.fetchall()
            return [
                DetalleVenta(
                    id=r["id"],
                    venta_id=r["venta_id"],
                    producto_id=r["producto_id"],
                    producto_nombre=r["producto_nombre"],
                    producto_codigo=r["producto_codigo"],
                    cantidad=int(r["cantidad"]),
                    precio_unitario=float(r["precio_unitario"]),
                    subtotal=float(r["subtotal"])
                ) for r in rows
            ]
