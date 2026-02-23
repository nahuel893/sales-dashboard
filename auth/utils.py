"""
Utilidades de autenticación: hashing de passwords y obtención de sucursales del usuario.
"""
from hashlib import sha256
import secrets


def hash_password(password):
    """Hashea un password con salt usando SHA-256."""
    salt = secrets.token_hex(16)
    hashed = sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def check_password(password, password_hash):
    """Verifica un password contra su hash."""
    try:
        salt, hashed = password_hash.split(':')
        return sha256(f"{salt}{password}".encode()).hexdigest() == hashed
    except (ValueError, AttributeError):
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
