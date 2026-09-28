from typing import List, Optional, Tuple
from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.models.models import Producto


class ProductoService:
    """Lógica de negocio para productos e inventario."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def listar_todos(self, solo_activos: bool = True) -> List[Producto]:
        """Obtiene la lista completa de productos."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock_actual, stock_minimo, is_active, created_at FROM productos"
            if solo_activos:
                query += " WHERE is_active = 1"
            query += " ORDER BY nombre ASC;"

            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                Producto(
                    id=row["id"],
                    codigo=row["codigo"],
                    nombre=row["nombre"],
                    categoria=row["categoria"],
                    precio_costo=float(row["precio_costo"]),
                    precio_venta=float(row["precio_venta"]),
                    stock_actual=int(row["stock_actual"]),
                    stock_minimo=int(row["stock_minimo"]),
                    is_active=bool(row["is_active"]),
                    created_at=str(row["created_at"])
                ) for row in rows
            ]

    def buscar(self, termino: str) -> List[Producto]:
        """Búsqueda flexible por código, nombre o categoría."""
        termino = f"%{termino.strip().lower()}%"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo, nombre, categoria, precio_costo, precio_venta, stock_actual, stock_minimo, is_active, created_at
                FROM productos
                WHERE is_active = 1 AND (LOWER(codigo) LIKE ? OR LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ?)
                ORDER BY nombre ASC;
            """, (termino, termino, termino))
            rows = cursor.fetchall()
            return [
                Producto(
                    id=row["id"],
                    codigo=row["codigo"],
                    nombre=row["nombre"],
                    categoria=row["categoria"],
                    precio_costo=float(row["precio_costo"]),
                    precio_venta=float(row["precio_venta"]),
                    stock_actual=int(row["stock_actual"]),
                    stock_minimo=int(row["stock_minimo"]),
                    is_active=bool(row["is_active"]),
                    created_at=str(row["created_at"])
                ) for row in rows
            ]

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE id = ?;", (producto_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Producto(
                id=row["id"],
                codigo=row["codigo"],
                nombre=row["nombre"],
                categoria=row["categoria"],
                precio_costo=float(row["precio_costo"]),
                precio_venta=float(row["precio_venta"]),
                stock_actual=int(row["stock_actual"]),
                stock_minimo=int(row["stock_minimo"]),
                is_active=bool(row["is_active"]),
                created_at=str(row["created_at"])
            )

    def guardar(self, producto: Producto) -> Tuple[bool, str, Optional[int]]:
        """Inserta o actualiza un producto con validaciones."""
        if not producto.codigo or not producto.nombre:
            return False, "El código y el nombre del producto son obligatorios.", None

        if producto.precio_venta < 0 or producto.precio_costo < 0:
            return False, "Los precios no pueden ser negativos.", None

        if producto.stock_actual < 0 or producto.stock_minimo < 0:
            return False, "Las cantidades de stock no pueden ser negativas.", None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if producto.id:
                    # Actualizar
                    cursor.execute("""
                        UPDATE productos
                        SET codigo = ?, nombre = ?, categoria = ?, precio_costo = ?,
                            precio_venta = ?, stock_actual = ?, stock_minimo = ?, is_active = ?
                        WHERE id = ?;
                    """, (
                        producto.codigo.strip().upper(),
                        producto.nombre.strip(),
                        producto.categoria.strip() or "General",
                        producto.precio_costo,
                        producto.precio_venta,
                        producto.stock_actual,
                        producto.stock_minimo,
                        1 if producto.is_active else 0,
                        producto.id
                    ))
                    conn.commit()
                    return True, "Producto actualizado correctamente.", producto.id
                else:
                    # Verificar código duplicado
                    cursor.execute("SELECT id FROM productos WHERE LOWER(codigo) = ?;", (producto.codigo.strip().lower(),))
                    if cursor.fetchone():
                        return False, f"El código '{producto.codigo}' ya está registrado.", None

                    # Insertar nuevo
                    cursor.execute("""
                        INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock_actual, stock_minimo, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        producto.codigo.strip().upper(),
                        producto.nombre.strip(),
                        producto.categoria.strip() or "General",
                        producto.precio_costo,
                        producto.precio_venta,
                        producto.stock_actual,
                        producto.stock_minimo,
                        1
                    ))
                    conn.commit()
                    return True, "Producto registrado exitosamente.", cursor.lastrowid
            except Exception as e:
                return False, f"Error al guardar producto: {str(e)}", None

    def eliminar(self, producto_id: int) -> Tuple[bool, str]:
        """Elimina suavemente (soft-delete) o física si no tiene historial."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Verificar si tiene ventas registradas
            cursor.execute("SELECT COUNT(*) as count FROM detalle_ventas WHERE producto_id = ?;", (producto_id,))
            tiene_ventas = cursor.fetchone()["count"] > 0

            if tiene_ventas:
                # Soft delete
                cursor.execute("UPDATE productos SET is_active = 0 WHERE id = ?;", (producto_id,))
                msg = "Producto archivado (desactivado) por tener historial de ventas."
            else:
                cursor.execute("DELETE FROM productos WHERE id = ?;", (producto_id,))
                msg = "Producto eliminado definitivamente."

            conn.commit()
            return True, msg
