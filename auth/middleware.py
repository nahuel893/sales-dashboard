"""
Middleware de autenticación: inicialización de Flask-Login, Flask-Session
y protección de rutas con before_request.
"""
from flask import redirect, request, session
from flask_login import LoginManager, current_user
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Paths públicos que no requieren autenticación
PUBLIC_PATHS = {
    '/login',
    '/_dash-layout',
    '/_dash-dependencies',
    '/assets/',
    '/_favicon.ico',
    '/_reload-hash',
}


def _is_public_path(path):
    """Determina si un path es público (no requiere auth)."""
    if path in PUBLIC_PATHS:
        return True
    for prefix in PUBLIC_PATHS:
        if prefix.endswith('/') and path.startswith(prefix):
            return True
    return False


def init_auth(flask_app, db_url):
    """Configura Flask-Login y Flask-Session en el servidor Flask de Dash.

    Args:
        flask_app: instancia de Flask (app.server)
        db_url: string de conexión a PostgreSQL
    """
    # Configurar sesiones server-side en PostgreSQL
    flask_app.config['SESSION_TYPE'] = 'sqlalchemy'
    engine = create_engine(db_url)
    flask_app.config['SESSION_SQLALCHEMY'] = engine
    flask_app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    flask_app.config['SESSION_SQLALCHEMY_SCHEMA'] = 'app'
    flask_app.config['SESSION_PERMANENT'] = True
    flask_app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24h

    Session(flask_app)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(flask_app)
    login_manager.login_view = '/login'

    # Session factory para cargar usuarios
    _SessionLocal = sessionmaker(bind=engine)

    @login_manager.user_loader
    def load_user(user_id):
        from auth.models import User
        db = _SessionLocal()
        try:
            return db.query(User).get(int(user_id))
        finally:
            db.close()


def protect_all_routes(flask_app):
    """Protege TODAS las rutas (incluyendo callbacks Dash) con before_request."""

    @flask_app.before_request
    def require_login():
        if _is_public_path(request.path):
            return None
        if not current_user.is_authenticated:
            # Para requests de callbacks Dash, retornar 401
            if request.path.startswith('/_dash-update-component'):
                from flask import abort
                abort(401)
            return redirect('/login')
        return None
