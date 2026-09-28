import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List
from sistema_ventas_python.services.cliente_service import ClienteService
from sistema_ventas_python.models.models import Cliente, Usuario


class ClienteModalDialog(ctk.CTkToplevel):
    """Modal para registrar o actualizar datos de un cliente."""

    def __init__(self, master, cliente: Optional[Cliente] = None, on_save_callback=None):
        super().__init__(master)
        self.cliente = cliente
        self.on_save_callback = on_save_callback
        self.cliente_service = ClienteService()

        es_edicion = cliente is not None and cliente.id is not None
        self.title("Editar Cliente" if es_edicion else "Registrar Nuevo Cliente")
        self.geometry("480x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._build_ui(es_edicion)

    def _build_ui(self, es_edicion: bool):
        pad_frame = ctk.CTkFrame(self, fg_color="transparent")
        pad_frame.pack(fill="both", expand=True, padx=25, pady=20)

        titulo_text = "✏️ Modificar Cliente" if es_edicion else "👥 Registrar Nuevo Cliente"
        lbl_titulo = ctk.CTkLabel(
            pad_frame,
            text=titulo_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        lbl_titulo.pack(fill="x", pady=(0, 15))

        # 2 columnas para Tipo de Doc y Número
        doc_row = ctk.CTkFrame(pad_frame, fg_color="transparent")
        doc_row.pack(fill="x", pady=(0, 10))
        doc_row.grid_columnconfigure(0, weight=2)
        doc_row.grid_columnconfigure(1, weight=5)

        f_tipo = ctk.CTkFrame(doc_row, fg_color="transparent")
        f_tipo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(f_tipo, text="Tipo Doc *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.cmb_tipo_doc = ctk.CTkComboBox(f_tipo, height=36, values=["DNI", "RUC", "PASAPORTE", "CE"])
        self.cmb_tipo_doc.pack(fill="x", pady=(2, 0))

        f_num = ctk.CTkFrame(doc_row, fg_color="transparent")
        f_num.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(f_num, text="N° Documento *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_documento = ctk.CTkEntry(f_num, height=36, placeholder_text="ej: 45891234")
        self.txt_documento.pack(fill="x", pady=(2, 0))

        # Nombre / Razón Social
        ctk.CTkLabel(pad_frame, text="Nombre Completo / Razón Social *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_nombre = ctk.CTkEntry(pad_frame, height=36, placeholder_text="ej: Juan Pérez o Empresa S.A.")
        self.txt_nombre.pack(fill="x", pady=(2, 10))

        # Teléfono
        ctk.CTkLabel(pad_frame, text="Teléfono / Celular", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_telefono = ctk.CTkEntry(pad_frame, height=36, placeholder_text="ej: +51 987654321")
        self.txt_telefono.pack(fill="x", pady=(2, 10))

        # Email
        ctk.CTkLabel(pad_frame, text="Correo Electrónico", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_email = ctk.CTkEntry(pad_frame, height=36, placeholder_text="ej: cliente@email.com")
        self.txt_email.pack(fill="x", pady=(2, 10))

        # Dirección
        ctk.CTkLabel(pad_frame, text="Dirección Fiscal o Domicilio", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x")
        self.txt_direccion = ctk.CTkEntry(pad_frame, height=36, placeholder_text="ej: Av. Los Álamos 123")
        self.txt_direccion.pack(fill="x", pady=(2, 15))

        # Rellenar datos si es edición
        if es_edicion and self.cliente:
            self.cmb_tipo_doc.set(self.cliente.tipo_documento)
            self.txt_documento.insert(0, self.cliente.numero_documento)
            self.txt_nombre.insert(0, self.cliente.nombre_razon_social)
            if self.cliente.telefono:
                self.txt_telefono.insert(0, self.cliente.telefono)
            if self.cliente.email:
                self.txt_email.insert(0, self.cliente.email)
            if self.cliente.direccion:
                self.txt_direccion.insert(0, self.cliente.direccion)

        # Botones
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
            text="Guardar Cliente 💾",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(weight="bold"),
            height=40,
            command=self._guardar
        )
        btn_guardar.pack(side="right", fill="x", expand=True, padx=(8, 0))

    def _guardar(self):
        tipo_doc = self.cmb_tipo_doc.get().strip()
        num_doc = self.txt_documento.get().strip()
        nombre = self.txt_nombre.get().strip()
        tel = self.txt_telefono.get().strip() or None
        mail = self.txt_email.get().strip() or None
        dir_val = self.txt_direccion.get().strip() or None

        cl_id = self.cliente.id if self.cliente else None
        cl = Cliente(
            id=cl_id,
            tipo_documento=tipo_doc,
            numero_documento=num_doc,
            nombre_razon_social=nombre,
            email=mail,
            telefono=tel,
            direccion=dir_val,
            is_active=True
        )

        exito, msg, _ = self.cliente_service.guardar(cl)
        if exito:
            messagebox.showinfo("Éxito", msg, parent=self)
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class ClientesView(ctk.CTkFrame):
    """Módulo completo para administración de cartera de clientes."""

    def __init__(self, master, usuario: Usuario, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.cliente_service = ClienteService()

        self._build_ui()
        self.cargar_clientes()

    def _build_ui(self):
        # Barra superior con título y botón de alta
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(15, 10))

        lbl_tit = ctk.CTkLabel(
            top_bar,
            text="👥 Cartera de Clientes",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        lbl_tit.pack(side="left")

        if self.usuario.rol != "CONSULTOR":
            btn_nuevo = ctk.CTkButton(
                top_bar,
                text="⚡ + Registrar Cliente",
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                command=self._abrir_modal_nuevo
            )
            btn_nuevo.pack(side="right")

        # Barra de búsqueda
        search_bar = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("white", "#1e222d"),
            border_width=1,
            border_color=("#e2e8f0", "#2d3748")
        )
        search_bar.pack(fill="x", padx=20, pady=(0, 12), ipady=8)

        self.txt_busqueda = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍 Buscar por nombre, número de documento (DNI/RUC) o email...",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.txt_busqueda.pack(fill="x", padx=15)
        self.txt_busqueda.bind("<KeyRelease>", lambda event: self._buscar_dinamico())

        # Cabecera tabla
        header_table = ctk.CTkFrame(self, height=38, corner_radius=8, fg_color=("#edf2f7", "#171923"))
        header_table.pack(fill="x", padx=20, pady=(0, 5))
        header_table.pack_propagate(False)

        col_configs = [
            ("DOCUMENTO", 140),
            ("NOMBRE / RAZÓN SOCIAL", 260),
            ("TELÉFONO", 130),
            ("EMAIL", 180),
            ("DIRECCIÓN", 190),
            ("ACCIONES", 100 if self.usuario.rol != "CONSULTOR" else 50),
        ]

        for col_name, col_width in col_configs:
            lbl = ctk.CTkLabel(
                header_table,
                text=col_name,
                width=col_width,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#718096", "#a0aec0"),
                anchor="w" if col_name != "ACCIONES" else "center"
            )
            lbl.pack(side="left", padx=5)

        # Contenedor desplazable de filas
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _buscar_dinamico(self):
        query = self.txt_busqueda.get().strip()
        if not query:
            self.cargar_clientes()
        else:
            clientes = self.cliente_service.buscar(query)
            self._render_filas(clientes)

    def cargar_clientes(self):
        clientes = self.cliente_service.listar_todos()
        self._render_filas(clientes)

    def _render_filas(self, clientes: List[Cliente]):
        for w in self.table_scroll.winfo_children():
            w.destroy()

        if not clientes:
            lbl_vacio = ctk.CTkLabel(
                self.table_scroll,
                text="No se encontraron clientes registrados.",
                font=ctk.CTkFont(size=13),
                text_color="#718096"
            )
            lbl_vacio.pack(pady=40)
            return

        for c in clientes:
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

            # Documento
            lbl_doc = ctk.CTkLabel(
                row_frame,
                text=f"{c.tipo_documento}: {c.numero_documento}",
                width=140,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#3b82f6",
                anchor="w"
            )
            lbl_doc.pack(side="left", padx=5)

            # Nombre
            lbl_nom = ctk.CTkLabel(
                row_frame,
                text=c.nombre_razon_social,
                width=260,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            lbl_nom.pack(side="left", padx=5)

            # Teléfono
            lbl_tel = ctk.CTkLabel(
                row_frame,
                text=c.telefono or "—",
                width=130,
                font=ctk.CTkFont(size=11),
                text_color="#718096",
                anchor="w"
            )
            lbl_tel.pack(side="left", padx=5)

            # Email
            lbl_mail = ctk.CTkLabel(
                row_frame,
                text=c.email or "—",
                width=180,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            lbl_mail.pack(side="left", padx=5)

            # Dirección
            lbl_dir = ctk.CTkLabel(
                row_frame,
                text=c.direccion or "—",
                width=190,
                font=ctk.CTkFont(size=11),
                text_color="#718096",
                anchor="w"
            )
            lbl_dir.pack(side="left", padx=5)

            # Acciones
            if self.usuario.rol != "CONSULTOR":
                btn_edit = ctk.CTkButton(
                    row_frame,
                    text="✏️",
                    width=32,
                    height=30,
                    corner_radius=6,
                    fg_color=("#e2e8f0", "#2d3748"),
                    hover_color=("#cbd5e0", "#4a5568"),
                    command=lambda cl=c: self._abrir_modal_editar(cl)
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
                    command=lambda cl_id=c.id: self._eliminar_cliente(cl_id)
                )
                btn_del.pack(side="left", padx=3)

    def _abrir_modal_nuevo(self):
        ClienteModalDialog(self.winfo_toplevel(), on_save_callback=self.cargar_clientes)

    def _abrir_modal_editar(self, cliente: Cliente):
        ClienteModalDialog(self.winfo_toplevel(), cliente=cliente, on_save_callback=self.cargar_clientes)

    def _eliminar_cliente(self, cliente_id: int):
        resp = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Desea eliminar o dar de baja a este cliente?",
            parent=self.winfo_toplevel()
        )
        if resp:
            exito, msg = self.cliente_service.eliminar(cliente_id)
            if exito:
                messagebox.showinfo("Éxito", msg, parent=self.winfo_toplevel())
                self.cargar_clientes()
            else:
                messagebox.showerror("Error", msg, parent=self.winfo_toplevel())
