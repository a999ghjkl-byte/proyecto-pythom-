import customtkinter as ctk
from typing import Callable, Optional
from sistema_ventas_python.services.auth_service import AuthService
from sistema_ventas_python.models.models import Usuario


class LoginView(ctk.CTkFrame):
    """Vista de inicio de sesión moderna y elegante con CustomTkinter."""

    def __init__(self, master, on_login_success: Callable[[Usuario], None], auth_service: Optional[AuthService] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_login_success = on_login_success
        self.auth_service = auth_service or AuthService()

        self._build_ui()

    def _build_ui(self):
        # Configurar grid centrado
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Contenedor central (Card)
        card = ctk.CTkFrame(
            self,
            width=460,
            corner_radius=20,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        card.grid(row=0, column=0, padx=20, pady=40)
        card.grid_propagate(True)

        # Padding interior
        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(padx=35, pady=35, fill="both", expand=True)

        # Logo / Emblema
        emblem = ctk.CTkLabel(
            inner_frame,
            text="💎",
            font=ctk.CTkFont(size=44)
        )
        emblem.pack(pady=(0, 5))

        # Título
        title = ctk.CTkLabel(
            inner_frame,
            text="SISTEMA DE VENTAS",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=("#1a202c", "#f7fafc")
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            inner_frame,
            text="Gestión Comercial, POS & Facturación",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("#718096", "#a0aec0")
        )
        subtitle.pack(pady=(2, 20))

        # Mensaje de error / notificación
        self.lbl_mensaje = ctk.CTkLabel(
            inner_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e53e3e",
            wraplength=360
        )
        self.lbl_mensaje.pack(pady=(0, 10))

        # Campo Usuario / Correo
        lbl_user = ctk.CTkLabel(
            inner_frame,
            text="Usuario o Correo Electrónico",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        lbl_user.pack(fill="x", pady=(0, 4))

        self.txt_usuario = ctk.CTkEntry(
            inner_frame,
            placeholder_text="ej: admin@lozano.com",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.txt_usuario.pack(fill="x", pady=(0, 15))
        self.txt_usuario.insert(0, "admin@lozano.com")

        # Campo Contraseña
        lbl_pass = ctk.CTkLabel(
            inner_frame,
            text="Contraseña de Acceso",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        lbl_pass.pack(fill="x", pady=(0, 4))

        self.pass_container = ctk.CTkFrame(inner_frame, fg_color="transparent")
        self.pass_container.pack(fill="x", pady=(0, 10))

        self.txt_password = ctk.CTkEntry(
            self.pass_container,
            placeholder_text="••••••••",
            show="•",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.txt_password.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.txt_password.insert(0, "123456")

        self.btn_toggle_pass = ctk.CTkButton(
            self.pass_container,
            text="👁️",
            width=44,
            height=44,
            corner_radius=10,
            fg_color=("#edf2f7", "#2d3748"),
            hover_color=("#e2e8f0", "#4a5568"),
            text_color=("#2d3748", "#e2e8f0"),
            command=self._toggle_password_visibility
        )
        self.btn_toggle_pass.pack(side="right")

        # Botón Iniciar Sesión grande
        self.btn_login = ctk.CTkButton(
            inner_frame,
            text="Acceder al Sistema  ➔",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self._ejecutar_login
        )
        self.btn_login.pack(fill="x", pady=(15, 20))

        # Atajo Enter en teclado
        self.txt_usuario.bind("<Return>", lambda event: self._ejecutar_login())
        self.txt_password.bind("<Return>", lambda event: self._ejecutar_login())

        # Acceso Rápido / Credenciales de demostración
        demo_frame = ctk.CTkFrame(
            inner_frame,
            corner_radius=12,
            fg_color=("#f8fafc", "#171923"),
            border_width=1,
            border_color=("#edf2f7", "#2d3748")
        )
        demo_frame.pack(fill="x", pady=(5, 0))

        lbl_demo = ctk.CTkLabel(
            demo_frame,
            text="🔑 Accesos Rápidos de Prueba",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#4a5568", "#a0aec0")
        )
        lbl_demo.pack(pady=(8, 4))

        btns_row = ctk.CTkFrame(demo_frame, fg_color="transparent")
        btns_row.pack(pady=(0, 8), fill="x", padx=10)

        btn_admin = ctk.CTkButton(
            btns_row,
            text="Admin (123456)",
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color=("#e2e8f0", "#2d3748"),
            text_color=("#2b6cb0", "#63b3ed"),
            hover_color=("#cbd5e0", "#4a5568"),
            command=lambda: self._set_credentials("admin@lozano.com", "123456")
        )
        btn_admin.pack(side="left", expand=True, fill="x", padx=3)

        btn_lucia = ctk.CTkButton(
            btns_row,
            text="Consultor (lucia@edu.com)",
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color=("#e2e8f0", "#2d3748"),
            text_color=("#2c7a7b", "#4fd1c5"),
            hover_color=("#cbd5e0", "#4a5568"),
            command=lambda: self._set_credentials("lucia@edu.com", "lucia2177$")
        )
        btn_lucia.pack(side="right", expand=True, fill="x", padx=3)

    def _toggle_password_visibility(self):
        if self.txt_password.cget("show") == "•":
            self.txt_password.configure(show="")
            self.btn_toggle_pass.configure(text="🙈")
        else:
            self.txt_password.configure(show="•")
            self.btn_toggle_pass.configure(text="👁️")

    def _set_credentials(self, username: str, passw: str):
        self.txt_usuario.delete(0, "end")
        self.txt_usuario.insert(0, username)
        self.txt_password.delete(0, "end")
        self.txt_password.insert(0, passw)
        self.lbl_mensaje.configure(text="")

    def _ejecutar_login(self):
        username = self.txt_usuario.get()
        password = self.txt_password.get()

        self.btn_login.configure(state="disabled", text="Verificando...")
        self.update_idletasks()

        exito, mensaje, usuario = self.auth_service.autenticar(username, password)
        self.btn_login.configure(state="normal", text="Acceder al Sistema  ➔")

        if exito and usuario:
            self.lbl_mensaje.configure(text="Acceso concedido.", text_color="#38a169")
            self.on_login_success(usuario)
        else:
            self.lbl_mensaje.configure(text=f"⚠️ {mensaje}", text_color="#e53e3e")
