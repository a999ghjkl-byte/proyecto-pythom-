from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sistema_ventas_python.database.connection import Database


class ReporteService:
    """Lógica de negocio para estadísticas, KPIs, reportes y métricas."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def obtener_resumen_general(self) -> Dict[str, Any]:
        """Calcula los KPIs primordiales del negocio."""
        hoy_str = date.today().strftime("%Y-%m-%d")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Total ventas históricas
            cursor.execute("SELECT COALESCE(SUM(total), 0) as total, COUNT(*) as cantidad FROM ventas;")
            row_ventas = cursor.fetchone()
            total_ingresos = float(row_ventas["total"])
            total_pedidos = int(row_ventas["cantidad"])

            # 2. Ventas del día de hoy
            cursor.execute("SELECT COALESCE(SUM(total), 0) as total, COUNT(*) as cantidad FROM ventas WHERE DATE(fecha_venta) = ?;", (hoy_str,))
            row_hoy = cursor.fetchone()
            ventas_hoy_monto = float(row_hoy["total"])
            pedidos_hoy = int(row_hoy["cantidad"])

            # 3. Ticket promedio
            ticket_promedio = round(total_ingresos / max(total_pedidos, 1), 2) if total_pedidos > 0 else 0.0

            # 4. Total clientes activos
            cursor.execute("SELECT COUNT(*) as count FROM clientes WHERE is_active = 1;")
            total_clientes = int(cursor.fetchone()["count"])

            # 5. Total productos y productos con stock bajo o crítico
            cursor.execute("SELECT COUNT(*) as count FROM productos WHERE is_active = 1;")
            total_productos = int(cursor.fetchone()["count"])

            cursor.execute("SELECT COUNT(*) as count FROM productos WHERE is_active = 1 AND stock_actual <= stock_minimo;")
            productos_stock_bajo = int(cursor.fetchone()["count"])

            # 6. Unidades totales en stock
            cursor.execute("SELECT COALESCE(SUM(stock_actual), 0) as total_unidades FROM productos WHERE is_active = 1;")
            total_stock_unidades = int(cursor.fetchone()["total_unidades"])

            return {
                "total_ingresos": total_ingresos,
                "total_pedidos": total_pedidos,
                "ventas_hoy_monto": ventas_hoy_monto,
                "pedidos_hoy": pedidos_hoy,
                "ticket_promedio": ticket_promedio,
                "total_clientes": total_clientes,
                "total_productos": total_productos,
                "productos_stock_bajo": productos_stock_bajo,
                "total_stock_unidades": total_stock_unidades
            }

    def obtener_top_productos(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Top de productos más vendidos en unidades y monto facturado."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.nombre,
                    p.codigo,
                    p.categoria,
                    COALESCE(SUM(dv.cantidad), 0) as unidades_vendidas,
                    COALESCE(SUM(dv.subtotal), 0) as total_generado
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                GROUP BY p.id, p.nombre, p.codigo, p.categoria
                ORDER BY unidades_vendidas DESC, total_generado DESC
                LIMIT ?;
            """, (limite,))
            rows = cursor.fetchall()
            return [
                {
                    "nombre": r["nombre"],
                    "codigo": r["codigo"],
                    "categoria": r["categoria"],
                    "unidades": int(r["unidades_vendidas"]),
                    "monto": float(r["total_generado"])
                } for r in rows
            ]

    def filtrar_ventas(self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, cliente_termino: Optional[str] = None) -> List[Dict[str, Any]]:
        """Reporte filtrado de ventas con subtotales y cliente."""
        query = """
            SELECT 
                v.id, v.codigo_venta, v.fecha_venta, v.metodo_pago,
                v.subtotal, v.impuesto, v.descuento, v.total,
                c.nombre_razon_social as cliente_nombre, c.numero_documento as cliente_doc,
                u.nombre_completo as vendedor_nombre
            FROM ventas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN usuarios u ON v.usuario_id = u.id
            WHERE 1=1
        """
        params = []

        if fecha_inicio:
            query += " AND DATE(v.fecha_venta) >= ?"
            params.append(fecha_inicio)

        if fecha_fin:
            query += " AND DATE(v.fecha_venta) <= ?"
            params.append(fecha_fin)

        if cliente_termino and cliente_termino.strip():
            query += " AND (LOWER(c.nombre_razon_social) LIKE ? OR LOWER(c.numero_documento) LIKE ?)"
            term = f"%{cliente_termino.strip().lower()}%"
            params.extend([term, term])

        query += " ORDER BY v.fecha_venta DESC;"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "codigo": r["codigo_venta"],
                    "fecha": str(r["fecha_venta"]),
                    "metodo_pago": r["metodo_pago"],
                    "cliente": r["cliente_nombre"],
                    "cliente_doc": r["cliente_doc"],
                    "vendedor": r["vendedor_nombre"],
                    "subtotal": float(r["subtotal"]),
                    "impuesto": float(r["impuesto"]),
                    "descuento": float(r["descuento"]),
                    "total": float(r["total"])
                } for r in rows
            ]

    def resumen_por_metodo_pago(self) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT metodo_pago, COUNT(*) as cantidad, SUM(total) as monto
                FROM ventas
                GROUP BY metodo_pago
                ORDER BY monto DESC;
            """)
            rows = cursor.fetchall()
            return [
                {
                    "metodo": r["metodo_pago"],
                    "cantidad": int(r["cantidad"]),
                    "monto": float(r["monto"])
                } for r in rows
            ]
