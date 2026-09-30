import customtkinter as ctk
from typing import Callable, Optional
from sistema_ventas_python.services.reporte_service import ReporteService
from sistema_ventas_python.models.models import Usuario


class DashboardView(ctk.CTkFrame):
    """Panel general con métricas, KPIs, productos destacados y gráficos de estado."""

    def __init__(self, master, usuario: Usuario, on_navigate: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.on_navigate = on_navigate
        self.reporte_service = ReporteService()

        self._build_ui()
        self.actualizar_datos()

    def _build_ui(self):
        # Frame desplazable para acomodar cualquier resolución
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=15)

        # Header con saludo y rol
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        saludo_text = f"¡Bienvenido/a, {self.usuario.nombre_completo}!"
        lbl_saludo = ctk.CTkLabel(
            header_frame,
            text=saludo_text,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            anchor="w"
        )
        lbl_saludo.pack(side="left")

        rol_badge = ctk.CTkLabel(
            header_frame,
            text=f" Rol: {self.usuario.rol} ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2b6cb0" if self.usuario.rol == "ADMIN" else "#2c7a7b",
            text_color="white",
            corner_radius=8
        )
        rol_badge.pack(side="right", padx=10)

        # Grid de Tarjetas de Métricas (KPI Cards)
        self.cards_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.cards_container.pack(fill="x", pady=(0, 20))
        for i in range(4):
            self.cards_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        self.card_ventas = self._crear_kpi_card(self.cards_container, 0, "💰 Facturación Total", "S/. 0.00", "Hoy: S/. 0.00", "#10b981")
        self.card_pedidos = self._crear_kpi_card(self.cards_container, 1, "🛍️ Pedidos Realizados", "0", "Órdenes cerradas", "#3b82f6")
        self.card_ticket = self._crear_kpi_card(self.cards_container, 2, "🏷️ Ticket Promedio", "S/. 0.00", "Por transacción", "#8b5cf6")
        self.card_stock = self._crear_kpi_card(self.cards_container, 3, "⚠️ Stock Bajo / Crítico", "0 productos", "Alerta inventario", "#ef4444")

        # Fila de Accesos directos si tiene permisos (no consultor)
        if self.usuario.rol != "CONSULTOR" and self.on_navigate:
            actions_frame = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color=("white", "#1e222d"), border_width=1, border_color=("#e2e8f0", "#2d3748"))
            actions_frame.pack(fill="x", pady=(0, 20), ipady=10)

            lbl_actions = ctk.CTkLabel(
                actions_frame,
                text="⚡ Acciones Rápidas:",
                font=ctk.CTkFont(size=13, weight="bold")
            )
            lbl_actions.pack(side="left", padx=20)

            btn_nueva_venta = ctk.CTkButton(
                actions_frame,
                text="🛒 Nueva Venta (POS)",
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: self.on_navigate("ventas")
            )
            btn_nueva_venta.pack(side="left", padx=8)

            btn_nuevo_prod = ctk.CTkButton(
                actions_frame,
                text="📦 Gestionar Productos",
                fg_color="#059669",
                hover_color="#047857",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: self.on_navigate("productos")
            )
            btn_nuevo_prod.pack(side="left", padx=8)

            btn_clientes = ctk.CTkButton(
                actions_frame,
                text="👥 Ver Clientes",
                fg_color="#4f46e5",
                hover_color="#4338ca",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: self.on_navigate("clientes")
            )
            btn_clientes.pack(side="left", padx=8)

        # Sección de 2 columnas: Top Productos & Distribución de Pagos
        cols_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cols_frame.pack(fill="both", expand=True, pady=(0, 20))
        cols_frame.grid_columnconfigure(0, weight=3)
        cols_frame.grid_columnconfigure(1, weight=2)

        # Columna Izquierda: Top Productos más vendidos
        panel_top = ctk.CTkFrame(
            cols_frame,
            corner_radius=16,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        panel_top.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_top_title = ctk.CTkLabel(
            panel_top,
            text="🏆 Top Productos Más Vendidos",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        lbl_top_title.pack(fill="x", padx=16, pady=(16, 12))

        self.top_prods_container = ctk.CTkFrame(panel_top, fg_color="transparent")
        self.top_prods_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Columna Derecha: Métodos de Pago
        panel_pagos = ctk.CTkFrame(
            cols_frame,
            corner_radius=16,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        panel_pagos.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        lbl_pagos_title = ctk.CTkLabel(
            panel_pagos,
            text="💳 Ventas por Método de Pago",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        lbl_pagos_title.pack(fill="x", padx=16, pady=(16, 12))

        self.pagos_container = ctk.CTkFrame(panel_pagos, fg_color="transparent")
        self.pagos_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _crear_kpi_card(self, parent, col: int, titulo: str, valor_inicial: str, subtexto: str, color_acento: str) -> dict:
        card = ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        lbl_tit = ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#4a5568", "#cbd5e1"),
            anchor="w"
        )
        lbl_tit.pack(fill="x", padx=16, pady=(16, 4))

        lbl_val = ctk.CTkLabel(
            card,
            text=valor_inicial,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=color_acento,
            anchor="w"
        )
        lbl_val.pack(fill="x", padx=16, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(
            card,
            text=subtexto,
            font=ctk.CTkFont(size=11),
            text_color=("#718096", "#a0aec0"),
            anchor="w"
        )
        lbl_sub.pack(fill="x", padx=16, pady=(0, 16))

        return {"card": card, "val": lbl_val, "sub": lbl_sub}

    def actualizar_datos(self):
        """Consulta métricas a través de la capa de servicio y actualiza la vista."""
        resumen = self.reporte_service.obtener_resumen_general()

        self.card_ventas["val"].configure(text=f"S/. {resumen['total_ingresos']:,.2f}")
        self.card_ventas["sub"].configure(text=f"Hoy: S/. {resumen['ventas_hoy_monto']:,.2f} ({resumen['pedidos_hoy']} ventas)")

        self.card_pedidos["val"].configure(text=str(resumen["total_pedidos"]))
        self.card_pedidos["sub"].configure(text=f"{resumen['total_clientes']} clientes registrados")

        self.card_ticket["val"].configure(text=f"S/. {resumen['ticket_promedio']:,.2f}")
        self.card_ticket["sub"].configure(text=f"{resumen['total_stock_unidades']} unidades en catálogo")

        stock_bajo = resumen["productos_stock_bajo"]
        self.card_stock["val"].configure(
            text=f"{stock_bajo} productos",
            text_color="#ef4444" if stock_bajo > 0 else "#10b981"
        )
        self.card_stock["sub"].configure(
            text="Requieren reposición" if stock_bajo > 0 else "Nivel de stock óptimo"
        )

        # Actualizar Top Productos
        for w in self.top_prods_container.winfo_children():
            w.destroy()

        top_prods = self.reporte_service.obtener_top_productos(5)
        if not top_prods:
            lbl_vacio = ctk.CTkLabel(self.top_prods_container, text="Aún no hay ventas registradas.", text_color="#718096")
            lbl_vacio.pack(pady=20)
        else:
            for idx, p in enumerate(top_prods, start=1):
                item_row = ctk.CTkFrame(self.top_prods_container, fg_color=("#f8fafc", "#282e3d"), corner_radius=10)
                item_row.pack(fill="x", pady=4, ipady=6, padx=2)

                lbl_num = ctk.CTkLabel(item_row, text=f"#{idx}", width=32, font=ctk.CTkFont(weight="bold", size=13), text_color="#2563eb")
                lbl_num.pack(side="left", padx=8)

                info_frame = ctk.CTkFrame(item_row, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True)

                lbl_nombre = ctk.CTkLabel(info_frame, text=p["nombre"], font=ctk.CTkFont(weight="bold", size=13), anchor="w")
                lbl_nombre.pack(fill="x")

                lbl_meta = ctk.CTkLabel(info_frame, text=f"{p['categoria']} • {p['unidades']} unidades vendidas", font=ctk.CTkFont(size=11), text_color="#718096", anchor="w")
                lbl_meta.pack(fill="x")

                lbl_monto = ctk.CTkLabel(item_row, text=f"S/. {p['monto']:,.2f}", font=ctk.CTkFont(weight="bold", size=13), text_color="#10b981")
                lbl_monto.pack(side="right", padx=12)

        # Actualizar Métodos de Pago
        for w in self.pagos_container.winfo_children():
            w.destroy()

        pagos = self.reporte_service.resumen_por_metodo_pago()
        if not pagos:
            lbl_vacio = ctk.CTkLabel(self.pagos_container, text="Sin transacciones aún.", text_color="#718096")
            lbl_vacio.pack(pady=20)
        else:
            for m in pagos:
                p_row = ctk.CTkFrame(self.pagos_container, fg_color=("#f8fafc", "#282e3d"), corner_radius=10)
                p_row.pack(fill="x", pady=5, ipady=6, padx=2)

                icono = "💵" if "EFECTIVO" in m["metodo"].upper() else ("💳" if "TARJETA" in m["metodo"].upper() else "🏦")
                lbl_icon = ctk.CTkLabel(p_row, text=icono, font=ctk.CTkFont(size=18), width=36)
                lbl_icon.pack(side="left", padx=6)

                detalles_frame = ctk.CTkFrame(p_row, fg_color="transparent")
                detalles_frame.pack(side="left", fill="both", expand=True)

                lbl_nom = ctk.CTkLabel(detalles_frame, text=m["metodo"].capitalize(), font=ctk.CTkFont(weight="bold", size=13), anchor="w")
                lbl_nom.pack(fill="x")

                lbl_cant = ctk.CTkLabel(detalles_frame, text=f"{m['cantidad']} transacciones", font=ctk.CTkFont(size=11), text_color="#718096", anchor="w")
                lbl_cant.pack(fill="x")

                lbl_monto = ctk.CTkLabel(p_row, text=f"S/. {m['monto']:,.2f}", font=ctk.CTkFont(weight="bold", size=13), text_color="#3b82f6")
                lbl_monto.pack(side="right", padx=12)
