from typing import Optional, Tuple
from sistema_ventas_python.database.connection import Database
from sistema_ventas_python.models.models import Usuario


class AuthService:
    """Lógica de negocio para autenticación de usuarios."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def autenticar(self, username: str, password_plana: str) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Valida las credenciales contra la base de datos SQLite.
        Retorna (exito, mensaje, usuario).
        """
        username = username.strip().lower()
        if not username or not password_plana:
            return False, "Por favor ingrese su usuario y contraseña.", None

        hash_ingresado = self.db.hash_password(password_plana)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, nombre_completo, rol, is_active, created_at
                FROM usuarios
                WHERE LOWER(username) = ?;
            """, (username,))
            row = cursor.fetchone()

            if not row:
                return False, "Usuario no encontrado.", None

            if row["password_hash"] != hash_ingresado:
                return False, "Contraseña incorrecta.", None

            if not row["is_active"]:
                return False, "La cuenta se encuentra inactiva.", None

            usuario = Usuario(
                id=row["id"],
                username=row["username"],
                nombre_completo=row["nombre_completo"],
                rol=row["rol"],
                is_active=bool(row["is_active"]),
                created_at=str(row["created_at"])
            )
            return True, "Inicio de sesión exitoso.", usuario
