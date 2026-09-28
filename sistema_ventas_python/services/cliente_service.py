from typing import List, Optional, Tuple
from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.models.models import Cliente


class ClienteService:
    """Lógica de negocio para administración de clientes."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def listar_todos(self, solo_activos: bool = True) -> List[Cliente]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, tipo_documento, numero_documento, nombre_razon_social, email, telefono, direccion, is_active, created_at FROM clientes"
            if solo_activos:
                query += " WHERE is_active = 1"
            query += " ORDER BY nombre_razon_social ASC;"

            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                Cliente(
                    id=row["id"],
                    tipo_documento=row["tipo_documento"],
                    numero_documento=row["numero_documento"],
                    nombre_razon_social=row["nombre_razon_social"],
                    email=row["email"],
                    telefono=row["telefono"],
                    direccion=row["direccion"],
                    is_active=bool(row["is_active"]),
                    created_at=str(row["created_at"])
                ) for row in rows
            ]

    def buscar(self, termino: str) -> List[Cliente]:
        termino = f"%{termino.strip().lower()}%"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tipo_documento, numero_documento, nombre_razon_social, email, telefono, direccion, is_active, created_at
                FROM clientes
                WHERE is_active = 1 AND (LOWER(nombre_razon_social) LIKE ? OR LOWER(numero_documento) LIKE ? OR LOWER(email) LIKE ?)
                ORDER BY nombre_razon_social ASC;
            """, (termino, termino, termino))
            rows = cursor.fetchall()
            return [
                Cliente(
                    id=row["id"],
                    tipo_documento=row["tipo_documento"],
                    numero_documento=row["numero_documento"],
                    nombre_razon_social=row["nombre_razon_social"],
                    email=row["email"],
                    telefono=row["telefono"],
                    direccion=row["direccion"],
                    is_active=bool(row["is_active"]),
                    created_at=str(row["created_at"])
                ) for row in rows
            ]

    def guardar(self, cliente: Cliente) -> Tuple[bool, str, Optional[int]]:
        if not cliente.numero_documento or not cliente.nombre_razon_social:
            return False, "El número de documento y el nombre/razón social son obligatorios.", None

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if cliente.id:
                    # Validar documento único excluyendo al actual
                    cursor.execute("""
                        SELECT id FROM clientes 
                        WHERE numero_documento = ? AND id != ?;
                    """, (cliente.numero_documento.strip(), cliente.id))
                    if cursor.fetchone():
                        return False, f"Ya existe otro cliente con el documento '{cliente.numero_documento}'.", None

                    cursor.execute("""
                        UPDATE clientes
                        SET tipo_documento = ?, numero_documento = ?, nombre_razon_social = ?,
                            email = ?, telefono = ?, direccion = ?, is_active = ?
                        WHERE id = ?;
                    """, (
                        cliente.tipo_documento.strip(),
                        cliente.numero_documento.strip(),
                        cliente.nombre_razon_social.strip(),
                        cliente.email.strip() if cliente.email else None,
                        cliente.telefono.strip() if cliente.telefono else None,
                        cliente.direccion.strip() if cliente.direccion else None,
                        1 if cliente.is_active else 0,
                        cliente.id
                    ))
                    conn.commit()
                    return True, "Cliente actualizado con éxito.", cliente.id
                else:
                    # Validar documento único
                    cursor.execute("SELECT id FROM clientes WHERE numero_documento = ?;", (cliente.numero_documento.strip(),))
                    if cursor.fetchone():
                        return False, f"El cliente con documento '{cliente.numero_documento}' ya se encuentra registrado.", None

                    cursor.execute("""
                        INSERT INTO clientes (tipo_documento, numero_documento, nombre_razon_social, email, telefono, direccion, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (
                        cliente.tipo_documento.strip(),
                        cliente.numero_documento.strip(),
                        cliente.nombre_razon_social.strip(),
                        cliente.email.strip() if cliente.email else None,
                        cliente.telefono.strip() if cliente.telefono else None,
                        cliente.direccion.strip() if cliente.direccion else None,
                        1
                    ))
                    conn.commit()
                    return True, "Cliente registrado con éxito.", cursor.lastrowid
            except Exception as e:
                return False, f"Error al guardar cliente: {str(e)}", None

    def eliminar(self, cliente_id: int) -> Tuple[bool, str]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM ventas WHERE cliente_id = ?;", (cliente_id,))
            tiene_ventas = cursor.fetchone()["count"] > 0

            if tiene_ventas:
                cursor.execute("UPDATE clientes SET is_active = 0 WHERE id = ?;", (cliente_id,))
                msg = "Cliente archivado por tener compras asociadas."
            else:
                cursor.execute("DELETE FROM clientes WHERE id = ?;", (cliente_id,))
                msg = "Cliente eliminado permanentemente."

            conn.commit()
            return True, msg
