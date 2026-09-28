import customtkinter as ctk
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sistema_ventas_python.services.reporte_service import ReporteService
from sistema_ventas_python.services.venta_service import VentaService
from sistema_ventas_python.models.models import Usuario, Venta, DetalleVenta
from sistema_ventas_python.views.ventas_view import ComprobanteModalDialog


class ReportesView(ctk.CTkFrame):
    """Módulo de reportes comerciales, historial de ventas y auditoría."""

    def __init__(self, master, usuario: Usuario, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.reporte_service = ReporteService()
        self.venta_service = VentaService()

        self._build_ui()
        self._filtrar("TODO")

    def _build_ui(self):
        # Barra superior
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 10))

        lbl_tit = ctk.CTkLabel(
            top_bar,
            text="📑 Reportes & Historial de Ventas",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        lbl_tit.pack(side="left")

        # Filtros rápidos por período
        period_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        period_frame.pack(fill="x", padx=20, pady=(0, 10), ipady=6)

        lbl_filtro = ctk.CTkLabel(period_frame, text="Período:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_filtro.pack(side="left", padx=(15, 8))

        self.btn_hoy = ctk.CTkButton(
            period_frame,
            text="Hoy",
            width=70,
            height=32,
            corner_radius=6,
            fg_color=("#edf2f7", "#2d3748"),
            text_color=("#2d3748", "#e2e8f0"),
            command=lambda: self._filtrar("HOY")
        )
        self.btn_hoy.pack(side="left", padx=4)

        self.btn_7dias = ctk.CTkButton(
            period_frame,
            text="Últimos 7 días",
            width=110,
            height=32,
            corner_radius=6,
            fg_color=("#edf2f7", "#2d3748"),
            text_color=("#2d3748", "#e2e8f0"),
            command=lambda: self._filtrar("7DIAS")
        )
        self.btn_7dias.pack(side="left", padx=4)

        self.btn_mes = ctk.CTkButton(
            period_frame,
            text="Mes Actual",
            width=100,
            height=32,
            corner_radius=6,
            fg_color=("#edf2f7", "#2d3748"),
            text_color=("#2d3748", "#e2e8f0"),
            command=lambda: self._filtrar("MES")
        )
        self.btn_mes.pack(side="left", padx=4)

        self.btn_todo = ctk.CTkButton(
            period_frame,
            text="Histórico Completo",
            width=130,
            height=32,
            corner_radius=6,
            fg_color="#2563eb",
            text_color="white",
            command=lambda: self._filtrar("TODO")
        )
        self.btn_todo.pack(side="left", padx=4)

        # Buscador por texto
        self.txt_buscar_cliente = ctk.CTkEntry(
            period_frame,
            placeholder_text="🔍 Filtrar por cliente o documento...",
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12)
        )
        self.txt_buscar_cliente.pack(side="right", fill="x", expand=True, padx=(20, 15))
        self.txt_buscar_cliente.bind("<KeyRelease>", lambda event: self._filtrar(self.filtro_actual))

        # Tarjetas de Resumen del Período
        self.cards_periodo = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_periodo.pack(fill="x", padx=20, pady=(0, 10))
        self.cards_periodo.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_total = self._crear_mini_kpi(self.cards_periodo, 0, "Facturación Período", "$0.00", "#10b981")
        self.card_cant = self._crear_mini_kpi(self.cards_periodo, 1, "Ventas Registradas", "0 órdenes", "#3b82f6")
        self.card_prom = self._crear_mini_kpi(self.cards_periodo, 2, "Ticket Promedio Período", "$0.00", "#8b5cf6")

        # Encabezado Tabla
        header_table = ctk.CTkFrame(self, height=36, corner_radius=8, fg_color=("#edf2f7", "#171923"))
        header_table.pack(fill="x", padx=20, pady=(0, 5))
        header_table.pack_propagate(False)

        col_configs = [
            ("CÓDIGO", 120),
            ("FECHA", 140),
            ("CLIENTE", 230),
            ("MÉTODO", 100),
            ("CAJERO", 130),
            ("TOTAL", 100),
            ("DETALLE", 80),
        ]

        for col_name, col_width in col_configs:
            lbl = ctk.CTkLabel(
                header_table,
                text=col_name,
                width=col_width,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#718096", "#a0aec0"),
                anchor="w" if col_name in ("CLIENTE", "CAJERO") else "center"
            )
            lbl.pack(side="left", padx=5)

        # Contenedor desplazable de filas
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _crear_mini_kpi(self, parent, col: int, titulo: str, valor: str, color: str):
        c = ctk.CTkFrame(parent, corner_radius=10, fg_color=("white", "#1e222d"), border_width=1, border_color=("#e2e8f0", "#2d3748"))
        c.grid(row=0, column=col, padx=4, sticky="nsew", ipady=4)
        lbl_t = ctk.CTkLabel(c, text=titulo, font=ctk.CTkFont(size=11), text_color="#718096")
        lbl_t.pack(pady=(6, 0))
        lbl_v = ctk.CTkLabel(c, text=valor, font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
        lbl_v.pack(pady=(0, 6))
        return lbl_v

    def _filtrar(self, tipo: str):
        self.filtro_actual = tipo
        hoy = date.today()

        fecha_ini = None
        fecha_fin = None

        # Resetear botones
        for b in (self.btn_hoy, self.btn_7dias, self.btn_mes, self.btn_todo):
            b.configure(fg_color=("#edf2f7", "#2d3748"), text_color=("#2d3748", "#e2e8f0"))

        if tipo == "HOY":
            fecha_ini = hoy.strftime("%Y-%m-%d")
            fecha_fin = hoy.strftime("%Y-%m-%d")
            self.btn_hoy.configure(fg_color="#2563eb", text_color="white")
        elif tipo == "7DIAS":
            fecha_ini = (hoy - timedelta(days=7)).strftime("%Y-%m-%d")
            fecha_fin = hoy.strftime("%Y-%m-%d")
            self.btn_7dias.configure(fg_color="#2563eb", text_color="white")
        elif tipo == "MES":
            fecha_ini = hoy.replace(day=1).strftime("%Y-%m-%d")
            fecha_fin = hoy.strftime("%Y-%m-%d")
            self.btn_mes.configure(fg_color="#2563eb", text_color="white")
        else:
            self.btn_todo.configure(fg_color="#2563eb", text_color="white")

        query_cl = self.txt_buscar_cliente.get().strip()
        ventas = self.reporte_service.filtrar_ventas(fecha_ini, fecha_fin, query_cl)

        # Actualizar mini KPIs
        tot_monto = sum(v["total"] for v in ventas)
        cant_v = len(ventas)
        prom = round(tot_monto / max(cant_v, 1), 2) if cant_v > 0 else 0.0

        self.card_total.configure(text=f"${tot_monto:,.2f}")
        self.card_cant.configure(text=f"{cant_v} órdenes")
        self.card_prom.configure(text=f"${prom:,.2f}")

        # Renderizar filas
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not ventas:
            lbl_v = ctk.CTkLabel(self.table_scroll, text="No hay ventas registradas para los filtros seleccionados.", text_color="#718096")
            lbl_v.pack(pady=40)
            return

        for v in ventas:
            row = ctk.CTkFrame(
                self.table_scroll,
                height=46,
                corner_radius=8,
                fg_color=("white", "#1e222d"),
                border_width=1,
                border_color=("#e2e8f0", "#2d3748")
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            # Código
            lbl_c = ctk.CTkLabel(row, text=v["codigo"], width=120, font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b82f6")
            lbl_c.pack(side="left", padx=5)

            # Fecha
            lbl_f = ctk.CTkLabel(row, text=v["fecha"][:16], width=140, font=ctk.CTkFont(size=11), text_color="#718096")
            lbl_f.pack(side="left", padx=5)

            # Cliente
            lbl_cl = ctk.CTkLabel(row, text=v["cliente"], width=230, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl_cl.pack(side="left", padx=5)

            # Método
            lbl_m = ctk.CTkLabel(row, text=v["metodo_pago"].capitalize(), width=100, font=ctk.CTkFont(size=11), text_color="#718096")
            lbl_m.pack(side="left", padx=5)

            # Vendedor
            lbl_u = ctk.CTkLabel(row, text=v["vendedor"], width=130, font=ctk.CTkFont(size=11), anchor="w")
            lbl_u.pack(side="left", padx=5)

            # Total
            lbl_tot = ctk.CTkLabel(row, text=f"${v['total']:,.2f}", width=100, font=ctk.CTkFont(size=13, weight="bold"), text_color="#10b981")
            lbl_tot.pack(side="left", padx=5)

            # Botón ver detalle
            btn_ver = ctk.CTkButton(
                row,
                text="👁️ Ver",
                width=65,
                height=28,
                corner_radius=6,
                fg_color=("#edf2f7", "#2d3748"),
                text_color=("#2d3748", "#e2e8f0"),
                hover_color=("#e2e8f0", "#4a5568"),
                font=ctk.CTkFont(size=11),
                command=lambda v_id=v["id"]: self._abrir_detalle_venta(v_id)
            )
            btn_ver.pack(side="left", padx=5)

    def _abrir_detalle_venta(self, venta_id: int):
        with self.venta_service.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.*, c.nombre_razon_social as cliente_nombre, c.numero_documento as cliente_doc,
                       u.nombre_completo as usuario_nombre
                FROM ventas v
                JOIN clientes c ON v.cliente_id = c.id
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = ?;
            """, (venta_id,))
            r = cursor.fetchone()
            if not r:
                return

            detalles = self.venta_service.obtener_detalle_venta(venta_id)
            venta_obj = Venta(
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
                fecha_venta=str(r["fecha_venta"]),
                detalles=detalles
            )

            ComprobanteModalDialog(self.winfo_toplevel(), venta_obj)
