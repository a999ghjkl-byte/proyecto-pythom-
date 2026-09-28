import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.services.auth_service import AuthService
from sistema_ventas_python.services.producto_service import ProductoService
from sistema_ventas_python.services.cliente_service import ClienteService
from sistema_ventas_python.services.venta_service import VentaService
from sistema_ventas_python.services.reporte_service import ReporteService

def run_tests():
    db = Database()
    print("[1/6] Base de datos SQLite3 inicializada correctamente.")

    auth = AuthService(db)
    ok, msg, admin_user = auth.autenticar("admin@lozano.com", "123456")
    assert ok and admin_user, f"Fallo admin: {msg}"
    print(f"[2/6] Auth Admin: OK -> {admin_user.nombre_completo} (Rol: {admin_user.rol})")

    ok2, msg2, consultor_user = auth.autenticar("lucia@edu.com", "lucia2177$")
    assert ok2 and consultor_user, f"Fallo consultor: {msg2}"
    print(f"[3/6] Auth Consultor: OK -> {consultor_user.nombre_completo} (Rol: {consultor_user.rol})")

    prod_service = ProductoService(db)
    prods = prod_service.listar_todos()
    assert len(prods) > 0, "No hay productos en BD"
    print(f"[4/6] Catálogo de Productos: OK ({len(prods)} productos registrados)")

    cliente_service = ClienteService(db)
    clientes = cliente_service.listar_todos()
    assert len(clientes) > 0, "No hay clientes en BD"
    print(f"[5/6] Cartera de Clientes: OK ({len(clientes)} clientes registrados)")

    reporte_service = ReporteService(db)
    resumen = reporte_service.obtener_resumen_general()
    print(f"[6/6] Métricas & Reportes: OK (Total ingresos: ${resumen['total_ingresos']:,.2f}, Pedidos: {resumen['total_pedidos']})")

    # Probar vistas (Tkinter / CustomTkinter import check)
    from sistema_ventas_python.views import (
        LoginView, MainWindow, DashboardView, ProductosView, VentasView, ClientesView, ReportesView
    )
    print("[ALL OK] Todas las capas de Lógica de Negocio y Vistas CustomTkinter compilan sin errores.")

if __name__ == "__main__":
    run_tests()
