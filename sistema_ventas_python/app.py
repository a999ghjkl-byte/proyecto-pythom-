import customtkinter as ctk
from typing import Optional
from sistema_ventas_python.models.models import Usuario
from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.views.login_view import LoginView
from sistema_ventas_python.views.main_window import MainWindow


class SalesApp(ctk.CTk):
    """Aplicación principal de escritorio construida 100% en Python."""

    def __init__(self):
        super().__init__()

        # Configuración estética global
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("Sistema de Ventas & Facturación — Python Desktop Suite")
        self.geometry("1240x780")
        self.minsize(1050, 680)

        # Inicializar base de datos SQLite y datos demo si no existen
        self.db = Database()

        # Usuario autenticado en la sesión
        self.usuario_actual: Optional[Usuario] = None

        # Contenedor raíz
        self.root_container = ctk.CTkFrame(self, fg_color="transparent")
        self.root_container.pack(fill="both", expand=True)

        # Mostrar pantalla inicial de Login
        self.mostrar_login()

    def mostrar_login(self):
        """Muestra la vista de autenticación."""
        self.usuario_actual = None
        for w in self.root_container.winfo_children():
            w.destroy()

        login_view = LoginView(
            self.root_container,
            on_login_success=self.al_iniciar_sesion
        )
        login_view.pack(fill="both", expand=True)

    def al_iniciar_sesion(self, usuario: Usuario):
        """Callback al verificar credenciales válidas."""
        self.usuario_actual = usuario
        for w in self.root_container.winfo_children():
            w.destroy()

        main_window = MainWindow(
            self.root_container,
            usuario=usuario,
            on_logout=self.mostrar_login
        )
        main_window.pack(fill="both", expand=True)


def run_app():
    """Función de lanzamiento de la aplicación."""
    app = SalesApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
