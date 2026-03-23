"""
Utilidades de autenticación: hashing de passwords y obtención de sucursales del usuario.
"""
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith('$2b$'):
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    # Legacy SHA-256: "salt:hash"
    parts = stored_hash.split(':', 1)
    if len(parts) == 2:
        import hashlib
        salt, hash_hex = parts
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_hex
    return False


def get_user_sucursales():
    """Retorna lista de id_sucursal permitidos para el usuario actual.

    - Si auth no está activa: retorna None (sin filtro).
    - Si user es admin o gerente: retorna None (ve todo).
    - Si user es supervisor: retorna lista de id_sucursal asignados.
    """
    try:
        from database import settings
        if not settings.SECRET_KEY:
            return None
    except Exception:
        return None

    try:
        from flask_login import current_user
        if not current_user or not current_user.is_authenticated:
            return None
        if current_user.is_admin or current_user.is_gerente:
            return None
        ids = current_user.sucursales_ids
        return ids if ids else []
    except Exception:
        return None
