from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Usuario:
    id: Optional[int] = None
    username: str = ""
    nombre_completo: str = ""
    rol: str = "VENDEDOR"
    is_active: bool = True
    created_at: Optional[str] = None


@dataclass
class Cliente:
    id: Optional[int] = None
    tipo_documento: str = "DNI"
    numero_documento: str = ""
    nombre_razon_social: str = ""
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


@dataclass
class Producto:
    id: Optional[int] = None
    codigo: str = ""
    nombre: str = ""
    categoria: str = "General"
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    stock_actual: int = 0
    stock_minimo: int = 5
    is_active: bool = True
    created_at: Optional[str] = None

    @property
    def es_stock_bajo(self) -> bool:
        return self.stock_actual <= self.stock_minimo

    @property
    def margen_ganancia(self) -> float:
        if self.precio_costo > 0:
            return round(((self.precio_venta - self.precio_costo) / self.precio_costo) * 100, 2)
        return 0.0


@dataclass
class ItemCarrito:
    producto: Producto
    cantidad: int
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        return round(self.cantidad * self.precio_unitario, 2)


@dataclass
class DetalleVenta:
    id: Optional[int] = None
    venta_id: Optional[int] = None
    producto_id: int = 0
    producto_nombre: str = ""
    producto_codigo: str = ""
    cantidad: int = 0
    precio_unitario: float = 0.0
    subtotal: float = 0.0


@dataclass
class Venta:
    id: Optional[int] = None
    codigo_venta: str = ""
    cliente_id: int = 0
    cliente_nombre: str = ""
    cliente_documento: str = ""
    usuario_id: int = 0
    usuario_nombre: str = ""
    metodo_pago: str = "EFECTIVO"
    subtotal: float = 0.0
    impuesto: float = 0.0
    descuento: float = 0.0
    total: float = 0.0
    notas: Optional[str] = None
    fecha_venta: Optional[str] = None
    detalles: List[DetalleVenta] = field(default_factory=list)
