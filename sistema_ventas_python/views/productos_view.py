import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List
from sistema_ventas_python.services.producto_service import ProductoService
from sistema_ventas_python.models.models import Producto, Usuario


class ProductoModalDialog(ctk.CTkToplevel):
    """Ventana modal moderna para registrar o editar un producto."""

    def __init__(self, master, producto: Optional[Producto] = None, on_save_callback=None):
        super().__init__(master)
        self.producto = producto
        self.on_save_callback = on_save_callback
        self.producto_service = ProductoService()

        es_edicion = producto is not None and producto.id is not None
        self.title("Editar Producto" if es_edicion else "Registrar Nuevo Producto")
        self.geometry("500x560")
        self.resizable(False, False)

        # Modal sobre la ventana padre
        self.transient(master)
        self.grab_set()

        self._build_ui(es_edicion)

    def _build_ui(self, es_edicion: bool):
        pad_frame = ctk.CTkFrame(self, fg_color="transparent")
        pad_frame.pack(fill="both", expand=True, padx=25, pady=20)

        titulo_text = "✏️ Editar Producto" if es_edicion else "📦 Nuevo Producto al Catálogo"
        lbl_titulo = ctk.CTkLabel(
            pad_frame,
            text=titulo_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        lbl_titulo.pack(fill="x", pady=(0, 15))

        # Formulario
        fields_frame = ctk.CTkFrame(pad_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True)

        # Código SKU
        ctk.CTkLabel(fields_frame, text="Código / SKU *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_codigo = ctk.CTkEntry(fields_frame, height=36, placeholder_text="ej: PROD-101")
        self.txt_codigo.pack(fill="x", pady=(2, 10))

        # Nombre
        ctk.CTkLabel(fields_frame, text="Nombre del Producto *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_nombre = ctk.CTkEntry(fields_frame, height=36, placeholder_text="ej: Laptop Lenovo...")
        self.txt_nombre.pack(fill="x", pady=(2, 10))

        # Categoría
        ctk.CTkLabel(fields_frame, text="Categoría", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.cmb_categoria = ctk.CTkComboBox(
            fields_frame,
            height=36,
            values=["Computación", "Accesorios", "Monitores", "Almacenamiento", "Componentes", "Audio", "Impresoras", "Redes", "Servicios", "General"]
        )
        self.cmb_categoria.pack(fill="x", pady=(2, 10))

        # 2 columnas para Precios
        precios_row = ctk.CTkFrame(fields_frame, fg_color="transparent")
        precios_row.pack(fill="x", pady=(0, 10))
        precios_row.grid_columnconfigure((0, 1), weight=1)

        f_costo = ctk.CTkFrame(precios_row, fg_color="transparent")
        f_costo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(f_costo, text="Precio Costo (S/.)", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_costo = ctk.CTkEntry(f_costo, height=36, placeholder_text="0.00")
        self.txt_costo.pack(fill="x", pady=(2, 0))

        f_venta = ctk.CTkFrame(precios_row, fg_color="transparent")
        f_venta.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(f_venta, text="Precio Venta (S/.) *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_venta = ctk.CTkEntry(f_venta, height=36, placeholder_text="0.00")
        self.txt_venta.pack(fill="x", pady=(2, 0))

        # 2 columnas para Stock
        stock_row = ctk.CTkFrame(fields_frame, fg_color="transparent")
        stock_row.pack(fill="x", pady=(0, 15))
        stock_row.grid_columnconfigure((0, 1), weight=1)

        f_actual = ctk.CTkFrame(stock_row, fg_color="transparent")
        f_actual.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(f_actual, text="Stock Actual (Unidades) *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_stock_actual = ctk.CTkEntry(f_actual, height=36, placeholder_text="0")
        self.txt_stock_actual.pack(fill="x", pady=(2, 0))

        f_minimo = ctk.CTkFrame(stock_row, fg_color="transparent")
        f_minimo.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(f_minimo, text="Stock Mínimo (Alerta) *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_stock_min = ctk.CTkEntry(f_minimo, height=36, placeholder_text="5")
        self.txt_stock_min.pack(fill="x", pady=(2, 0))

        # Llenar datos si es edición
        if es_edicion and self.producto:
            self.txt_codigo.insert(0, self.producto.codigo)
            self.txt_nombre.insert(0, self.producto.nombre)
            self.cmb_categoria.set(self.producto.categoria)
            self.txt_costo.insert(0, str(self.producto.precio_costo))
            self.txt_venta.insert(0, str(self.producto.precio_venta))
            self.txt_stock_actual.insert(0, str(self.producto.stock_actual))
            self.txt_stock_min.insert(0, str(self.producto.stock_minimo))

        # Botones de Acción
        actions_frame = ctk.CTkFrame(pad_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(10, 0))

        btn_cancelar = ctk.CTkButton(
            actions_frame,
            text="Cancelar",
            fg_color="#718096",
            hover_color="#4a5568",
            height=40,
            command=self.destroy
        )
        btn_cancelar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_guardar = ctk.CTkButton(
            actions_frame,
            text="Guardar Producto 💾",
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            height=40,
            command=self._guardar
        )
        btn_guardar.pack(side="right", fill="x", expand=True, padx=(8, 0))

    def _guardar(self):
        codigo = self.txt_codigo.get().strip()
        nombre = self.txt_nombre.get().strip()
        categoria = self.cmb_categoria.get().strip()

        try:
            costo = float(self.txt_costo.get() or "0")
            venta = float(self.txt_venta.get() or "0")
            stock_act = int(self.txt_stock_actual.get() or "0")
            stock_min = int(self.txt_stock_min.get() or "5")
        except ValueError:
            messagebox.showerror("Error de Validación", "Precios y cantidades deben ser números válidos.", parent=self)
            return

        prod_id = self.producto.id if self.producto else None
        prod = Producto(
            id=prod_id,
            codigo=codigo,
            nombre=nombre,
            categoria=categoria,
            precio_costo=costo,
            precio_venta=venta,
            stock_actual=stock_act,
            stock_minimo=stock_min,
            is_active=True
        )

        exito, msg, _ = self.producto_service.guardar(prod)
        if exito:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class ProductosView(ctk.CTkFrame):
    """Módulo completo de gestión de productos e inventario."""

    def __init__(self, master, usuario: Usuario, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.producto_service = ProductoService()
        self.solo_stock_bajo = False

        self._build_ui()
        self.cargar_productos()

    def _build_ui(self):
        # Barra superior con título y controles
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 10))

        lbl_tit = ctk.CTkLabel(
            top_bar,
            text="📦 Catálogo de Productos & Inventario",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        lbl_tit.pack(side="left")

        # Botón Nuevo Producto si no es CONSULTOR
        if self.usuario.rol != "CONSULTOR":
            btn_nuevo = ctk.CTkButton(
                top_bar,
                text="⚡ + Nuevo Producto",
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                command=self._abrir_modal_nuevo
            )
            btn_nuevo.pack(side="right")

        # Barra de Búsqueda y Filtros
        filter_bar = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        filter_bar.pack(fill="x", padx=20, pady=(0, 12), ipady=8)

        # Buscador dinámico
        self.txt_busqueda = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Buscar por nombre, código SKU o categoría...",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.txt_busqueda.pack(side="left", fill="x", expand=True, padx=(15, 10))
        self.txt_busqueda.bind("<KeyRelease>", lambda event: self._buscar_dinamico())

        # Botón filtro Stock Bajo
        self.btn_filtro_stock = ctk.CTkButton(
            filter_bar,
            text="⚠️ Ver Solo Stock Crítico",
            height=38,
            corner_radius=8,
            fg_color=("#edf2f7", "#2d3748"),
            text_color=("#2d3748", "#e2e8f0"),
            hover_color=("#e2e8f0", "#4a5568"),
            command=self._toggle_filtro_stock
        )
        self.btn_filtro_stock.pack(side="right", padx=(0, 15))

        # Encabezado de la Tabla
        header_table = ctk.CTkFrame(
            self,
            height=38,
            corner_radius=8,
            fg_color=("#edf2f7", "#171923")
        )
        header_table.pack(fill="x", padx=20, pady=(0, 5))
        header_table.pack_propagate(False)

        col_configs = [
            ("CÓDIGO", 110),
            ("PRODUCTO", 280),
            ("CATEGORÍA", 130),
            ("PRECIO VENTA (S/.)", 120),
            ("COSTO (S/.)", 100),
            ("STOCK ACTUAL", 110),
            ("ESTADO", 100),
            ("ACCIONES", 110 if self.usuario.rol != "CONSULTOR" else 60),
        ]

        for col_name, col_width in col_configs:
            lbl = ctk.CTkLabel(
                header_table,
                text=col_name,
                width=col_width,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#718096", "#a0aec0"),
                anchor="w" if col_name in ("PRODUCTO", "CATEGORÍA") else "center"
            )
            lbl.pack(side="left", padx=5)

        # Contenedor desplazable con las filas
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _buscar_dinamico(self):
        query = self.txt_busqueda.get().strip()
        if not query:
            self.cargar_productos()
        else:
            prods = self.producto_service.buscar(query)
            if self.solo_stock_bajo:
                prods = [p for p in prods if p.es_stock_bajo]
            self._render_filas(prods)

    def _toggle_filtro_stock(self):
        self.solo_stock_bajo = not self.solo_stock_bajo
        if self.solo_stock_bajo:
            self.btn_filtro_stock.configure(
                text="✅ Mostrando Solo Stock Crítico",
                fg_color="#ef4444",
                text_color="white",
                hover_color="#dc2626"
            )
        else:
            self.btn_filtro_stock.configure(
                text="⚠️ Ver Solo Stock Crítico",
                fg_color=("#edf2f7", "#2d3748"),
                text_color=("#2d3748", "#e2e8f0"),
                hover_color=("#e2e8f0", "#4a5568")
            )
        self._buscar_dinamico()

    def cargar_productos(self):
        prods = self.producto_service.listar_todos(solo_activos=True)
        if self.solo_stock_bajo:
            prods = [p for p in prods if p.es_stock_bajo]
        self._render_filas(prods)

    def _render_filas(self, productos: List[Producto]):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not productos:
            lbl_vacio = ctk.CTkLabel(
                self.table_scroll,
                text="No se encontraron productos que coincidan con la búsqueda.",
                font=ctk.CTkFont(size=13),
                text_color="#718096"
            )
            lbl_vacio.pack(pady=40)
            return

        for p in productos:
            row_frame = ctk.CTkFrame(
                self.table_scroll,
                height=48,
                corner_radius=8,
                fg_color=("white", "#1e222d"),
                border_width=1,
                border_color=("#e2e8f0", "#2d3748")
            )
            row_frame.pack(fill="x", pady=3)
            row_frame.pack_propagate(False)

            # Código SKU
            lbl_cod = ctk.CTkLabel(
                row_frame,
                text=p.codigo,
                width=110,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#3b82f6"
            )
            lbl_cod.pack(side="left", padx=5)

            # Nombre
            lbl_nom = ctk.CTkLabel(
                row_frame,
                text=p.nombre,
                width=280,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            lbl_nom.pack(side="left", padx=5)

            # Categoría
            lbl_cat = ctk.CTkLabel(
                row_frame,
                text=p.categoria,
                width=130,
                font=ctk.CTkFont(size=12),
                text_color="#718096",
                anchor="w"
            )
            lbl_cat.pack(side="left", padx=5)

            # Precio Venta
            lbl_venta = ctk.CTkLabel(
                row_frame,
                text=f"S/. {p.precio_venta:,.2f}",
                width=120,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#10b981"
            )
            lbl_venta.pack(side="left", padx=5)

            # Costo
            lbl_costo = ctk.CTkLabel(
                row_frame,
                text=f"S/. {p.precio_costo:,.2f}",
                width=100,
                font=ctk.CTkFont(size=11),
                text_color="#718096"
            )
            lbl_costo.pack(side="left", padx=5)

            # Stock Actual
            color_stock = "#ef4444" if p.es_stock_bajo else ("#f59e0b" if p.stock_actual <= p.stock_minimo * 1.5 else "#10b981")
            lbl_stock = ctk.CTkLabel(
                row_frame,
                text=f"{p.stock_actual} uds (mín {p.stock_minimo})",
                width=110,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color_stock
            )
            lbl_stock.pack(side="left", padx=5)

            # Badge Estado
            estado_texto = "Crítico ⚠️" if p.es_stock_bajo else "Óptimo ✅"
            badge_color = "#fef2f2" if p.es_stock_bajo else "#f0fdf4"
            badge_text_col = "#dc2626" if p.es_stock_bajo else "#16a34a"
            lbl_estado = ctk.CTkLabel(
                row_frame,
                text=estado_texto,
                width=100,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=badge_color,
                text_color=badge_text_col,
                corner_radius=6
            )
            lbl_estado.pack(side="left", padx=5)

            # Botones de Acción (solo para usuarios con permisos)
            if self.usuario.rol != "CONSULTOR":
                btn_edit = ctk.CTkButton(
                    row_frame,
                    text="✏️",
                    width=32,
                    height=30,
                    corner_radius=6,
                    fg_color=("#e2e8f0", "#2d3748"),
                    hover_color=("#cbd5e0", "#4a5568"),
                    command=lambda prod=p: self._abrir_modal_editar(prod)
                )
                btn_edit.pack(side="left", padx=3)

                btn_del = ctk.CTkButton(
                    row_frame,
                    text="🗑️",
                    width=32,
                    height=30,
                    corner_radius=6,
                    fg_color="#fee2e2",
                    hover_color="#fca5a5",
                    text_color="#dc2626",
                    command=lambda prod_id=p.id: self._eliminar_producto(prod_id)
                )
                btn_del.pack(side="left", padx=3)

    def _abrir_modal_nuevo(self):
        ProductoModalDialog(self.winfo_toplevel(), on_save_callback=self.cargar_productos)

    def _abrir_modal_editar(self, producto: Producto):
        ProductoModalDialog(self.winfo_toplevel(), producto=producto, on_save_callback=self.cargar_productos)

    def _eliminar_producto(self, producto_id: int):
        resp = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar o archivar este producto?",
            parent=self.winfo_toplevel()
        )
        if resp:
            exito, msg = self.producto_service.eliminar(producto_id)
            if exito:
                messagebox.showinfo("Éxito", msg, parent=self.winfo_toplevel())
                self.cargar_productos()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())
