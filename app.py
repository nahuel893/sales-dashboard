#!/usr/bin/env python3
"""
Dashboard de ventas - Medallion ETL
Punto de entrada principal con sistema de navegación multi-tablero.

Uso:
    python app.py

Acceder en: http://localhost:8050
"""
from datetime import date, timedelta
from dash import Dash, html, dcc, callback, Output, Input
import dash_mantine_components as dmc

# Imports locales
from config import SERVER_CONFIG
from database import settings
from data.queries import (
    obtener_genericos, obtener_marcas, obtener_rutas, obtener_preventistas,
    obtener_rango_fechas, obtener_anios_disponibles, cargar_ventas_por_cliente
)
from layouts.home_layout import create_home_layout
from layouts.main_layout import create_ventas_layout
from layouts.tablero_layout import create_tablero_layout
from layouts.ytd_layout import create_ytd_layout
from layouts.cliente_layout import create_cliente_layout
from layouts.clientes_layout import create_clientes_layout
from data.ytd_queries import obtener_anios_disponibles_ytd, obtener_mes_actual, obtener_anio_actual
from cache import init_app as init_cache, warmup_cache

# Crear app (antes de queries para que init_cache tenga el server)
app = Dash(__name__, suppress_callback_exceptions=True,
           external_stylesheets=dmc.styles.ALL)
app.title = "Medallion ETL - Dashboard"
server = app.server  # Flask server para gunicorn

# Inicializar cache ANTES de cualquier query con @cache.memoize
init_cache(server)

# Warmup: pre-carga queries comunes en cache
# (estas mismas llamadas alimentan las variables que necesitan los layouts)
print("Obteniendo rango de fechas...")
fecha_min, fecha_max = obtener_rango_fechas()
print(f"Datos disponibles: {fecha_min} a {fecha_max}")

print("Cargando filtros de producto...")
lista_genericos = obtener_genericos()
lista_marcas = obtener_marcas()
print(f"  - {len(lista_genericos)} genericos, {len(lista_marcas)} marcas")

print("Cargando filtros de ruta/preventista...")
lista_rutas = obtener_rutas()
lista_preventistas = obtener_preventistas()
print(f"  - {len(lista_rutas)} rutas, {len(lista_preventistas)} preventistas")

# Carga inicial de datos para verificar conectividad (va al cache)
hoy_startup = date.today()
fecha_desde_startup = hoy_startup.replace(day=1)
print(f"Cargando datos iniciales ({fecha_desde_startup} a {hoy_startup})...")
df_ventas = cargar_ventas_por_cliente(fecha_desde_startup, hoy_startup)
clientes_con_ventas = len(df_ventas[df_ventas['cantidad_total'] > 0])
clientes_sin_ventas = len(df_ventas[df_ventas['cantidad_total'] == 0])
print(f"Cargados {len(df_ventas):,} clientes ({clientes_con_ventas:,} con ventas, {clientes_sin_ventas:,} sin ventas)")

# Autenticación condicional: solo si SECRET_KEY está configurada
AUTH_ENABLED = bool(settings.SECRET_KEY)
if AUTH_ENABLED:
    server.secret_key = settings.SECRET_KEY
    from auth.middleware import init_auth, protect_all_routes
    print("Configurando autenticación...")
    init_auth(server)
    allowed_origins = None
    if settings.ALLOWED_ORIGINS:
        allowed_origins = set(o.strip() for o in settings.ALLOWED_ORIGINS.split(',') if o.strip())
    protect_all_routes(server, allowed_origins=allowed_origins)

    # Security headers (A-01, A-02)
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    }

    @server.after_request
    def apply_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        response.headers.pop('Server', None)
        return response

    # Limpieza de registros de auditoría antiguos al inicio
    from auth.utils import cleanup_old_audit_logs
    cleanup_old_audit_logs()

    print("  - Autenticación habilitada")
else:
    print("  - Autenticación deshabilitada (SECRET_KEY no configurada)")

# Datos para YTD Dashboard
print("Cargando datos para YTD Dashboard...")
try:
    ytd_anios = obtener_anios_disponibles_ytd()
    ytd_anio_actual = obtener_anio_actual()
    ytd_mes_actual = obtener_mes_actual()
    print(f"  - Años disponibles: {ytd_anios}")
except Exception as e:
    print(f"  - Error cargando datos YTD: {e}")
    ytd_anios = [2025, 2024]
    ytd_anio_actual = 2025
    ytd_mes_actual = 12

# Años disponibles para tablero de comparación
print("Cargando años disponibles...")
lista_anios = obtener_anios_disponibles()
print(f"  - Años: {lista_anios}")

# ytd_layout se pre-crea (no tiene fechas que cambien, solo año/mes)
ytd_layout = create_ytd_layout(
    anio_actual=ytd_anio_actual,
    mes_actual=ytd_mes_actual,
    anios_disponibles=ytd_anios
)

# Layout principal con routing
app.layout = dmc.MantineProvider(
    html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])
)


# Callback de routing
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Muestra la página correspondiente según la URL."""
    if AUTH_ENABLED and pathname == '/login':
        from layouts.login_layout import create_login_layout
        return create_login_layout()

    # Proteger todas las rutas: redirigir a /login si no está autenticado
    if AUTH_ENABLED:
        from flask_login import current_user
        if not current_user.is_authenticated:
            return dcc.Location(href='/login', id='auth-redirect')
    if AUTH_ENABLED and pathname == '/logout':
        from flask_login import logout_user, current_user
        if current_user.is_authenticated:
            logout_user()
        return dcc.Location(href='/login', id='logout-redirect')
    if AUTH_ENABLED and pathname == '/admin/usuarios':
        from flask_login import current_user as cu
        if cu.is_authenticated and cu.is_admin:
            from layouts.admin_layout import create_admin_layout
            return create_admin_layout()
        return dcc.Location(href='/', id='admin-redirect')
    if AUTH_ENABLED and pathname == '/admin/audit':
        from flask_login import current_user as cu
        if cu.is_authenticated and cu.is_admin:
            from layouts.audit_layout import create_audit_layout
            return create_audit_layout()
        return dcc.Location(href='/', id='admin-audit-redirect')
    if pathname == '/ventas':
        hoy = date.today()
        return create_ventas_layout(
            fecha_min=fecha_min,
            fecha_max=fecha_max,
            fecha_desde_default=hoy.replace(day=1),
            fecha_hasta_default=hoy,
            lista_genericos=lista_genericos,
            lista_marcas=lista_marcas,
            lista_rutas=lista_rutas,
            lista_preventistas=lista_preventistas
        )
    elif pathname == '/ytd':
        return ytd_layout
    elif pathname == '/clientes':
        return create_clientes_layout()
    elif pathname and pathname.startswith('/cliente/'):
        parts = pathname.strip('/').split('/')
        if len(parts) == 2:
            try:
                id_cliente = int(parts[1])
                return create_cliente_layout(id_cliente)
            except (ValueError, IndexError):
                pass
        return html.Div([
            html.H2("Cliente no encontrado", style={'textAlign': 'center', 'padding': '60px', 'color': '#666'})
        ])
    elif pathname == '/tablero':
        hoy = date.today()
        return create_tablero_layout(
            fecha_min=fecha_min,
            fecha_max=fecha_max,
            fecha_desde_default=hoy.replace(day=1),
            fecha_hasta_default=hoy,
            lista_genericos=lista_genericos,
            lista_marcas=lista_marcas,
            lista_rutas=lista_rutas,
            lista_preventistas=lista_preventistas,
            lista_anios=lista_anios
        )
    else:
        # Página de inicio: generar dinámicamente con info del usuario si auth activa
        user = None
        if AUTH_ENABLED:
            try:
                from flask_login import current_user
                if current_user.is_authenticated:
                    user = current_user
            except Exception:
                pass
        return create_home_layout(user=user)


# Importar callbacks (se registran automaticamente)
# Esto debe estar DESPUES de crear app y layout
import callbacks.callbacks  # noqa: E402, F401
import callbacks.tablero_callbacks  # noqa: E402, F401
import callbacks.ytd_callbacks  # noqa: E402, F401
import callbacks.cliente_callbacks  # noqa: E402, F401
import callbacks.clientes_callbacks  # noqa: E402, F401
if AUTH_ENABLED:
    import callbacks.auth_callbacks  # noqa: E402, F401
    import callbacks.admin_callbacks  # noqa: E402, F401
    import callbacks.audit_callbacks  # noqa: E402, F401


if __name__ == '__main__':
    print("\n" + "="*50)
    print("DASHBOARD MEDALLION ETL")
    print("="*50)
    print(f"Acceder localmente: http://localhost:{SERVER_CONFIG['port']}")
    print(f"Acceder en red:     http://<tu-ip>:{SERVER_CONFIG['port']}")
    print("Presionar Ctrl+C para detener")
    print("="*50 + "\n")

    app.run(
        debug=SERVER_CONFIG['debug'],
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port']
    )
