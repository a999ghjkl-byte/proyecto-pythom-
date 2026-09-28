import customtkinter as ctk
from datetime import datetime
from typing import Callable, Optional
from sistema_ventas_python.models.models import Usuario
from sistema_ventas_python.views.dashboard_view import DashboardView
from sistema_ventas_python.views.ventas_view import VentasView
from sistema_ventas_python.views.productos_view import ProductosView
from sistema_ventas_python.views.clientes_view import ClientesView
from sistema_ventas_python.views.reportes_view import ReportesView


class MainWindow(ctk.CTkFrame):
    """Ventana principal moderna con Sidebar de navegación y contenedor dinámico de vistas."""

    def __init__(self, master, usuario: Usuario, on_logout: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.on_logout = on_logout
        self.current_view_name = ""
        self.nav_buttons = {}

        self._build_ui()
        # Vista inicial: siempre el Dashboard
        self.navegar("dashboard")
        self._iniciar_reloj()

    def _build_ui(self):
        # 2 Columnas: Sidebar (Izq) y Área de Contenido (Der)
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=("white", "#11141c"),
            border_width=1,
            border_color=("#e2e8f0", "#1e222d")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 15))

        lbl_logo = ctk.CTkLabel(brand_frame, text="💎", font=ctk.CTkFont(size=28))
        lbl_logo.pack(side="left", padx=(0, 10))

        brand_text = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text.pack(side="left", fill="both")

        lbl_brand = ctk.CTkLabel(
            brand_text,
            text="VENTAS PRO",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w"
        )
        lbl_brand.pack(fill="x")

        lbl_tag = ctk.CTkLabel(
            brand_text,
            text="Suite Comercial Python",
            font=ctk.CTkFont(size=11),
            text_color="#718096",
            anchor="w"
        )
        lbl_tag.pack(fill="x")

        # Divisor
        div = ctk.CTkFrame(self.sidebar, height=1, fg_color=("#e2e8f0", "#1e222d"))
        div.pack(fill="x", padx=15, pady=(0, 15))

        # Tarjeta de Usuario Activo
        user_card = ctk.CTkFrame(
            self.sidebar,
            corner_radius=12,
            fg_color=("#f8fafc", "#1a1e29"),
            border_width=1,
            border_color=("#edf2f7", "#242938")
        )
        user_card.pack(fill="x", padx=14, pady=(0, 18), ipady=6)

        initial = self.usuario.nombre_completo[0].upper() if self.usuario.nombre_completo else "U"
        lbl_avatar = ctk.CTkLabel(
            user_card,
            text=initial,
            width=36,
            height=36,
            corner_radius=18,
            fg_color="#2563eb",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_avatar.pack(side="left", padx=(10, 8))

        u_info = ctk.CTkFrame(user_card, fg_color="transparent")
        u_info.pack(side="left", fill="both", expand=True)

        lbl_u_name = ctk.CTkLabel(
            u_info,
            text=self.usuario.nombre_completo,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        lbl_u_name.pack(fill="x")

        lbl_u_rol = ctk.CTkLabel(
            u_info,
            text=f"Rol: {self.usuario.rol}",
            font=ctk.CTkFont(size=10),
            text_color="#3b82f6",
            anchor="w"
        )
        lbl_u_rol.pack(fill="x")

        # Botones de Navegación
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=12)

        # Si el usuario es CONSULTOR ("un usuario q solo tenga aceso al dashbor con informacion brebe nada mas")
        # solo se le muestra la opción del Dashboard. Si es ADMIN o VENDEDOR, tiene el menú completo.
        es_consultor = self.usuario.rol == "CONSULTOR"

        if es_consultor:
            items_nav = [
                ("dashboard", "📊 Resumen Ejecutivo"),
            ]
        else:
            items_nav = [
                ("dashboard", "📊 Resumen General"),
                ("ventas", "🛒 Punto de Venta (POS)"),
                ("productos", "📦 Catálogo & Stock"),
                ("clientes", "👥 Cartera de Clientes"),
                ("reportes", "📑 Reportes & Ventas"),
            ]

        for view_key, label_text in items_nav:
            btn = ctk.CTkButton(
                nav_container,
                text=f"  {label_text}",
                height=42,
                corner_radius=10,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color="transparent",
                text_color=("#4a5568", "#cbd5e1"),
                hover_color=("#edf2f7", "#1e222d"),
                command=lambda k=view_key: self.navegar(k)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[view_key] = btn

        # Footer Sidebar con Toggle de Tema y Logout
        footer_side = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_side.pack(fill="x", padx=12, pady=15)

        self.btn_tema = ctk.CTkButton(
            footer_side,
            text="🌓 Cambiar Tema",
            height=34,
            corner_radius=8,
            fg_color=("#edf2f7", "#1a1e29"),
            text_color=("#4a5568", "#cbd5e1"),
            hover_color=("#e2e8f0", "#242938"),
            font=ctk.CTkFont(size=11),
            command=self._toggle_theme
        )
        self.btn_tema.pack(fill="x", pady=(0, 8))

        btn_logout = ctk.CTkButton(
            footer_side,
            text="🚪 Cerrar Sesión",
            height=38,
            corner_radius=10,
            fg_color="#fee2e2",
            hover_color="#fca5a5",
            text_color="#dc2626",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_logout
        )
        btn_logout.pack(fill="x")

        # ================= CONTENEDOR PRINCIPAL =================
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Barra Superior de la App
        self.top_header = ctk.CTkFrame(
            self.main_container,
            height=54,
            corner_radius=0,
            fg_color=("white", "#11141c"),
            border_width=1,
            border_color=("#e2e8f0", "#1e222d")
        )
        self.top_header.grid(row=0, column=0, sticky="ew")
        self.top_header.pack_propagate(False)

        self.lbl_seccion_titulo = ctk.CTkLabel(
            self.top_header,
            text="Panel Principal",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            anchor="w"
        )
        self.lbl_seccion_titulo.pack(side="left", padx=20)

        # Reloj en vivo
        self.lbl_reloj = ctk.CTkLabel(
            self.top_header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#718096"
        )
        self.lbl_reloj.pack(side="right", padx=20)

        # Contenedor dinámico de vistas
        self.view_host = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_host.grid(row=1, column=0, sticky="nsew")

    def _iniciar_reloj(self):
        ahora = datetime.now().strftime("%d/%m/%Y • %H:%M:%S")
        self.lbl_reloj.configure(text=f"🕒 {ahora}")
        self.after(1000, self._iniciar_reloj)

    def _toggle_theme(self):
        modo = ctk.get_appearance_mode()
        if modo == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def navegar(self, view_name: str):
        """Alterna limpiamente la vista actual dentro del view_host."""
        self.current_view_name = view_name

        # Actualizar estilo de botones del sidebar
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(
                    fg_color="#2563eb",
                    text_color="white",
                    hover_color="#1d4ed8"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#4a5568", "#cbd5e1"),
                    hover_color=("#edf2f7", "#1e222d")
                )

        # Destruir vista anterior
        for w in self.view_host.winfo_children():
            w.destroy()

        # Instanciar y montar la vista solicitada
        if view_name == "dashboard":
            self.lbl_seccion_titulo.configure(text="📊 Resumen Ejecutivo & Métricas")
            view = DashboardView(self.view_host, usuario=self.usuario, on_navigate=self.navegar)
            view.pack(fill="both", expand=True)

        elif view_name == "ventas":
            self.lbl_seccion_titulo.configure(text="🛒 Punto de Venta (POS) & Carrito")
            view = VentasView(self.view_host, usuario=self.usuario)
            view.pack(fill="both", expand=True)

        elif view_name == "productos":
            self.lbl_seccion_titulo.configure(text="📦 Catálogo de Productos & Stock")
            view = ProductosView(self.view_host, usuario=self.usuario)
            view.pack(fill="both", expand=True)

        elif view_name == "clientes":
            self.lbl_seccion_titulo.configure(text="👥 Cartera de Clientes")
            view = ClientesView(self.view_host, usuario=self.usuario)
            view.pack(fill="both", expand=True)

        elif view_name == "reportes":
            self.lbl_seccion_titulo.configure(text="📑 Reportes & Historial de Ventas")
            view = ReportesView(self.view_host, usuario=self.usuario)
            view.pack(fill="both", expand=True)
