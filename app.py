#!/usr/bin/env python3
"""
Dashboard de ventas - Medallion ETL
Punto de entrada principal con sistema de navegación multi-tablero.

Uso:
    python app.py

Acceder en: http://localhost:8050
"""
from datetime import timedelta
from dash import Dash, html, dcc, callback, Output, Input
import dash_mantine_components as dmc

# Imports locales
from config import SERVER_CONFIG
from data.queries import (
    obtener_genericos, obtener_marcas, obtener_rutas, obtener_preventistas,
    obtener_rango_fechas, cargar_ventas_por_cliente
)
from layouts.home_layout import create_home_layout
from layouts.main_layout import create_ventas_layout
from layouts.ytd_layout import create_ytd_layout
from layouts.cliente_layout import create_cliente_layout
from data.ytd_queries import obtener_anios_disponibles_ytd, obtener_mes_actual, obtener_anio_actual

# Obtener rango de fechas
print("Obteniendo rango de fechas...")
fecha_min, fecha_max = obtener_rango_fechas()
print(f"Datos disponibles: {fecha_min} a {fecha_max}")

# Obtener listas para filtros
print("Cargando filtros de producto...")
lista_genericos = obtener_genericos()
lista_marcas = obtener_marcas()
print(f"  - {len(lista_genericos)} genericos, {len(lista_marcas)} marcas")

print("Cargando filtros de ruta/preventista...")
lista_rutas = obtener_rutas()
lista_preventistas = obtener_preventistas()
print(f"  - {len(lista_rutas)} rutas, {len(lista_preventistas)} preventistas")

# Cargar datos iniciales (ultimo mes)
fecha_desde_default = fecha_max - timedelta(days=30)
print(f"Cargando datos iniciales ({fecha_desde_default} a {fecha_max})...")
df_ventas = cargar_ventas_por_cliente(fecha_desde_default, fecha_max)
clientes_con_ventas = len(df_ventas[df_ventas['cantidad_total'] > 0])
clientes_sin_ventas = len(df_ventas[df_ventas['cantidad_total'] == 0])
print(f"Cargados {len(df_ventas):,} clientes ({clientes_con_ventas:,} con ventas, {clientes_sin_ventas:,} sin ventas)")

# Crear app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=dmc.styles.ALL)
app.title = "Medallion ETL - Dashboard"

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

# Pre-crear layouts
home_layout = create_home_layout()
ventas_layout = create_ventas_layout(
    fecha_min=fecha_min,
    fecha_max=fecha_max,
    fecha_desde_default=fecha_desde_default,
    lista_genericos=lista_genericos,
    lista_marcas=lista_marcas,
    lista_rutas=lista_rutas,
    lista_preventistas=lista_preventistas
)
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
    if pathname == '/ventas':
        return ventas_layout
    elif pathname == '/ytd':
        return ytd_layout
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
    elif pathname == '/nuevo':
        # Placeholder para nuevo tablero
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Link(
                        html.Span("← Inicio", style={
                            'color': '#aaa',
                            'fontSize': '14px',
                            'textDecoration': 'none',
                            'padding': '8px 15px',
                            'backgroundColor': 'rgba(255,255,255,0.1)',
                            'borderRadius': '5px',
                            'cursor': 'pointer'
                        }),
                        href='/',
                        style={'textDecoration': 'none'}
                    ),
                ], style={'marginBottom': '10px'}),
                html.H1("Nuevo Tablero", style={'margin': '0', 'color': 'white'}),
                html.P("Este tablero está en construcción",
                       style={'margin': '5px 0 0 0', 'color': '#ccc'})
            ], style={
                'backgroundColor': '#1a1a2e',
                'padding': '20px'
            }),
            html.Div([
                html.Div([
                    html.H2("🚧 En Construcción", style={'color': '#666', 'marginBottom': '20px'}),
                    html.P("Este tablero estará disponible próximamente.", style={'color': '#999'}),
                    dcc.Link(
                        html.Button("Volver al Inicio", style={
                            'padding': '15px 30px',
                            'fontSize': '16px',
                            'backgroundColor': '#3498db',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'marginTop': '30px'
                        }),
                        href='/'
                    )
                ], style={
                    'textAlign': 'center',
                    'padding': '100px 20px'
                })
            ], style={
                'backgroundColor': '#f5f7fa',
                'minHeight': 'calc(100vh - 120px)'
            })
        ])
    else:
        # Página de inicio por defecto
        return home_layout


# Importar callbacks (se registran automaticamente)
# Esto debe estar DESPUES de crear app y layout
import callbacks.callbacks  # noqa: E402, F401
import callbacks.ytd_callbacks  # noqa: E402, F401
import callbacks.cliente_callbacks  # noqa: E402, F401


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
