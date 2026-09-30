import sqlite3
import os
import sys
import hashlib
from typing import Optional

# Determinar directorio base persistente (para scripts y para .EXE compilado)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = os.path.join(BASE_DIR, "ventas.db")


class Database:
    """Clase singleton / gestora de conexiones SQLite3."""
    _instance: Optional["Database"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash SHA-256 para contraseñas sin requerir librerías externas."""
        salt = "kardex_sales_suite_2026"
        return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

    def _init_db(self):
        """Crea las tablas y los índices si no existen, y ejecuta el seed inicial."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Tabla Usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'VENDEDOR',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Tabla Clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_documento TEXT NOT NULL DEFAULT 'DNI',
                    numero_documento TEXT UNIQUE NOT NULL,
                    nombre_razon_social TEXT NOT NULL,
                    email TEXT,
                    telefono TEXT,
                    direccion TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Tabla Productos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL DEFAULT 'General',
                    precio_costo REAL NOT NULL DEFAULT 0.0,
                    precio_venta REAL NOT NULL DEFAULT 0.0,
                    stock_actual INTEGER NOT NULL DEFAULT 0,
                    stock_minimo INTEGER NOT NULL DEFAULT 5,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Tabla Ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_venta TEXT UNIQUE NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    metodo_pago TEXT NOT NULL DEFAULT 'EFECTIVO',
                    subtotal REAL NOT NULL,
                    impuesto REAL NOT NULL,
                    descuento REAL NOT NULL DEFAULT 0.0,
                    total REAL NOT NULL,
                    notas TEXT,
                    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                );
            """)

            # 5. Tabla Detalle de Ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas (id) ON DELETE CASCADE,
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                );
            """)

            conn.commit()

            # Seed inicial de prueba si no hay usuarios
            cursor.execute("SELECT COUNT(*) as count FROM usuarios;")
            user_count = cursor.fetchone()["count"]

            if user_count == 0:
                self._seed_initial_data(cursor)
                conn.commit()

    def _seed_initial_data(self, cursor: sqlite3.Cursor):
        """Inserta datos de demostración para iniciar el sistema inmediatamente."""
        # Usuarios iniciales
        admin_pass = self.hash_password("123456")
        consultor_pass = self.hash_password("lucia2177$")
        vendedor_pass = self.hash_password("123456")

        cursor.executemany("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES (?, ?, ?, ?);
        """, [
            ("admin@lozano.com", admin_pass, "Administrador Principal", "ADMIN"),
            ("lucia@edu.com", consultor_pass, "Lucía Consultora", "CONSULTOR"),
            ("vendedor@lozano.com", vendedor_pass, "Carlos Vendedor", "VENDEDOR"),
        ])

        # Clientes iniciales
        cursor.executemany("""
            INSERT INTO clientes (tipo_documento, numero_documento, nombre_razon_social, email, telefono, direccion)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [
            ("DNI", "45891234", "Juan Pérez Mendoza", "juan.perez@gmail.com", "987654321", "Av. Primavera 450"),
            ("RUC", "20601892341", "Inka Retail S.A.C.", "compras@inkaretail.pe", "991223344", "Av. Javier Prado 1200"),
            ("DNI", "71239876", "María Rodríguez Gómez", "m.rodriguez@hotmail.com", "955112233", "Calle Las Flores 320"),
            ("RUC", "20554901238", "Tech Solutions Perú S.A.", "contacto@techsol.pe", "944556677", "Jr. Puno 840"),
            ("DNI", "10456789", "Carlos Benavides Torres", "carlos.b@empresa.com", "912345678", "Av. Arequipa 2100"),
        ])

        # Productos iniciales con precios reales en Soles peruanos (S/.)
        cursor.executemany("""
            INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock_actual, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, [
            ("PROD-001", "Laptop Lenovo ThinkPad 15\"", "Computación", 2400.00, 3299.00, 15, 4),
            ("PROD-002", "Mouse Inalámbrico Logitech MX", "Accesorios", 180.00, 289.00, 30, 8),
            ("PROD-003", "Teclado Mecánico RGB Redragon", "Accesorios", 120.00, 199.00, 20, 5),
            ("PROD-004", "Monitor Dell 27\" IPS Full HD", "Monitores", 520.00, 799.00, 10, 3),
            ("PROD-005", "Disco Sólido SSD NVMe 1TB Kingston", "Almacenamiento", 190.00, 289.00, 25, 6),
            ("PROD-006", "Memoria RAM 16GB DDR4 Corsair", "Componentes", 110.00, 179.00, 18, 5),
            ("PROD-007", "Auriculares Gamer HyperX Cloud II", "Audio", 210.00, 329.00, 12, 4),
            ("PROD-008", "Cámara Web Full HD 1080p con Micrófono", "Accesorios", 75.00, 129.00, 8, 5),
            ("PROD-009", "Impresora Multifuncional Epson EcoTank", "Impresoras", 680.00, 999.00, 6, 2),
            ("PROD-010", "Router WiFi 6 Gigabit TP-Link", "Redes", 160.00, 249.00, 3, 5), # Stock bajo para alerta
        ])

        # Ventas iniciales para tener reportes con datos reales en Soles (S/.)
        cursor.execute("SELECT id FROM usuarios WHERE username = 'admin@lozano.com';")
        admin_id = cursor.fetchone()["id"]

        cursor.execute("SELECT id FROM clientes LIMIT 3;")
        client_ids = [row["id"] for row in cursor.fetchall()]

        ventas_demo = [
            ("VNT-2026-0001", client_ids[0], admin_id, "EFECTIVO", 3299.00, 593.82, 0.0, 3892.82, "Primera venta Laptop Lenovo"),
            ("VNT-2026-0002", client_ids[1], admin_id, "TRANSFERENCIA", 1775.00, 310.50, 50.0, 2035.50, "Compra corporativa accesorios"),
            ("VNT-2026-0003", client_ids[2], admin_id, "TARJETA", 799.00, 143.82, 0.0, 942.82, "Monitor Dell"),
        ]

        for cod, cl_id, us_id, metodo, sub, imp, desc, tot, notas in ventas_demo:
            cursor.execute("""
                INSERT INTO ventas (codigo_venta, cliente_id, usuario_id, metodo_pago, subtotal, impuesto, descuento, total, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (cod, cl_id, us_id, metodo, sub, imp, desc, tot, notas))
            v_id = cursor.lastrowid

            if cod == "VNT-2026-0001":
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, 1, 1, 3299.00, 3299.00);", (v_id,))
            elif cod == "VNT-2026-0002":
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, 2, 2, 289.00, 578.00);", (v_id,))
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, 3, 2, 199.00, 398.00);", (v_id,))
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, 4, 1, 799.00, 799.00);", (v_id,))
            elif cod == "VNT-2026-0003":
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, 4, 1, 799.00, 799.00);", (v_id,))
