#!/usr/bin/env python3
"""
Dashboard de ventas - Medallion ETL
Visualiza ventas por cliente en un mapa de burbujas interactivo.

Uso:
    python dashboard.py

Acceder en: http://localhost:8050
"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
from datetime import datetime, timedelta

# Imports de módulos locales
from config import SCIPY_AVAILABLE, METRICA_LABELS, COLOR_SCALE_BURBUJAS, COLOR_SCALE_CALOR, SERVER_CONFIG
from data.queries import (
    obtener_genericos, obtener_marcas, obtener_rutas, obtener_preventistas,
    obtener_rango_fechas, cargar_ventas_por_cliente, cargar_ventas_animacion,
    cargar_ventas_por_fecha
)
from utils.visualization import crear_grilla_calor_optimizada, calcular_zonas, COLORES_CALOR

# ==========================================
# APLICACIÓN DASH
# ==========================================

# Obtener rango de fechas
print("Obteniendo rango de fechas...")
fecha_min, fecha_max = obtener_rango_fechas()
print(f"Datos disponibles: {fecha_min} a {fecha_max}")

# Obtener listas para filtros
print("Cargando filtros de producto...")
lista_genericos = obtener_genericos()
lista_marcas = obtener_marcas()
print(f"  - {len(lista_genericos)} genéricos, {len(lista_marcas)} marcas")

print("Cargando filtros de ruta/preventista...")
lista_rutas = obtener_rutas()
lista_preventistas = obtener_preventistas()
print(f"  - {len(lista_rutas)} rutas, {len(lista_preventistas)} preventistas")


# Cargar datos iniciales (último mes)
fecha_desde_default = fecha_max - timedelta(days=30)
print(f"Cargando datos iniciales ({fecha_desde_default} a {fecha_max})...")
df_ventas = cargar_ventas_por_cliente(fecha_desde_default, fecha_max)
clientes_con_ventas = len(df_ventas[df_ventas['cantidad_total'] > 0])
clientes_sin_ventas = len(df_ventas[df_ventas['cantidad_total'] == 0])
print(f"Cargados {len(df_ventas):,} clientes ({clientes_con_ventas:,} con ventas, {clientes_sin_ventas:,} sin ventas)")

# Crear app
app = Dash(__name__)
app.title = "Medallion ETL - Mapa de Ventas"

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🗺️ Mapa de Ventas por Cliente", style={'margin': '0', 'color': 'white'}),
        html.P("Visualización de volumen de ventas geolocalizado",
               style={'margin': '5px 0 0 0', 'color': '#ccc'})
    ], style={
        'backgroundColor': '#1a1a2e',
        'padding': '20px',
        'marginBottom': '10px'
    }),

    # Filtro de fechas
    html.Div([
        html.Div([
            html.Label("📅 Rango de Fechas:", style={'fontWeight': 'bold', 'marginRight': '15px'}),
            dcc.DatePickerRange(
                id='filtro-fechas',
                min_date_allowed=fecha_min,
                max_date_allowed=fecha_max,
                start_date=fecha_desde_default,
                end_date=fecha_max,
                display_format='DD/MM/YYYY'
            ),
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], style={'padding': '15px 20px', 'backgroundColor': '#e8f4f8', 'borderBottom': '2px solid #1a1a2e'}),

    # Fila 1: Filtros de cliente - Primera línea (Canal, Subcanal, Localidad)
    html.Div([
        html.Div([
            html.Label("Canal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-canal',
                options=[],
                value=[],
                multi=True,
                placeholder="Todos los canales",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Subcanal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-subcanal',
                options=[],
                value=[],
                multi=True,
                placeholder="Todos los subcanales",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Localidad:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-localidad',
                options=[],
                value=[],
                multi=True,
                placeholder="Todas las localidades",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#f5f5f5'}),

    # Fila 2: Filtros de cliente - Segunda línea (Lista Precio, Sucursal, Métrica)
    html.Div([
        html.Div([
            html.Label("Lista Precio:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-lista-precio',
                options=[],
                value=[],
                multi=True,
                placeholder="Todas las listas",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Sucursal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-sucursal',
                options=[],
                value=[],
                multi=True,
                placeholder="Todas las sucursales",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Métrica:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-metrica',
                options=[
                    {'label': 'Cantidad (bultos)', 'value': 'cantidad_total'},
                    {'label': 'Facturación ($)', 'value': 'facturacion'},
                    {'label': 'Documentos', 'value': 'cantidad_documentos'}
                ],
                value='cantidad_total',
                clearable=False,
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#f5f5f5'}),

    # Fila 3: Filtros de producto (multi-selección)
    html.Div([
        html.Div([
            html.Label("Genérico:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-generico',
                options=[{'label': g, 'value': g} for g in lista_genericos],
                value=[],
                multi=True,
                placeholder="Todos los genéricos",
                style={'fontSize': '14px'}
            )
        ], style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Marca:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-marca',
                options=[{'label': m, 'value': m} for m in lista_marcas],
                value=[],
                multi=True,
                placeholder="Todas las marcas",
                style={'fontSize': '14px'}
            )
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '15px 20px', 'backgroundColor': '#fff3cd', 'borderBottom': '1px solid #ffc107'}),

    # Fila 4: Filtros de fuerza de ventas, ruta y preventista
    html.Div([
        html.Div([
            html.Label("Fuerza de Ventas:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.RadioItems(
                id='filtro-fuerza-venta',
                options=[
                    {'label': ' Todos', 'value': 'TODOS'},
                    {'label': ' FV1', 'value': 'FV1'},
                    {'label': ' FV4', 'value': 'FV4'}
                ],
                value='TODOS',
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'marginRight': '20px', 'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Ruta:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-ruta',
                options=[{'label': str(r), 'value': r} for r in lista_rutas],
                value=[],
                multi=True,
                placeholder="Todas las rutas",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Preventista:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Dropdown(
                id='filtro-preventista',
                options=[{'label': p, 'value': p} for p in lista_preventistas],
                value=[],
                multi=True,
                placeholder="Todos los preventistas",
                style={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '15px 20px', 'backgroundColor': '#d4edda', 'borderBottom': '1px solid #28a745'}),

    # KPIs
    html.Div(id='kpis-container', style={
        'padding': '20px 40px',
        'display': 'flex',
        'justifyContent': 'space-around',
        'alignItems': 'center',
        'backgroundColor': '#fff',
        'borderBottom': '1px solid #ddd'
    }),

    # Opciones de visualización - Fila 1 (Zonas, Escala, Tipo mapa)
    html.Div([
        html.Div([
            html.Label("Mostrar zonas:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Checklist(
                id='opciones-zonas',
                options=[
                    {'label': ' Zonas por Ruta', 'value': 'ruta'},
                    {'label': ' Zonas por Preventista', 'value': 'preventista'}
                ],
                value=[],
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'marginRight': '20px', 'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Escala:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Checklist(
                id='opcion-escala-log',
                options=[
                    {'label': ' Logarítmica', 'value': 'log'}
                ],
                value=['log'],
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Tipo mapa calor:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.RadioItems(
                id='tipo-mapa-calor',
                options=[
                    {'label': ' Difuso', 'value': 'density'},
                    {'label': ' Grilla', 'value': 'grilla'}
                ],
                value='density',
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'marginRight': '20px', 'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#e7f3ff'}),

    # Opciones de visualización - Fila 2 (Tamaño celda, Radio difuso, Normalización)
    html.Div([
        html.Div([
            html.Label("Tamaño celda:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Slider(
                id='slider-precision',
                min=1,
                max=3,
                step=0.25,
                value=2,
                marks={
                    1: {'label': '10km²', 'style': {'fontSize': '12px'}},
                    2: {'label': '1km²', 'style': {'fontSize': '12px'}},
                    3: {'label': '100m²', 'style': {'fontSize': '12px'}}
                },
                tooltip={'placement': 'bottom', 'always_visible': True}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Radio difuso:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Slider(
                id='slider-radio-difuso',
                min=10,
                max=100,
                step=10,
                value=50,
                marks={
                    10: {'label': '10', 'style': {'fontSize': '12px'}},
                    50: {'label': '50', 'style': {'fontSize': '12px'}},
                    100: {'label': '100', 'style': {'fontSize': '12px'}}
                },
                tooltip={'placement': 'bottom', 'always_visible': True}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Normalización:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.RadioItems(
                id='tipo-normalizacion',
                options=[
                    {'label': ' Normal', 'value': 'normal'},
                    {'label': ' Percentil', 'value': 'percentil'},
                    {'label': ' Limitado', 'value': 'limitado'}
                ],
                value='normal',
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'marginRight': '15px', 'fontSize': '14px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#e7f3ff'}),

    # Opciones de animación
    html.Div([
        html.Div([
            html.Label("Animación temporal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.Checklist(
                id='opcion-animacion',
                options=[
                    {'label': ' Activar animación', 'value': 'animar'}
                ],
                value=[],
                inline=True,
                inputStyle={'marginRight': '8px'},
                labelStyle={'fontSize': '14px'}
            )
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            html.Label("Granularidad:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
            dcc.RadioItems(
                id='granularidad-animacion',
                options=[
                    {'label': ' Día', 'value': 'dia'},
                    {'label': ' Semana', 'value': 'semana'},
                    {'label': ' Mes', 'value': 'mes'}
                ],
                value='semana',
                inline=True,
                inputStyle={'marginRight': '5px'},
                labelStyle={'fontSize': '14px', 'marginRight': '15px'}
            )
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '10px 20px', 'backgroundColor': '#fff3e0', 'borderBottom': '1px solid #007bff'}),

    # Pestañas de mapas
    dcc.Tabs(id='tabs-mapas', value='tab-burbujas', children=[
        dcc.Tab(label='🔵 Mapa de Burbujas', value='tab-burbujas', children=[
            html.Div([
                dcc.Loading(
                    id='loading-mapa',
                    type='circle',
                    children=[dcc.Graph(id='mapa-ventas', style={'height': '87vh'})]
                )
            ], style={'padding': '10px'})
        ]),
        dcc.Tab(label='🌡️ Mapa de Calor', value='tab-calor', children=[
            html.Div([
                dcc.Loading(
                    id='loading-mapa-calor',
                    type='circle',
                    children=[dcc.Graph(id='mapa-calor', style={'height': '87vh'})]
                )
            ], style={'padding': '10px'})
        ]),
        dcc.Tab(label='📊 Tablero Ventas', value='tab-tablero', children=[
            html.Div([
                # Fila 1: Gráficos circulares
                html.Div([
                    html.Div([
                        html.H5("Ventas por Canal", style={'textAlign': 'center', 'marginBottom': '5px'}),
                        dcc.Graph(id='grafico-pie-canal', style={'height': '280px'})
                    ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.H5("Ventas por Lista Precio", style={'textAlign': 'center', 'marginBottom': '5px'}),
                        dcc.Graph(id='grafico-pie-lista', style={'height': '280px'})
                    ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.H5("Ventas por Subcanal", style={'textAlign': 'center', 'marginBottom': '5px'}),
                        dcc.Graph(id='grafico-pie-subcanal', style={'height': '280px'})
                    ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                ], style={'marginBottom': '10px'}),

                # Fila 2: Top 10 Clientes y Ventas por Mes
                html.Div([
                    html.Div([
                        html.H5("Top 10 Clientes", style={'textAlign': 'center', 'marginBottom': '5px'}),
                        dcc.Graph(id='grafico-barras-clientes', style={'height': '300px'})
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.H5("Ventas por Mes", style={'textAlign': 'center', 'marginBottom': '5px'}),
                        dcc.Graph(id='grafico-barras-mensual', style={'height': '300px'})
                    ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                ], style={'marginBottom': '10px'}),

                # Fila 3: Evolución Diaria (ancho completo, cuadrado)
                html.Div([
                    html.H5("Evolución Diaria de Ventas", style={'textAlign': 'center', 'marginBottom': '5px'}),
                    dcc.Graph(id='grafico-linea-tiempo', style={'height': '450px'})
                ]),
            ], style={'padding': '10px', 'backgroundColor': '#fafafa'})
        ]),
        # Mapa 3D comentado - no carga correctamente
        # dcc.Tab(label='🏔️ Mapa 3D', value='tab-3d', children=[
        #     html.Div([
        #         dcc.Loading(
        #             id='loading-mapa-3d',
        #             type='circle',
        #             children=[dcc.Graph(id='mapa-3d', style={'height': '87vh'})]
        #         )
        #     ], style={'padding': '10px'})
        # ]),
    ], style={'marginBottom': '0'}),

], style={'fontFamily': 'Arial, sans-serif'})


# ==========================================
# CALLBACKS
# ==========================================

@callback(
    [Output('filtro-ruta', 'options'),
     Output('filtro-ruta', 'value'),
     Output('filtro-preventista', 'options'),
     Output('filtro-preventista', 'value')],
    [Input('filtro-fuerza-venta', 'value')]
)
def actualizar_rutas_preventistas(fuerza_venta):
    """Actualiza opciones de Ruta y Preventista según la Fuerza de Venta seleccionada."""
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None

    rutas = obtener_rutas(fv)
    preventistas = obtener_preventistas(fv)

    opciones_rutas = [{'label': str(r), 'value': r} for r in rutas]
    opciones_preventistas = [{'label': p, 'value': p} for p in preventistas]

    # Limpiar selección al cambiar FV
    return opciones_rutas, [], opciones_preventistas, []


@callback(
    [Output('filtro-canal', 'options'),
     Output('filtro-subcanal', 'options'),
     Output('filtro-localidad', 'options'),
     Output('filtro-lista-precio', 'options'),
     Output('filtro-sucursal', 'options')],
    [Input('filtro-fechas', 'start_date'),
     Input('filtro-fechas', 'end_date')]
)
def actualizar_filtros(start_date, end_date):
    """Actualiza opciones de filtros cuando cambian las fechas."""
    df = cargar_ventas_por_cliente(start_date, end_date)

    canales = [{'label': c, 'value': c} for c in sorted(df['canal'].unique())]
    subcanales = [{'label': s, 'value': s} for s in sorted(df['subcanal'].unique())]
    localidades = [{'label': l, 'value': l} for l in sorted(df['localidad'].dropna().unique())]
    listas_precio = [{'label': l, 'value': l} for l in sorted(df['lista_precio'].unique())]
    sucursales = [{'label': s, 'value': s} for s in sorted(df['sucursal'].unique())]

    return canales, subcanales, localidades, listas_precio, sucursales


@callback(
    [Output('mapa-ventas', 'figure'),
     Output('kpis-container', 'children')],
    [Input('filtro-fechas', 'start_date'),
     Input('filtro-fechas', 'end_date'),
     Input('filtro-canal', 'value'),
     Input('filtro-subcanal', 'value'),
     Input('filtro-localidad', 'value'),
     Input('filtro-lista-precio', 'value'),
     Input('filtro-sucursal', 'value'),
     Input('filtro-metrica', 'value'),
     Input('filtro-generico', 'value'),
     Input('filtro-marca', 'value'),
     Input('filtro-ruta', 'value'),
     Input('filtro-preventista', 'value'),
     Input('filtro-fuerza-venta', 'value'),
     Input('opciones-zonas', 'value'),
     Input('opcion-animacion', 'value'),
     Input('granularidad-animacion', 'value')]
)
def actualizar_mapa(start_date, end_date, canales, subcanales, localidades, listas_precio, sucursales, metrica, genericos, marcas, rutas, preventistas, fuerza_venta, opciones_zonas, opcion_animacion, granularidad):
    """Actualiza el mapa y KPIs según los filtros."""

    # Convertir fuerza_venta: 'TODOS' -> None
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None
    usar_animacion = 'animar' in (opcion_animacion or [])
    granularidad = granularidad or 'semana'

    # Cargar datos filtrados
    if usar_animacion:
        df = cargar_ventas_animacion(start_date, end_date, genericos, marcas, rutas, preventistas, fv, granularidad)
    else:
        df = cargar_ventas_por_cliente(start_date, end_date, genericos, marcas, rutas, preventistas, fv)

    # Aplicar filtros de cliente en pandas (más eficiente para multi-select)
    if canales and len(canales) > 0:
        df = df[df['canal'].isin(canales)]
    if subcanales and len(subcanales) > 0:
        df = df[df['subcanal'].isin(subcanales)]
    if localidades and len(localidades) > 0:
        df = df[df['localidad'].isin(localidades)]
    if listas_precio and len(listas_precio) > 0:
        df = df[df['lista_precio'].isin(listas_precio)]
    if sucursales and len(sucursales) > 0:
        df = df[df['sucursal'].isin(sucursales)]

    # Labels para métricas
    metrica_labels = {
        'cantidad_total': 'Cantidad (bultos)',
        'facturacion': 'Facturación ($)',
        'cantidad_documentos': 'Documentos'
    }

    # Crear mapa de burbujas
    if len(df) > 0:
        # Centro del mapa
        center_lat = df['latitud'].mean()
        center_lon = df['longitud'].mean()

        # MAPA ANIMADO
        if usar_animacion and 'periodo' in df.columns:
            df_con_ventas = df[df['cantidad_total'] > 0].copy()
            if len(df_con_ventas) > 0:
                # Calcular tamaño normalizado global
                max_val = df_con_ventas[metrica].max()
                df_con_ventas['size'] = 10 + (df_con_ventas[metrica] / max_val * 30)
                df_con_ventas['hover_text'] = df_con_ventas.apply(
                    lambda r: f"<b>{r['razon_social']}</b><br>Localidad: {r['localidad']}<br>{metrica_labels[metrica]}: {r[metrica]:,.0f}", axis=1
                )

                fig = px.scatter_map(
                    df_con_ventas,
                    lat='latitud',
                    lon='longitud',
                    size='size',
                    color=metrica,
                    color_continuous_scale=[[0, 'rgb(70, 130, 180)'], [0.5, 'rgb(255, 165, 0)'], [1, 'rgb(220, 20, 20)']],
                    animation_frame='periodo',
                    hover_name='razon_social',
                    hover_data={'latitud': False, 'longitud': False, 'size': False, 'periodo': True, metrica: ':,.0f'},
                    zoom=8,
                    center=dict(lat=center_lat, lon=center_lon),
                    map_style='open-street-map',
                    opacity=0.8
                )
                fig.update_layout(
                    margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                    coloraxis_colorbar=dict(title=metrica_labels[metrica], tickformat=',.0f')
                )
                # Ajustar velocidad de animación
                fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300
            else:
                fig = px.scatter_map(lat=[-24.8], lon=[-65.4], zoom=7, map_style='open-street-map')
                fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

        # MAPA ESTÁTICO
        else:
            # Separar clientes con y sin ventas
            df_con_ventas = df[df['cantidad_total'] > 0].copy()
            df_sin_ventas = df[df['cantidad_total'] == 0].copy()

            # Crear figura base
            fig = go.Figure()

            # Dibujar zonas si están habilitadas (primero, para que queden debajo)
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df, tipo_zona)
                    for zona in zonas:
                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'],
                            lon=zona['lons'],
                            mode='lines',
                            fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                            hoverinfo='name',
                            showlegend=True
                        ))

            # Primero: clientes SIN ventas (grises, más pequeños, al fondo)
            if len(df_sin_ventas) > 0:
                fig.add_trace(go.Scattermap(
                    lat=df_sin_ventas['latitud'],
                    lon=df_sin_ventas['longitud'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='#aaaaaa',
                        opacity=0.6
                    ),
                    name='Sin ventas',
                    text=df_sin_ventas['razon_social'],
                    hovertemplate='<b>%{text}</b><br>' +
                                  'Localidad: %{customdata[0]}<br>' +
                                  'Subcanal: %{customdata[1]}<br>' +
                                  '<b>Sin ventas en el período</b><extra></extra>',
                    customdata=df_sin_ventas[['localidad', 'subcanal']].values
                ))

            # Segundo: clientes CON ventas (colores según métrica)
            if len(df_con_ventas) > 0:
                # Calcular tamaño de burbujas normalizado
                size_col = df_con_ventas[metrica]
                size_normalized = 10 + (size_col / size_col.max() * 30)

                fig.add_trace(go.Scattermap(
                    lat=df_con_ventas['latitud'],
                    lon=df_con_ventas['longitud'],
                    mode='markers',
                    marker=dict(
                        size=size_normalized,
                        color=df_con_ventas[metrica],
                        colorscale=[[0, 'rgb(70, 130, 180)'], [0.5, 'rgb(255, 165, 0)'], [1, 'rgb(220, 20, 20)']],  # Azul acero → Naranja → Rojo
                        showscale=True,
                        colorbar=dict(
                            title=metrica_labels[metrica],
                            tickformat=',.0f'
                        ),
                        opacity=0.8
                    ),
                    name='Con ventas',
                    text=df_con_ventas['razon_social'],
                    hovertemplate='<b>%{text}</b><br>' +
                                  'Localidad: %{customdata[0]}<br>' +
                                  'Subcanal: %{customdata[1]}<br>' +
                                  'Bultos: %{customdata[2]:,.0f}<br>' +
                                  'Facturación: $%{customdata[3]:,.2f}<br>' +
                                  'Documentos: %{customdata[4]}<extra></extra>',
                    customdata=df_con_ventas[['localidad', 'subcanal', 'cantidad_total', 'facturacion', 'cantidad_documentos']].values
                ))

            fig.update_layout(
                map=dict(
                    style='open-street-map',
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=8
                ),
                margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                showlegend=True,
                legend=dict(
                    yanchor='top',
                    y=0.99,
                    xanchor='left',
                    x=0.01,
                    bgcolor='rgba(255,255,255,0.8)'
                )
            )
    else:
        # Mapa vacío
        fig = px.scatter_map(
            lat=[-24.8], lon=[-65.4],
            zoom=7,
            map_style='open-street-map'
        )
        fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

    # Crear KPIs
    n_con_ventas = len(df[df['cantidad_total'] > 0])
    n_sin_ventas = len(df[df['cantidad_total'] == 0])

    kpis = [
        html.Div([
            html.Span("📍", style={'fontSize': '36px'}),
            html.Div([
                html.Div(f"{len(df):,}", style={'fontSize': '32px', 'fontWeight': 'bold', 'color': '#1a1a2e'}),
                html.Div([
                    html.Span("Clientes ", style={'fontSize': '16px', 'color': '#666'}),
                    html.Span(f"({n_con_ventas:,} activos, ", style={'fontSize': '14px', 'color': '#27ae60'}),
                    html.Span(f"{n_sin_ventas:,} sin ventas)", style={'fontSize': '14px', 'color': '#aaa'})
                ])
            ])
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '15px', 'textAlign': 'center'}),

        html.Div([
            html.Span("📦", style={'fontSize': '36px'}),
            html.Div([
                html.Div(f"{df['cantidad_total'].sum():,.0f}", style={'fontSize': '32px', 'fontWeight': 'bold', 'color': '#e74c3c'}),
                html.Div("Bultos vendidos", style={'fontSize': '16px', 'color': '#666'})
            ])
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '15px', 'textAlign': 'center'}),

        html.Div([
            html.Span("💰", style={'fontSize': '36px'}),
            html.Div([
                html.Div(f"${df['facturacion'].sum():,.0f}", style={'fontSize': '32px', 'fontWeight': 'bold', 'color': '#27ae60'}),
                html.Div("Facturación", style={'fontSize': '16px', 'color': '#666'})
            ])
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '15px', 'textAlign': 'center'}),

        html.Div([
            html.Span("📄", style={'fontSize': '36px'}),
            html.Div([
                html.Div(f"{df['cantidad_documentos'].sum():,.0f}", style={'fontSize': '32px', 'fontWeight': 'bold', 'color': '#3498db'}),
                html.Div("Documentos", style={'fontSize': '16px', 'color': '#666'})
            ])
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '15px', 'textAlign': 'center'}),
    ]

    return fig, kpis


@callback(
    Output('mapa-calor', 'figure'),
    [Input('filtro-fechas', 'start_date'),
     Input('filtro-fechas', 'end_date'),
     Input('filtro-canal', 'value'),
     Input('filtro-subcanal', 'value'),
     Input('filtro-localidad', 'value'),
     Input('filtro-lista-precio', 'value'),
     Input('filtro-sucursal', 'value'),
     Input('filtro-metrica', 'value'),
     Input('filtro-generico', 'value'),
     Input('filtro-marca', 'value'),
     Input('filtro-ruta', 'value'),
     Input('filtro-preventista', 'value'),
     Input('filtro-fuerza-venta', 'value'),
     Input('opciones-zonas', 'value'),
     Input('opcion-escala-log', 'value'),
     Input('slider-precision', 'value'),
     Input('tipo-mapa-calor', 'value'),
     Input('slider-radio-difuso', 'value'),
     Input('tipo-normalizacion', 'value'),
     Input('opcion-animacion', 'value'),
     Input('granularidad-animacion', 'value')]
)
def actualizar_mapa_calor(start_date, end_date, canales, subcanales, localidades, listas_precio, sucursales, metrica, genericos, marcas, rutas, preventistas, fuerza_venta, opciones_zonas, opcion_escala, precision, tipo_mapa, radio_difuso, tipo_normalizacion, opcion_animacion, granularidad):
    """Actualiza el mapa de calor (difuso o grilla)."""

    # Convertir fuerza_venta: 'TODOS' -> None
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None
    usar_animacion = 'animar' in (opcion_animacion or [])
    granularidad = granularidad or 'semana'

    # Cargar datos filtrados
    if usar_animacion:
        df = cargar_ventas_animacion(start_date, end_date, genericos, marcas, rutas, preventistas, fv, granularidad)
    else:
        df = cargar_ventas_por_cliente(start_date, end_date, genericos, marcas, rutas, preventistas, fv)

    # Aplicar filtros de cliente
    if canales and len(canales) > 0:
        df = df[df['canal'].isin(canales)]
    if subcanales and len(subcanales) > 0:
        df = df[df['subcanal'].isin(subcanales)]
    if localidades and len(localidades) > 0:
        df = df[df['localidad'].isin(localidades)]
    if listas_precio and len(listas_precio) > 0:
        df = df[df['lista_precio'].isin(listas_precio)]
    if sucursales and len(sucursales) > 0:
        df = df[df['sucursal'].isin(sucursales)]

    # Solo clientes con ventas para el mapa de calor
    df_con_ventas = df[df['cantidad_total'] > 0].copy()

    # Labels para métricas
    metrica_labels = {
        'cantidad_total': 'Cantidad (bultos)',
        'facturacion': 'Facturación ($)',
        'cantidad_documentos': 'Documentos'
    }

    # Determinar si usar escala logarítmica
    usar_log = opcion_escala and 'log' in opcion_escala
    escala_texto = " (log)" if usar_log else ""

    # Calcular tamaño de celda según precision (aprox en grados -> metros)
    precision = precision or 2  # default
    cell_degrees = 10 ** -precision
    cell_meters = cell_degrees * 111000  # ~111km por grado
    if cell_meters >= 1000:
        tamanio_celda_texto = f'{cell_meters/1000:.1f}km²'
    else:
        tamanio_celda_texto = f'{cell_meters:.0f}m²'
    tipo_mapa = tipo_mapa or 'density'
    radio_difuso = radio_difuso or 50  # default
    tipo_normalizacion = tipo_normalizacion or 'normal'

    if len(df_con_ventas) > 0:
        # Centro del mapa
        center_lat = df_con_ventas['latitud'].mean()
        center_lon = df_con_ventas['longitud'].mean()

        # MAPA DE CALOR ANIMADO
        if usar_animacion and 'periodo' in df_con_ventas.columns:
            # Usar density_map con animation_frame
            df_con_ventas['metrica_z'] = df_con_ventas[metrica]
            if usar_log:
                df_con_ventas['metrica_z'] = np.log1p(df_con_ventas['metrica_z'])

            fig = px.density_map(
                df_con_ventas,
                lat='latitud',
                lon='longitud',
                z='metrica_z',
                radius=radio_difuso,
                opacity=0.5,
                animation_frame='periodo',
                center=dict(lat=center_lat, lon=center_lon),
                zoom=8,
                map_style='open-street-map',
                color_continuous_scale=[
                    [0.0, 'rgb(0, 0, 150)'],
                    [0.15, 'rgb(0, 100, 255)'],
                    [0.3, 'rgb(0, 200, 255)'],
                    [0.45, 'rgb(0, 255, 150)'],
                    [0.55, 'rgb(200, 255, 0)'],
                    [0.7, 'rgb(255, 200, 0)'],
                    [0.85, 'rgb(255, 100, 0)'],
                    [1.0, 'rgb(200, 0, 0)']
                ]
            )
            fig.update_layout(
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                coloraxis_colorbar=dict(title=metrica_labels[metrica] + escala_texto, tickformat=',.0f')
            )
            # Ajustar velocidad de animación
            if hasattr(fig.layout, 'updatemenus') and fig.layout.updatemenus:
                fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300

        elif tipo_mapa == 'density':
            # === MAPA DIFUSO (density_map) ===

            # Aplicar normalización según el tipo seleccionado
            if tipo_normalizacion == 'percentil':
                # Convertir valores a percentiles (0-100)
                df_con_ventas['metrica_z'] = df_con_ventas[metrica].rank(pct=True) * 100
                norm_texto = " [percentil]"
                range_color = [0, 100]
            elif tipo_normalizacion == 'limitado':
                # Limitar al percentil 95 para evitar saturación por outliers
                p95 = df_con_ventas[metrica].quantile(0.95)
                df_con_ventas['metrica_z'] = df_con_ventas[metrica].clip(upper=p95)
                norm_texto = " [p95]"
                range_color = [0, p95]
            else:
                # Normal
                df_con_ventas['metrica_z'] = df_con_ventas[metrica]
                norm_texto = ""
                range_color = None

            # Aplicar escala logarítmica si está activada (después de normalización)
            if usar_log and tipo_normalizacion == 'normal':
                df_con_ventas['metrica_z'] = np.log1p(df_con_ventas['metrica_z'])

            fig = px.density_map(
                df_con_ventas,
                lat='latitud',
                lon='longitud',
                z='metrica_z',
                radius=radio_difuso,
                opacity=0.5,
                center=dict(lat=center_lat, lon=center_lon),
                zoom=8,
                map_style='open-street-map',
                color_continuous_scale=[
                    [0.0, 'rgb(0, 0, 150)'],
                    [0.15, 'rgb(0, 100, 255)'],
                    [0.3, 'rgb(0, 200, 255)'],
                    [0.45, 'rgb(0, 255, 150)'],
                    [0.55, 'rgb(200, 255, 0)'],
                    [0.7, 'rgb(255, 200, 0)'],
                    [0.85, 'rgb(255, 100, 0)'],
                    [1.0, 'rgb(200, 0, 0)']
                ],
                range_color=range_color,
                hover_data={
                    'razon_social': True,
                    'localidad': True,
                    'cantidad_total': ':.0f',
                    'facturacion': ':,.2f'
                }
            )

            fig.update_layout(
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                coloraxis_colorbar=dict(
                    title=metrica_labels[metrica] + escala_texto + norm_texto,
                    tickformat=',.0f'
                ),
                title=dict(
                    text=f'🌡️ Mapa de Calor Difuso - {metrica_labels[metrica]}{escala_texto}{norm_texto}',
                    x=0.5,
                    xanchor='center'
                )
            )

            # Dibujar zonas si están habilitadas
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df, tipo_zona)
                    for zona in zonas:
                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'],
                            lon=zona['lons'],
                            mode='lines',
                            fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                            hoverinfo='name',
                            showlegend=True
                        ))

        else:
            # === MAPA POR GRILLA ===
            grupos = crear_grilla_calor_optimizada(df_con_ventas, metrica, precision=precision, usar_log=usar_log, n_grupos=8)

            fig = go.Figure()

            # Dibujar cada grupo de celdas como un solo trace
            for grupo_id, grupo in grupos.items():
                color = COLORES_CALOR[grupo_id]
                fig.add_trace(go.Scattermap(
                    lat=grupo['lats'],
                    lon=grupo['lons'],
                    mode='lines',
                    fill='toself',
                    fillcolor=color,
                    line=dict(color=color, width=0),
                    name=f"Nivel {grupo_id + 1}",
                    hoverinfo='text',
                    hovertext=f"Celdas: {grupo['n_celdas']}<br>Clientes: {grupo['total_clientes']:,}",
                    showlegend=False
                ))

            # Agregar colorbar ficticio para mostrar la escala
            # Usamos un scatter invisible con colorscale
            val_min = df_con_ventas[metrica].min()
            val_max = df_con_ventas[metrica].max()
            fig.add_trace(go.Scattermap(
                lat=[None],
                lon=[None],
                mode='markers',
                marker=dict(
                    size=0,
                    color=[val_min, val_max],
                    colorscale=[
                        [0.0, 'rgb(0, 50, 150)'],
                        [0.14, 'rgb(0, 100, 255)'],
                        [0.28, 'rgb(0, 200, 255)'],
                        [0.42, 'rgb(0, 255, 150)'],
                        [0.57, 'rgb(200, 255, 0)'],
                        [0.71, 'rgb(255, 200, 0)'],
                        [0.85, 'rgb(255, 100, 0)'],
                        [1.0, 'rgb(200, 0, 0)']
                    ],
                    showscale=True,
                    colorbar=dict(
                        title=metrica_labels[metrica] + escala_texto,
                        tickformat=',.0f',
                        x=1.0,
                        xpad=10
                    )
                ),
                showlegend=False,
                hoverinfo='skip'
            ))

            # Dibujar zonas si están habilitadas
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df, tipo_zona)
                    for zona in zonas:
                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'],
                            lon=zona['lons'],
                            mode='lines',
                            fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                            hoverinfo='name',
                            showlegend=True
                        ))

            fig.update_layout(
                map=dict(
                    style='open-street-map',
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=8
                ),
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                title=dict(
                    text=f'🌡️ Mapa de Calor Grilla - {metrica_labels[metrica]}{escala_texto} (celdas {tamanio_celda_texto})',
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=True if opciones_zonas else False
            )
    else:
        # Mapa vacío
        fig = go.Figure()
        fig.add_trace(go.Scattermap(
            lat=[-24.8],
            lon=[-65.4],
            mode='markers',
            marker=dict(size=1),
            showlegend=False
        ))
        fig.update_layout(
            map=dict(
                style='open-street-map',
                center=dict(lat=-24.8, lon=-65.4),
                zoom=7
            ),
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0}
        )

    return fig


# Mapa 3D comentado - no carga correctamente
# @callback(
#     Output('mapa-3d', 'figure'),
#     [Input('filtro-fechas', 'start_date'),
#      Input('filtro-fechas', 'end_date'),
#      Input('filtro-canal', 'value'),
#      Input('filtro-subcanal', 'value'),
#      Input('filtro-localidad', 'value'),
#      Input('filtro-metrica', 'value'),
#      Input('filtro-generico', 'value'),
#      Input('filtro-marca', 'value'),
#      Input('filtro-ruta', 'value'),
#      Input('filtro-preventista', 'value')]
# )
# def actualizar_mapa_3d(start_date, end_date, canales, subcanales, localidades, metrica, genericos, marcas, rutas, preventistas):
#     """Actualiza el mapa 3D donde la altura representa las ventas."""
#
#     # Cargar datos filtrados
#     df = cargar_ventas_por_cliente(start_date, end_date, genericos, marcas, rutas, preventistas)
#
#     # Aplicar filtros de cliente
#     if canales and len(canales) > 0:
#         df = df[df['canal'].isin(canales)]
#     if subcanales and len(subcanales) > 0:
#         df = df[df['subcanal'].isin(subcanales)]
#     if localidades and len(localidades) > 0:
#         df = df[df['localidad'].isin(localidades)]
#
#     # Solo clientes con ventas
#     df_con_ventas = df[df['cantidad_total'] > 0].copy()
#
#     # Labels para métricas
#     metrica_labels = {
#         'cantidad_total': 'Cantidad (bultos)',
#         'facturacion': 'Facturación ($)',
#         'cantidad_documentos': 'Documentos'
#     }
#
#     if len(df_con_ventas) > 0:
#         # Normalizar coordenadas para visualización 3D
#         # Centrar en 0,0 y escalar
#         lat_center = df_con_ventas['latitud'].mean()
#         lon_center = df_con_ventas['longitud'].mean()
#
#         df_con_ventas['x'] = (df_con_ventas['longitud'] - lon_center) * 100
#         df_con_ventas['y'] = (df_con_ventas['latitud'] - lat_center) * 100
#
#         # Altura basada en la métrica (escala logarítmica para mejor visualización)
#         df_con_ventas['z'] = np.log1p(df_con_ventas[metrica])
#         # Normalizar altura
#         z_max = df_con_ventas['z'].max()
#         if z_max > 0:
#             df_con_ventas['z'] = df_con_ventas['z'] / z_max * 50
#
#         # Crear gráfico 3D
#         fig = go.Figure(data=[
#             go.Scatter3d(
#                 x=df_con_ventas['x'],
#                 y=df_con_ventas['y'],
#                 z=df_con_ventas['z'],
#                 mode='markers',
#                 marker=dict(
#                     size=6,
#                     color=df_con_ventas[metrica],
#                     colorscale='RdYlBu_r',
#                     showscale=True,
#                     colorbar=dict(
#                         title=metrica_labels[metrica],
#                         tickformat=',.0f'
#                     ),
#                     opacity=0.8
#                 ),
#                 text=df_con_ventas['razon_social'],
#                 hovertemplate='<b>%{text}</b><br>' +
#                               f'{metrica_labels[metrica]}: ' + '%{marker.color:,.0f}<br>' +
#                               '<extra></extra>'
#             )
#         ])
#
#         # También agregar "columnas" desde el suelo hasta cada punto
#         for _, row in df_con_ventas.iterrows():
#             fig.add_trace(go.Scatter3d(
#                 x=[row['x'], row['x']],
#                 y=[row['y'], row['y']],
#                 z=[0, row['z']],
#                 mode='lines',
#                 line=dict(color='rgba(100,100,100,0.3)', width=2),
#                 showlegend=False,
#                 hoverinfo='skip'
#             ))
#
#         fig.update_layout(
#             scene=dict(
#                 xaxis_title='Longitud',
#                 yaxis_title='Latitud',
#                 zaxis_title=metrica_labels[metrica],
#                 camera=dict(
#                     eye=dict(x=1.5, y=1.5, z=1.2)
#                 ),
#                 aspectmode='manual',
#                 aspectratio=dict(x=1, y=1, z=0.5)
#             ),
#             margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
#             title=dict(
#                 text=f'🏔️ Visualización 3D - {metrica_labels[metrica]}',
#                 x=0.5,
#                 xanchor='center'
#             )
#         )
#     else:
#         # Gráfico vacío
#         fig = go.Figure()
#         fig.update_layout(
#             scene=dict(
#                 xaxis_title='Longitud',
#                 yaxis_title='Latitud',
#                 zaxis_title='Ventas'
#             ),
#             margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
#             title='Sin datos para el período seleccionado'
#         )
#
#     return fig


@callback(
    [Output('grafico-pie-canal', 'figure'),
     Output('grafico-pie-lista', 'figure'),
     Output('grafico-pie-subcanal', 'figure'),
     Output('grafico-barras-clientes', 'figure'),
     Output('grafico-barras-mensual', 'figure'),
     Output('grafico-linea-tiempo', 'figure')],
    [Input('filtro-fechas', 'start_date'),
     Input('filtro-fechas', 'end_date'),
     Input('filtro-canal', 'value'),
     Input('filtro-subcanal', 'value'),
     Input('filtro-localidad', 'value'),
     Input('filtro-lista-precio', 'value'),
     Input('filtro-sucursal', 'value'),
     Input('filtro-metrica', 'value'),
     Input('filtro-generico', 'value'),
     Input('filtro-marca', 'value'),
     Input('filtro-ruta', 'value'),
     Input('filtro-preventista', 'value'),
     Input('filtro-fuerza-venta', 'value')]
)
def actualizar_tablero(start_date, end_date, canales, subcanales, localidades, listas_precio, sucursales, metrica, genericos, marcas, rutas, preventistas, fuerza_venta):
    """Actualiza todos los gráficos del tablero de ventas."""

    # Convertir fuerza_venta: 'TODOS' -> None
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None

    # Cargar datos
    df = cargar_ventas_por_cliente(start_date, end_date, genericos, marcas, rutas, preventistas, fv)

    # Aplicar filtros
    if canales and len(canales) > 0:
        df = df[df['canal'].isin(canales)]
    if subcanales and len(subcanales) > 0:
        df = df[df['subcanal'].isin(subcanales)]
    if localidades and len(localidades) > 0:
        df = df[df['localidad'].isin(localidades)]
    if listas_precio and len(listas_precio) > 0:
        df = df[df['lista_precio'].isin(listas_precio)]
    if sucursales and len(sucursales) > 0:
        df = df[df['sucursal'].isin(sucursales)]

    # Solo clientes con ventas
    df = df[df['cantidad_total'] > 0]

    # Labels para métricas
    metrica_labels = {
        'cantidad_total': 'Cantidad',
        'facturacion': 'Facturación',
        'cantidad_documentos': 'Documentos'
    }

    # Colores consistentes
    colores = px.colors.qualitative.Set2

    # 1. Gráfico circular - Ventas por Canal
    if len(df) > 0:
        df_canal = df.groupby('canal')[metrica].sum().reset_index()
        df_canal = df_canal.sort_values(metrica, ascending=False)
        fig_pie_canal = px.pie(
            df_canal, values=metrica, names='canal',
            color_discrete_sequence=colores,
            hole=0.4
        )
        fig_pie_canal.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie_canal.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    else:
        fig_pie_canal = px.pie(values=[1], names=['Sin datos'])
        fig_pie_canal.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    # 2. Gráfico circular - Ventas por Lista Precio
    if len(df) > 0:
        df_lista = df.groupby('lista_precio')[metrica].sum().reset_index()
        df_lista = df_lista.sort_values(metrica, ascending=False).head(8)  # Top 8
        fig_pie_lista = px.pie(
            df_lista, values=metrica, names='lista_precio',
            color_discrete_sequence=colores,
            hole=0.4
        )
        fig_pie_lista.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie_lista.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    else:
        fig_pie_lista = px.pie(values=[1], names=['Sin datos'])
        fig_pie_lista.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    # 3. Gráfico circular - Ventas por Subcanal
    if len(df) > 0:
        df_subcanal = df.groupby('subcanal')[metrica].sum().reset_index()
        df_subcanal = df_subcanal.sort_values(metrica, ascending=False).head(8)  # Top 8
        fig_pie_subcanal = px.pie(
            df_subcanal, values=metrica, names='subcanal',
            color_discrete_sequence=colores,
            hole=0.4
        )
        fig_pie_subcanal.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie_subcanal.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    else:
        fig_pie_subcanal = px.pie(values=[1], names=['Sin datos'])
        fig_pie_subcanal.update_layout(margin=dict(t=10, b=10, l=10, r=10))

    # 4. Gráfico de barras - Top 10 Clientes
    if len(df) > 0:
        df_top = df.nlargest(10, metrica)[['razon_social', metrica]].copy()
        df_top['razon_social'] = df_top['razon_social'].str[:25]  # Truncar nombres largos
        fig_barras_clientes = px.bar(
            df_top, x=metrica, y='razon_social',
            orientation='h',
            color=metrica,
            color_continuous_scale='Blues'
        )
        fig_barras_clientes.update_layout(
            margin=dict(t=10, b=30, l=10, r=10),
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title=metrica_labels[metrica],
            yaxis_title='',
            coloraxis_showscale=False
        )
    else:
        fig_barras_clientes = px.bar(x=[0], y=['Sin datos'])
        fig_barras_clientes.update_layout(margin=dict(t=10, b=30, l=10, r=10))

    # 5. Gráfico de barras - Ventas por Mes
    df_fecha = cargar_ventas_por_fecha(start_date, end_date, canales, subcanales, localidades, listas_precio, sucursales, genericos, marcas, rutas, preventistas)
    if len(df_fecha) > 0:
        df_fecha['mes'] = pd.to_datetime(df_fecha['fecha']).dt.to_period('M').astype(str)
        df_mensual = df_fecha.groupby('mes')[metrica].sum().reset_index()
        fig_barras_mensual = px.bar(
            df_mensual, x='mes', y=metrica,
            color=metrica,
            color_continuous_scale='Greens'
        )
        fig_barras_mensual.update_layout(
            margin=dict(t=10, b=30, l=10, r=10),
            xaxis_title='Mes',
            yaxis_title=metrica_labels[metrica],
            coloraxis_showscale=False
        )
    else:
        fig_barras_mensual = px.bar(x=['Sin datos'], y=[0])
        fig_barras_mensual.update_layout(margin=dict(t=10, b=30, l=10, r=10))

    # 6. Línea de tiempo - Evolución diaria
    if len(df_fecha) > 0:
        fig_linea = go.Figure()
        fig_linea.add_trace(go.Scatter(
            x=df_fecha['fecha'],
            y=df_fecha[metrica],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#3498db', width=2),
            fillcolor='rgba(52, 152, 219, 0.3)',
            name=metrica_labels[metrica]
        ))
        # Agregar línea de tendencia (promedio móvil 7 días)
        fig_linea.add_trace(go.Scatter(
            x=df_fecha['fecha'],
            y=df_fecha[metrica].rolling(window=7, min_periods=1).mean(),
            mode='lines',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            name='Tendencia (7 días)'
        ))
        fig_linea.update_layout(
            margin=dict(t=10, b=30, l=50, r=10),
            xaxis_title='',
            yaxis_title=metrica_labels[metrica],
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        fig_linea.update_yaxes(tickformat=',.0f')
    else:
        fig_linea = go.Figure()
        fig_linea.update_layout(margin=dict(t=10, b=30, l=50, r=10))

    return fig_pie_canal, fig_pie_lista, fig_pie_subcanal, fig_barras_clientes, fig_barras_mensual, fig_linea


# Callback de gráfico de evolución removido - ahora está en el tablero
# @callback(
#     Output('grafico-evolucion', 'figure'),
#     [Input('filtro-fechas', 'start_date'),
#      Input('filtro-fechas', 'end_date'),
#      Input('filtro-canal', 'value'),
#      Input('filtro-subcanal', 'value'),
#      Input('filtro-localidad', 'value'),
#      Input('filtro-lista-precio', 'value'),
#      Input('filtro-metrica', 'value'),
#      Input('filtro-generico', 'value'),
#      Input('filtro-marca', 'value'),
#      Input('filtro-ruta', 'value'),
#      Input('filtro-preventista', 'value')]
# )
def _actualizar_grafico_deprecated(start_date, end_date, canales, subcanales, localidades, listas_precio, metrica, genericos, marcas, rutas, preventistas):
    """DEPRECATED - Actualiza el gráfico de evolución temporal."""

    # Cargar datos por fecha con filtros
    df = cargar_ventas_por_fecha(start_date, end_date, canales, subcanales, localidades, listas_precio, None, genericos, marcas, rutas, preventistas)

    if len(df) == 0:
        # Gráfico vacío
        fig = px.line(title="Sin datos para el período seleccionado")
        fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title="",
            margin={'r': 10, 't': 40, 'l': 10, 'b': 40}
        )
        return fig

    # Labels para métricas
    metrica_labels = {
        'cantidad_total': 'Bultos',
        'facturacion': 'Facturación ($)',
        'cantidad_documentos': 'Documentos'
    }

    # Colores por métrica
    metrica_colores = {
        'cantidad_total': '#e74c3c',
        'facturacion': '#27ae60',
        'cantidad_documentos': '#3498db'
    }

    # Crear gráfico de área
    fig = px.area(
        df,
        x='fecha',
        y=metrica,
        color_discrete_sequence=[metrica_colores[metrica]],
        labels={metrica: metrica_labels[metrica], 'fecha': 'Fecha'}
    )

    # Agregar línea de tendencia
    fig.add_scatter(
        x=df['fecha'],
        y=df[metrica].rolling(window=7, min_periods=1).mean(),
        mode='lines',
        name='Promedio móvil (7 días)',
        line=dict(color='#1a1a2e', width=2, dash='dot')
    )

    fig.update_layout(
        margin={'r': 10, 't': 10, 'l': 10, 'b': 40},
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis_title="",
        yaxis_title=metrica_labels[metrica],
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat=',.0f')

    return fig


# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("DASHBOARD MEDALLION ETL - MAPA DE VENTAS")
    print("="*50)
    print("Acceder localmente: http://localhost:8050")
    print("Acceder en red:     http://<tu-ip>:8050")
    print("Presionar Ctrl+C para detener")
    print("="*50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=8050)
