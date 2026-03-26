"""
Utilidades de autenticación: hashing de passwords, obtención de sucursales del usuario
y funciones de auditoría.
"""
import bcrypt
import json


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


def log_audit(action_type, path=None, filter_data=None, response_status=None):
    """Log an audit event. Safe to call even if AUTH_ENABLED is False (no-op).

    Args:
        action_type: Type of event (page_view, login, logout, login_failed, filter_change, admin_action)
        path: Request path (auto-detected from Flask request if None)
        filter_data: Dict of filter values (serialized to JSON)
        response_status: HTTP response status code
    """
    try:
        from database import settings, AuthSessionLocal
        if not settings.SECRET_KEY:
            return
        from flask import request as flask_request
        from flask_login import current_user
        from auth.models import AuditLog

        db = AuthSessionLocal()
        try:
            entry = AuditLog(
                user_id=current_user.id if current_user.is_authenticated else None,
                username=current_user.username if current_user.is_authenticated else None,
                ip_address=flask_request.remote_addr or '0.0.0.0',
                user_agent=str(flask_request.user_agent)[:500] if flask_request.user_agent else None,
                method=flask_request.method,
                path=path or flask_request.path,
                action_type=action_type,
                filter_data=json.dumps(filter_data, default=str) if filter_data else None,
                response_status=response_status,
            )
            db.add(entry)
            db.commit()
        finally:
            db.close()
    except Exception:
        pass  # Fire-and-forget: never break the request


def cleanup_old_audit_logs(days=None):
    """Delete audit log entries older than N days.

    Args:
        days: Number of days to retain. Defaults to AUDIT_RETENTION_DAYS from config.
    """
    try:
        from database import settings, AuthSessionLocal
        if not settings.SECRET_KEY:
            return
        from datetime import datetime, timedelta
        from auth.models import AuditLog
        from config import AUDIT_RETENTION_DAYS

        if days is None:
            days = AUDIT_RETENTION_DAYS

        cutoff = datetime.utcnow() - timedelta(days=days)
        db = AuthSessionLocal()
        try:
            deleted = db.query(AuditLog).filter(AuditLog.timestamp < cutoff).delete()
            db.commit()
            if deleted:
                print(f"  - Audit log: {deleted} registros antiguos eliminados")
        finally:
            db.close()
    except Exception:
        pass
