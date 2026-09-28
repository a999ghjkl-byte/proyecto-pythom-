# 💎 Sistema de Ventas & Facturación — 100% Python

Aplicación de escritorio moderna construida **completamente en Python** utilizando **CustomTkinter** para la interfaz gráfica y **SQLite3** nativo para la persistencia de datos local, sin HTML, CSS ni JavaScript, y sin requerir servidores externos.

---

## 🚀 Cómo Ejecutar la Aplicación

Para iniciar el sistema, simplemente ejecuta:

```bash
python main.py
```

---

## 🔑 Credenciales de Acceso Preconfiguradas

El sistema inicializa automáticamente la base de datos `ventas.db` con usuarios y datos demostrativos listos para usar:

| Usuario / Correo | Contraseña | Rol | Permisos / Acceso |
| :--- | :--- | :--- | :--- |
| **admin@lozano.com** | `123456` | **ADMIN** | Acceso total (Dashboard, Ventas POS, Catálogo, Clientes, Reportes) |
| **lucia@edu.com** | `lucia2177$` | **CONSULTOR** | **Solo lectura**: Acceso exclusivo al Dashboard con KPIs y métricas breves |
| **vendedor@lozano.com** | `123456` | **VENDEDOR** | Operaciones comerciales (Punto de Venta POS, Clientes, Catálogo) |

> 💡 *En la pantalla de Login hay botones de acceso rápido que completan las credenciales con un solo clic.*

---

## 🏗️ Arquitectura del Proyecto (Separación de Capas)

El código está estructurado en clases siguiendo los principios de arquitectura limpia y separación de responsabilidades:

```text
kardex_login_fullpython/
│
├── main.py                          # Punto de entrada directo
├── ventas.db                        # Base de datos SQLite3 automática
│
└── sistema_ventas_python/
    ├── database/
    │   └── connection.py            # Gestión SQLite3 (tablas, índices, seed inicial, hash SHA-256)
    │
    ├── models/
    │   └── models.py                # Modelos OOP (Usuario, Cliente, Producto, Venta, ItemCarrito)
    │
    ├── services/                    # Capa de Lógica de Negocio (sin dependencias de GUI)
    │   ├── auth_service.py          # Autenticación, validación de sesiones y roles
    │   ├── producto_service.py      # CRUD de inventario, stock crítico y búsqueda
    │   ├── cliente_service.py       # CRUD de cartera de clientes y documentos
    │   ├── venta_service.py         # Lógica atómica de venta, carrito y actualización de stock
    │   └── reporte_service.py       # KPIs, top productos y filtros por período
    │
    └── views/                       # Interfaz Gráfica (CustomTkinter)
        ├── login_view.py            # Pantalla de Login moderna con feedback visual
        ├── main_window.py           # Ventana principal con Sidebar de navegación y control de roles
        ├── dashboard_view.py        # Dashboard con tarjetas KPI, ranking y métricas ejecutivas
        ├── ventas_view.py           # Punto de Venta (POS) con Carrito de compras y comprobante digital
        ├── productos_view.py        # Gestión de catálogo con búsqueda dinámica y modal de alta/edición
        ├── clientes_view.py         # Gestión de clientes con modal y búsqueda instantánea
        └── reportes_view.py         # Historial de ventas, filtros temporales y visor de comprobantes
```

---

## 🌟 Módulos Implementados

1. **Pantalla de Inicio de Sesión (Login)**
   - Diseño tipo tarjeta con diseño moderno en modo oscuro/claro.
   - Validación segura de contraseña y control de usuario inactivo.
   - Botón para alternar visibilidad de contraseña (👁️ / 🙈).
   - Atajo con la tecla `Enter`.

2. **Dashboard / Resumen Ejecutivo**
   - Tarjetas de KPIs en tiempo real: Facturación Total, Ventas Hoy, Ticket Promedio, Alertas de Stock Crítico.
   - Ranking interactivo de los productos más vendidos.
   - Distribución de ventas por método de pago (Efectivo, Tarjeta, Transferencia).
   - Acceso exclusivo y optimizado para usuarios con rol **CONSULTOR** (como se solicitó).

3. **Módulo de Registro de Productos & Inventario**
   - Buscador dinámico por SKU, nombre o categoría en tiempo real.
   - Botón de filtro rápido "⚠️ Ver Solo Stock Crítico".
   - Formulario modal emergente para registrar y editar productos.
   - Control de precio de compra, precio de venta, stock mínimo y stock actual.

4. **Módulo de Ventas con Carrito de Compras (POS)**
   - Catálogo interactivo de productos a la izquierda para añadir al carrito con un clic.
   - Carrito de compras con controles incrementales `[-]` y `[+]`, cálculo de subtotal por producto y botón de eliminar item.
   - Selección de cliente desde combobox.
   - Cálculo automático en tiempo real de Subtotal, Descuentos opcionales, Impuesto (18%) y Total.
   - Transacción atómica en SQLite: descuenta automáticamente las unidades del inventario y genera el código consecutivo `VNT-2026-XXXX`.
   - Emisión de comprobante digital detallado al completar la venta.

5. **Módulo de Clientes**
   - Listado ordenado con búsqueda por nombre o número de documento (DNI/RUC).
   - Modal de alta y edición con validación de documento único.

6. **Módulo de Reportes & Historial**
   - Filtros por rangos de fecha rápidos: *Hoy*, *Últimos 7 días*, *Mes Actual*, *Histórico Completo*.
   - Resumen financiero del período seleccionado.
   - Visor detallado de cualquier venta anterior para reimprimir o revisar items.
