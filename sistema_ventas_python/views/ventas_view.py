import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional, Dict
from sistema_ventas_python.services.venta_service import VentaService
from sistema_ventas_python.services.producto_service import ProductoService
from sistema_ventas_python.services.cliente_service import ClienteService
from sistema_ventas_python.models.models import Producto, Cliente, ItemCarrito, Venta, Usuario


class ComprobanteModalDialog(ctk.CTkToplevel):
    """Comprobante digital / Ticket de venta moderno."""

    def __init__(self, master, venta: Venta):
        super().__init__(master)
        self.venta = venta
        self.title(f"Comprobante Electrónico — {venta.codigo_venta}")
        self.geometry("450x620")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=("white", "#1e222d"),
            corner_radius=16,
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado Ticket
        lbl_emblem = ctk.CTkLabel(container, text="💎", font=ctk.CTkFont(size=32))
        lbl_emblem.pack(pady=(15, 0))

        lbl_empresa = ctk.CTkLabel(container, text="SISTEMA DE VENTAS PRO", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_empresa.pack()

        lbl_ruc = ctk.CTkLabel(container, text="RUC: 20601892341 • COMPROBANTE DE PAGO", font=ctk.CTkFont(size=10), text_color="#718096")
        lbl_ruc.pack(pady=(0, 10))

        # Divisor
        div1 = ctk.CTkFrame(container, height=1, fg_color=("#e2e8f0", "#2d3748"))
        div1.pack(fill="x", padx=15, pady=5)

        # Info Venta
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=5)

        self._add_info_row(info_frame, "Código Venta:", self.venta.codigo_venta, es_bold=True)
        self._add_info_row(info_frame, "Fecha y Hora:", str(self.venta.fecha_venta))
        self._add_info_row(info_frame, "Cliente:", self.venta.cliente_nombre)
        self._add_info_row(info_frame, "Documento:", self.venta.cliente_documento)
        self._add_info_row(info_frame, "Cajero/Vendedor:", self.venta.usuario_nombre)
        self._add_info_row(info_frame, "Método de Pago:", self.venta.metodo_pago)

        # Divisor
        div2 = ctk.CTkFrame(container, height=1, fg_color=("#e2e8f0", "#2d3748"))
        div2.pack(fill="x", padx=15, pady=8)

        # Items
        items_scroll = ctk.CTkScrollableFrame(container, height=140, fg_color="transparent")
        items_scroll.pack(fill="both", expand=True, padx=15)

        for det in self.venta.detalles:
            i_row = ctk.CTkFrame(items_scroll, fg_color="transparent")
            i_row.pack(fill="x", pady=2)

            lbl_desc = ctk.CTkLabel(i_row, text=f"{det.cantidad}x {det.producto_nombre}", font=ctk.CTkFont(size=11), anchor="w")
            lbl_desc.pack(side="left", fill="x", expand=True)

            lbl_sub = ctk.CTkLabel(i_row, text=f"${det.subtotal:,.2f}", font=ctk.CTkFont(size=11, weight="bold"))
            lbl_sub.pack(side="right")

        # Divisor
        div3 = ctk.CTkFrame(container, height=1, fg_color=("#e2e8f0", "#2d3748"))
        div3.pack(fill="x", padx=15, pady=8)

        # Totales
        tot_frame = ctk.CTkFrame(container, fg_color="transparent")
        tot_frame.pack(fill="x", padx=20, pady=5)

        self._add_info_row(tot_frame, "Subtotal:", f"${self.venta.subtotal:,.2f}")
        if self.venta.descuento > 0:
            self._add_info_row(tot_frame, "Descuento:", f"-${self.venta.descuento:,.2f}")
        self._add_info_row(tot_frame, "Impuesto (18%):", f"${self.venta.impuesto:,.2f}")

        row_total = ctk.CTkFrame(tot_frame, fg_color="transparent")
        row_total.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(row_total, text="TOTAL:", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        ctk.CTkLabel(row_total, text=f"${self.venta.total:,.2f}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#10b981").pack(side="right")

        # Botón Cerrar
        btn_cerrar = ctk.CTkButton(
            container,
            text="Aceptar y Nueva Venta ➔",
            height=42,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        btn_cerrar.pack(fill="x", padx=20, pady=(15, 10))

    def _add_info_row(self, parent, label: str, val: str, es_bold: bool = False):
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", pady=1)
        ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=11), text_color="#718096").pack(side="left")
        ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=11, weight="bold" if es_bold else "normal")).pack(side="right")


class VentasView(ctk.CTkFrame):
    """Punto de Venta (POS) con Carrito de Compras interactivo y cálculo en vivo."""

    def __init__(self, master, usuario: Usuario, on_sale_completed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.on_sale_completed = on_sale_completed
        self.venta_service = VentaService()
        self.producto_service = ProductoService()
        self.cliente_service = ClienteService()

        self.carrito: Dict[int, ItemCarrito] = {}  # producto_id -> ItemCarrito
        self.clientes_cache: List[Cliente] = []
        self.productos_cache: List[Producto] = []

        self._build_ui()
        self.refrescar_datos()

    def _build_ui(self):
        # 2 Columnas: Izquierda (Catálogo) / Derecha (Carrito y Pago)
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO: CATÁLOGO =================
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(15, 8), pady=15)

        # Header catálogo
        lbl_cat_tit = ctk.CTkLabel(
            left_panel,
            text="📦 Catálogo de Productos Disponibles",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            anchor="w"
        )
        lbl_cat_tit.pack(fill="x", pady=(0, 10))

        # Buscador de productos
        search_box = ctk.CTkFrame(
            left_panel,
            corner_radius=10,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        search_box.pack(fill="x", pady=(0, 10), ipady=4)

        self.txt_buscar_prod = ctk.CTkEntry(
            search_box,
            placeholder_text="🔍 Buscar producto por nombre o SKU...",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.txt_buscar_prod.pack(fill="x", padx=10, pady=5)
        self.txt_buscar_prod.bind("<KeyRelease>", lambda event: self._filtrar_catalogo())

        # Lista de productos desplazable
        self.scroll_catalogo = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.scroll_catalogo.pack(fill="both", expand=True)

        # ================= PANEL DERECHO: CARRITO =================
        right_panel = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 15), pady=15)

        pad_right = ctk.CTkFrame(right_panel, fg_color="transparent")
        pad_right.pack(fill="both", expand=True, padx=16, pady=16)

        # Header Carrito
        cart_header = ctk.CTkFrame(pad_right, fg_color="transparent")
        cart_header.pack(fill="x", pady=(0, 10))

        lbl_cart_tit = ctk.CTkLabel(
            cart_header,
            text="🛒 Carrito de Compras",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        lbl_cart_tit.pack(side="left")

        btn_vaciar = ctk.CTkButton(
            cart_header,
            text="Vaciar",
            width=70,
            height=28,
            corner_radius=6,
            fg_color="#fee2e2",
            hover_color="#fca5a5",
            text_color="#dc2626",
            font=ctk.CTkFont(size=11),
            command=self._vaciar_carrito
        )
        btn_vaciar.pack(side="right")

        # Selector de Cliente
        client_box = ctk.CTkFrame(pad_right, fg_color=("#f8fafc", "#282e3d"), corner_radius=10)
        client_box.pack(fill="x", pady=(0, 10), ipady=6, padx=2)

        lbl_cl = ctk.CTkLabel(
            client_box,
            text="Cliente *",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#718096",
            anchor="w"
        )
        lbl_cl.pack(fill="x", padx=10, pady=(4, 2))

        self.cmb_clientes = ctk.CTkComboBox(
            client_box,
            height=34,
            corner_radius=8,
            values=["Cargando clientes..."]
        )
        self.cmb_clientes.pack(fill="x", padx=10, pady=(0, 6))

        # Lista de Items en Carrito
        self.scroll_carrito = ctk.CTkScrollableFrame(
            pad_right,
            height=180,
            fg_color=("#f8fafc", "#171923"),
            corner_radius=10
        )
        self.scroll_carrito.pack(fill="both", expand=True, pady=(0, 10))

        # Caja de Totales & Opciones de Pago
        summary_box = ctk.CTkFrame(pad_right, fg_color=("#f8fafc", "#282e3d"), corner_radius=12)
        summary_box.pack(fill="x", pady=(0, 10), ipady=6, padx=2)

        # Fila Método de pago & Descuento
        row_inputs = ctk.CTkFrame(summary_box, fg_color="transparent")
        row_inputs.pack(fill="x", padx=12, pady=(6, 4))
        row_inputs.grid_columnconfigure((0, 1), weight=1)

        f_pago = ctk.CTkFrame(row_inputs, fg_color="transparent")
        f_pago.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(f_pago, text="Método de Pago", font=ctk.CTkFont(size=11, weight="bold"), text_color="#718096", anchor="w").pack(fill="x")
        self.cmb_metodo = ctk.CTkComboBox(
            f_pago,
            height=32,
            values=["EFECTIVO", "TARJETA", "TRANSFERENCIA"]
        )
        self.cmb_metodo.pack(fill="x", pady=(2, 0))

        f_desc = ctk.CTkFrame(row_inputs, fg_color="transparent")
        f_desc.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(f_desc, text="Descuento ($)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#718096", anchor="w").pack(fill="x")
        self.txt_descuento = ctk.CTkEntry(f_desc, height=32, placeholder_text="0.00")
        self.txt_descuento.insert(0, "0.00")
        self.txt_descuento.pack(fill="x", pady=(2, 0))
        self.txt_descuento.bind("<KeyRelease>", lambda event: self._actualizar_vista_totales())

        # Desglose numérico
        desglose = ctk.CTkFrame(summary_box, fg_color="transparent")
        desglose.pack(fill="x", padx=12, pady=(4, 6))

        r_sub = ctk.CTkFrame(desglose, fg_color="transparent")
        r_sub.pack(fill="x", pady=1)
        ctk.CTkLabel(r_sub, text="Subtotal:", font=ctk.CTkFont(size=12), text_color="#718096").pack(side="left")
        self.lbl_subtotal_val = ctk.CTkLabel(r_sub, text="$0.00", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_subtotal_val.pack(side="right")

        r_imp = ctk.CTkFrame(desglose, fg_color="transparent")
        r_imp.pack(fill="x", pady=1)
        ctk.CTkLabel(r_imp, text="Impuesto (18%):", font=ctk.CTkFont(size=12), text_color="#718096").pack(side="left")
        self.lbl_impuesto_val = ctk.CTkLabel(r_imp, text="$0.00", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_impuesto_val.pack(side="right")

        # TOTAL GRANDE
        r_tot = ctk.CTkFrame(desglose, fg_color="transparent")
        r_tot.pack(fill="x", pady=(6, 2))
        ctk.CTkLabel(r_tot, text="TOTAL A PAGAR:", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.lbl_total_val = ctk.CTkLabel(r_tot, text="$0.00", font=ctk.CTkFont(size=22, weight="bold"), text_color="#10b981")
        self.lbl_total_val.pack(side="right")

        # Botón grande COMPLETAR VENTA
        es_consultor = self.usuario.rol == "CONSULTOR"
        btn_text = "🔒 Modo Consulta (Solo Lectura)" if es_consultor else "💰 COMPLETAR VENTA (F5) ➔"
        btn_state = "disabled" if es_consultor else "normal"

        self.btn_completar = ctk.CTkButton(
            pad_right,
            text=btn_text,
            height=46,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#059669" if not es_consultor else "#718096",
            hover_color="#047857" if not es_consultor else "#718096",
            state=btn_state,
            command=self._completar_venta
        )
        self.btn_completar.pack(fill="x")

    def refrescar_datos(self):
        """Carga clientes y productos desde la base de datos."""
        self.clientes_cache = self.cliente_service.listar_todos()
        self.productos_cache = self.producto_service.listar_todos()

        # Actualizar combobox clientes
        if self.clientes_cache:
            nombres = [f"{c.numero_documento} - {c.nombre_razon_social}" for c in self.clientes_cache]
            self.cmb_clientes.configure(values=nombres)
            self.cmb_clientes.set(nombres[0])
        else:
            self.cmb_clientes.configure(values=["Sin clientes registrados"])

        self._filtrar_catalogo()

    def _filtrar_catalogo(self):
        query = self.txt_buscar_prod.get().strip().lower()

        for w in self.scroll_catalogo.winfo_children():
            w.destroy()

        productos_filtrados = [
            p for p in self.productos_cache
            if not query or query in p.nombre.lower() or query in p.codigo.lower() or query in p.categoria.lower()
        ]

        if not productos_filtrados:
            lbl_vacio = ctk.CTkLabel(self.scroll_catalogo, text="No hay productos disponibles.", text_color="#718096")
            lbl_vacio.pack(pady=30)
            return

        for p in productos_filtrados:
            card = ctk.CTkFrame(
                self.scroll_catalogo,
                corner_radius=10,
                fg_color=("white", "#1e222d"),
                border_width=1,
                border_color=("#e2e8f0", "#2d3748")
            )
            card.pack(fill="x", pady=4, ipady=6, padx=2)

            # Info izquierda
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=12)

            lbl_tit = ctk.CTkLabel(info, text=p.nombre, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            lbl_tit.pack(fill="x")

            stock_text = f"Stock: {p.stock_actual} uds"
            stock_color = "#ef4444" if p.stock_actual <= p.stock_minimo else "#718096"
            lbl_sub = ctk.CTkLabel(info, text=f"{p.codigo} • {p.categoria} • {stock_text}", font=ctk.CTkFont(size=11), text_color=stock_color, anchor="w")
            lbl_sub.pack(fill="x")

            # Precio y botón agregar a la derecha
            right_sub = ctk.CTkFrame(card, fg_color="transparent")
            right_sub.pack(side="right", padx=12)

            lbl_precio = ctk.CTkLabel(right_sub, text=f"${p.precio_venta:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981")
            lbl_precio.pack(side="left", padx=(0, 10))

            btn_add = ctk.CTkButton(
                right_sub,
                text="+ Añadir",
                width=75,
                height=32,
                corner_radius=8,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                font=ctk.CTkFont(size=12, weight="bold"),
                state="disabled" if p.stock_actual <= 0 or self.usuario.rol == "CONSULTOR" else "normal",
                command=lambda prod=p: self._agregar_al_carrito(prod)
            )
            btn_add.pack(side="right")

    def _agregar_al_carrito(self, producto: Producto):
        if producto.stock_actual <= 0:
            messagebox.showwarning("Sin Stock", f"El producto '{producto.nombre}' no tiene stock disponible.", parent=self.winfo_toplevel())
            return

        if producto.id in self.carrito:
            item = self.carrito[producto.id]
            if item.cantidad + 1 > producto.stock_actual:
                messagebox.showwarning("Límite de Stock", f"No puedes agregar más unidades. Stock disponible: {producto.stock_actual}", parent=self.winfo_toplevel())
                return
            item.cantidad += 1
        else:
            self.carrito[producto.id] = ItemCarrito(
                producto=producto,
                cantidad=1,
                precio_unitario=producto.precio_venta
            )

        self._render_carrito()

    def _cambiar_cantidad(self, producto_id: int, delta: int):
        if producto_id in self.carrito:
            item = self.carrito[producto_id]
            nueva_cant = item.cantidad + delta
            if nueva_cant <= 0:
                del self.carrito[producto_id]
            elif nueva_cant > item.producto.stock_actual:
                messagebox.showwarning("Límite de Stock", f"Stock máximo alcanzado ({item.producto.stock_actual} uds).", parent=self.winfo_toplevel())
                return
            else:
                item.cantidad = nueva_cant
            self._render_carrito()

    def _eliminar_item(self, producto_id: int):
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self._render_carrito()

    def _vaciar_carrito(self):
        if self.carrito:
            self.carrito.clear()
            self._render_carrito()

    def _render_carrito(self):
        for w in self.scroll_carrito.winfo_children():
            w.destroy()

        if not self.carrito:
            lbl_vacio = ctk.CTkLabel(
                self.scroll_carrito,
                text="El carrito está vacío.\nAñade productos desde el catálogo.",
                font=ctk.CTkFont(size=12),
                text_color="#718096"
            )
            lbl_vacio.pack(pady=40)
        else:
            for p_id, item in list(self.carrito.items()):
                row = ctk.CTkFrame(self.scroll_carrito, fg_color=("white", "#1e222d"), corner_radius=8)
                row.pack(fill="x", pady=2, padx=2, ipady=4)

                # Info
                lbl_desc = ctk.CTkLabel(
                    row,
                    text=item.producto.nombre,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=150,
                    anchor="w"
                )
                lbl_desc.pack(side="left", padx=8)

                # Control Cantidad [-] [Qty] [+]
                qty_box = ctk.CTkFrame(row, fg_color="transparent")
                qty_box.pack(side="left", padx=4)

                btn_minus = ctk.CTkButton(
                    qty_box,
                    text="-",
                    width=26,
                    height=24,
                    corner_radius=4,
                    fg_color=("#e2e8f0", "#2d3748"),
                    hover_color=("#cbd5e0", "#4a5568"),
                    command=lambda pid=p_id: self._cambiar_cantidad(pid, -1)
                )
                btn_minus.pack(side="left")

                lbl_cant = ctk.CTkLabel(
                    qty_box,
                    text=str(item.cantidad),
                    width=30,
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                lbl_cant.pack(side="left")

                btn_plus = ctk.CTkButton(
                    qty_box,
                    text="+",
                    width=26,
                    height=24,
                    corner_radius=4,
                    fg_color=("#e2e8f0", "#2d3748"),
                    hover_color=("#cbd5e0", "#4a5568"),
                    command=lambda pid=p_id: self._cambiar_cantidad(pid, 1)
                )
                btn_plus.pack(side="left")

                # Subtotal
                lbl_sub = ctk.CTkLabel(
                    row,
                    text=f"${item.subtotal:,.2f}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#10b981",
                    width=65,
                    anchor="e"
                )
                lbl_sub.pack(side="left", padx=4)

                # Quitar
                btn_del = ctk.CTkButton(
                    row,
                    text="❌",
                    width=24,
                    height=24,
                    corner_radius=4,
                    fg_color="transparent",
                    hover_color="#fee2e2",
                    text_color="#dc2626",
                    command=lambda pid=p_id: self._eliminar_item(pid)
                )
                btn_del.pack(side="right", padx=6)

        self._actualizar_vista_totales()

    def _actualizar_vista_totales(self):
        try:
            desc_val = float(self.txt_descuento.get() or "0")
        except ValueError:
            desc_val = 0.0

        items_list = list(self.carrito.values())
        totales = self.venta_service.calcular_totales(items_list, descuento=desc_val)

        self.lbl_subtotal_val.configure(text=f"${totales['subtotal']:,.2f}")
        self.lbl_impuesto_val.configure(text=f"${totales['impuesto']:,.2f}")
        self.lbl_total_val.configure(text=f"${totales['total']:,.2f}")

    def _completar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "Por favor agregue al menos un producto al carrito.", parent=self.winfo_toplevel())
            return

        # Obtener cliente seleccionado
        combo_val = self.cmb_clientes.get()
        cliente_id = None
        for c in self.clientes_cache:
            if combo_val.startswith(c.numero_documento):
                cliente_id = c.id
                break

        if not cliente_id:
            messagebox.showerror("Error", "Debe seleccionar un cliente registrado.", parent=self.winfo_toplevel())
            return

        metodo = self.cmb_metodo.get()
        try:
            descuento = float(self.txt_descuento.get() or "0")
        except ValueError:
            descuento = 0.0

        items_list = list(self.carrito.values())

        exito, msg, venta = self.venta_service.procesar_venta(
            cliente_id=cliente_id,
            usuario_id=self.usuario.id or 1,
            items=items_list,
            metodo_pago=metodo,
            descuento=descuento,
            notas=f"Venta generada en POS por {self.usuario.nombre_completo}"
        )

        if exito and venta:
            # Vaciar carrito y actualizar catálogo
            self.carrito.clear()
            self._render_carrito()
            self.refrescar_datos()

            if self.on_sale_completed:
                self.on_sale_completed()

            # Mostrar Comprobante digital moderno
            ComprobanteModalDialog(self.winfo_toplevel(), venta)
        else:
            messagebox.showerror("Error en Venta", msg, parent=self.winfo_toplevel())
