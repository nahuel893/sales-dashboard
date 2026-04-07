"""
Middleware de autenticación: inicialización de Flask-Login, Flask-Session
y protección de rutas con before_request.
"""
import time
from collections import defaultdict
from flask import redirect, request, session, jsonify
from flask_login import LoginManager, current_user
from flask_session import Session
from sqlalchemy.orm import sessionmaker

from pathlib import Path
from database import auth_engine

SESSION_DIR = Path(__file__).parent.parent / 'session_data'

# Paths públicos que no requieren autenticación
PUBLIC_PATHS = {
    '/login',
    '/assets/',
    '/_favicon.ico',
    '/_dash-component-suites/',
    '/_dash-gc/',
}

# Dash internal endpoints blocked entirely for unauthenticated users.
# /_reload-hash exposes package versions without providing functionality.
DASH_BLOCKED_PATHS = {'/_reload-hash'}

# Dash layout/dependencies: serve stub JSON for unauthenticated users
# (prevents leaking full component tree while allowing login page to bootstrap)
DASH_STUB_PATHS = {'/_dash-layout', '/_dash-dependencies'}


def _is_public_path(path):
    """Determina si un path es público (no requiere auth)."""
    if path in PUBLIC_PATHS:
        return True
    for prefix in PUBLIC_PATHS:
        if prefix.endswith('/') and path.startswith(prefix):
            return True
    return False


def init_auth(flask_app):
    """Configura Flask-Login y Flask-Session en el servidor Flask de Dash.

    Args:
        flask_app: instancia de Flask (app.server)
    """
    # Configurar sesiones server-side
    from database import settings
    if settings.REDIS_URL:
        import redis as redis_lib
        flask_app.config['SESSION_TYPE'] = 'redis'
        flask_app.config['SESSION_REDIS'] = redis_lib.from_url(settings.REDIS_URL)
        flask_app.config['SESSION_KEY_PREFIX'] = 'sd_session:'
    else:
        SESSION_DIR.mkdir(exist_ok=True)
        flask_app.config['SESSION_TYPE'] = 'filesystem'
        flask_app.config['SESSION_FILE_DIR'] = str(SESSION_DIR)
    flask_app.config['SESSION_PERMANENT'] = True
    flask_app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 min
    flask_app.config['SESSION_REFRESH_EACH_REQUEST'] = False

    Session(flask_app)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(flask_app)
    login_manager.login_view = '/login'

    # Session factory para cargar usuarios
    _SessionLocal = sessionmaker(bind=auth_engine)

    @login_manager.user_loader
    def load_user(user_id):
        from auth.models import User
        from sqlalchemy.orm import joinedload
        db = _SessionLocal()
        try:
            user = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.sucursales))
                .filter(User.id == int(user_id))
                .first()
            )
            db.expunge_all()
            return user
        finally:
            db.close()


def protect_all_routes(flask_app, allowed_origins=None):
    """Protege TODAS las rutas (incluyendo callbacks Dash) con before_request.

    Args:
        flask_app: instancia de Flask (app.server)
        allowed_origins: set of allowed Origin values for POST requests.
            If None or empty, Origin validation is skipped (permissive).
    """

    # C-02: Rate limiting for unauthenticated users on /_dash-update-component
    RATE_LIMIT_MAX = 5          # max requests per window
    RATE_LIMIT_WINDOW = 60      # window in seconds

    from database import settings as _settings
    if _settings.REDIS_URL:
        import redis as redis_lib
        _redis_rl = redis_lib.from_url(_settings.REDIS_URL)

        def _is_rate_limited(ip):
            """Redis-backed rate limiter (shared across workers)."""
            key = f"sd_rl:{ip}"
            count = _redis_rl.incr(key)
            if count == 1:
                _redis_rl.expire(key, RATE_LIMIT_WINDOW)
            return count > RATE_LIMIT_MAX
    else:
        _rate_limit_store = defaultdict(list)

        def _is_rate_limited(ip):
            """In-memory rate limiter (per-worker)."""
            now = time.time()
            cutoff = now - RATE_LIMIT_WINDOW
            timestamps = [t for t in _rate_limit_store[ip] if t > cutoff]
            if not timestamps:
                del _rate_limit_store[ip]
                timestamps = []
            else:
                _rate_limit_store[ip] = timestamps
            if len(timestamps) >= RATE_LIMIT_MAX:
                return True
            _rate_limit_store[ip].append(now)
            return False

    @flask_app.before_request
    def require_login():
        # A-03: Origin validation on POST requests
        if request.method == 'POST' and allowed_origins:
            origin = request.headers.get('Origin')
            if origin and origin not in allowed_origins:
                return jsonify({"error": "origin rejected"}), 403

        # C-01: Block /_reload-hash for unauthenticated users (exposes versions)
        if request.path in DASH_BLOCKED_PATHS and not current_user.is_authenticated:
            return jsonify({"error": "forbidden"}), 403

        # C-01: Serve stub layout/dependencies for unauthenticated users
        # (prevents leaking full component tree while allowing login to bootstrap)
        if request.path in DASH_STUB_PATHS and not current_user.is_authenticated:
            from flask import Response
            from auth.utils import get_stub_layout_json, get_stub_dependencies_json
            stub_fn = get_stub_layout_json if request.path == '/_dash-layout' else get_stub_dependencies_json
            return Response(stub_fn(), content_type='application/json')

        if _is_public_path(request.path):
            return None
        # Los callbacks Dash (_dash-update-component) se dejan pasar —
        # el routing callback en app.py maneja la redirección a /login
        if request.path.startswith('/_dash-update-component'):
            # C-02: Rate limit unauthenticated users (5/min per IP)
            if not current_user.is_authenticated:
                ip = request.remote_addr or '0.0.0.0'
                if _is_rate_limited(ip):
                    return jsonify({"error": "rate limit exceeded"}), 429
            else:
                # Refresh session TTL only on real user callback activity
                session.modified = True
            return None
        if not current_user.is_authenticated:
            return redirect('/login')
        return None

    # Paths to skip in audit logging (static assets and Dash internals)
    AUDIT_SKIP_PREFIXES = (
        '/assets/',
        '/_dash-component-suites/',
        '/_dash-gc/',
        '/_favicon.ico',
        '/_dash-update-component',
        '/_dash-layout',
        '/_dash-dependencies',
        '/_reload-hash',
    )

    # Known page routes to log
    AUDIT_PAGE_PREFIXES = (
        '/', '/ventas', '/ytd', '/clientes', '/cliente/',
        '/tablero', '/admin/', '/login', '/logout',
    )

    @flask_app.after_request
    def audit_log_request(response):
        """Log page views and auth events for authenticated users."""
        try:
            path = request.path
            method = request.method

            # Skip static assets and Dash internals
            if any(path.startswith(prefix) for prefix in AUDIT_SKIP_PREFIXES):
                return response

            # Only log GET requests to known page routes
            if method != 'GET':
                return response

            # Check if path matches a known page route
            is_page = path == '/' or any(
                path == route or (route.endswith('/') and path.startswith(route))
                for route in AUDIT_PAGE_PREFIXES if route != '/'
            )
            if not is_page:
                return response

            # Determine action_type
            if path == '/logout':
                action_type = 'logout'
            else:
                action_type = 'page_view'

            from auth.utils import log_audit
            log_audit(
                action_type=action_type,
                path=path,
                response_status=response.status_code,
            )
        except Exception:
            pass  # Never break the response

        return response
