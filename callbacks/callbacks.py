"""
Callbacks del dashboard.
Define todas las interacciones y actualizaciones de la UI.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, clientside_callback, Output, Input, State, html, ctx, no_update
import dash_mantine_components as dmc

from data.queries import (
    obtener_rutas, obtener_preventistas, obtener_marcas, obtener_anios_disponibles,
    cargar_ventas_por_cliente, cargar_ventas_animacion, cargar_ventas_por_fecha,
    cargar_ventas_por_cliente_generico, buscar_clientes,
)
from utils.visualization import crear_grilla_calor_optimizada, calcular_zonas, COLORES_CALOR
from config import METRICA_LABELS, DARK


# =============================================================================
# CALLBACK DRAWER DE FILTROS
# =============================================================================

@callback(
    Output('drawer-filtros', 'opened'),
    Input('btn-toggle-filtros', 'n_clicks'),
    State('drawer-filtros', 'opened'),
    prevent_initial_call=True
)
def toggle_drawer(n_clicks, opened):
    return not opened


# =============================================================================
# CALLBACKS DE FILTROS
# =============================================================================

@callback(
    [Output('filtro-ruta', 'data'),
     Output('filtro-ruta', 'value'),
     Output('filtro-preventista', 'data'),
     Output('filtro-preventista', 'value')],
    [Input('filtro-fuerza-venta', 'value')]
)
def actualizar_rutas_preventistas(fuerza_venta):
    """Actualiza opciones de Ruta y Preventista segun la Fuerza de Venta seleccionada."""
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None

    opciones_rutas = obtener_rutas(fv)  # ya retorna [{"label": ..., "value": "suc|ruta"}]
    preventistas = obtener_preventistas(fv)
    opciones_preventistas = [{'label': p, 'value': p} for p in preventistas]

    return opciones_rutas, [], opciones_preventistas, []


@callback(
    [Output('filtro-canal', 'data'),
     Output('filtro-subcanal', 'data'),
     Output('filtro-localidad', 'data'),
     Output('filtro-lista-precio', 'data'),
     Output('filtro-sucursal', 'data')],
    [Input('filtro-fechas', 'value')]
)
def actualizar_filtros(fechas_value):
    """Actualiza opciones de filtros cuando cambian las fechas."""
    start_date, end_date = (fechas_value or [None, None])[:2]
    df = cargar_ventas_por_cliente(start_date, end_date)

    canales = [{'label': c, 'value': c} for c in sorted(df['canal'].unique())]
    subcanales = [{'label': s, 'value': s} for s in sorted(df['subcanal'].unique())]
    localidades = [{'label': l, 'value': l} for l in sorted(df['localidad'].dropna().unique())]
    listas_precio = [{'label': l, 'value': l} for l in sorted(df['lista_precio'].unique())]
    sucursales = [{'label': s, 'value': s} for s in sorted(df['sucursal'].unique())]

    return canales, subcanales, localidades, listas_precio, sucursales


@callback(
    [Output('filtro-marca', 'data'),
     Output('filtro-marca', 'value')],
    [Input('filtro-generico', 'value')],
    prevent_initial_call=True
)
def actualizar_marcas_por_generico(genericos_seleccionados):
    """Actualiza las opciones de marca según los genéricos seleccionados (filtro en cascada)."""
    marcas = obtener_marcas(genericos_seleccionados)
    opciones_marcas = [{'label': m, 'value': m} for m in marcas]
    # Limpiar selección actual de marcas cuando cambia el genérico
    return opciones_marcas, []


@callback(
    Output('filtro-sucursal', 'value'),
    [Input('filtro-tipo-sucursal', 'value'),
     Input('filtro-sucursal', 'data')],
    prevent_initial_call=True
)
def actualizar_sucursal_por_tipo(tipo_sucursal, opciones_sucursales):
    """Auto-filtra sucursales según el tipo seleccionado."""
    if not opciones_sucursales:
        return []

    # Extraer valores de las opciones (data puede ser lista de strings o dicts)
    todas_sucursales = [
        opt['value'] if isinstance(opt, dict) else opt
        for opt in opciones_sucursales
    ]

    if tipo_sucursal == 'TODAS':
        # No filtrar, mostrar todas (valor vacío = sin filtro)
        return []
    elif tipo_sucursal == 'SUCURSALES':
        # Solo sucursales (excluir Casa Central)
        return [s for s in todas_sucursales if s != 'CASA CENTRAL' and 'SUCURSAL' in s.upper()]
    elif tipo_sucursal == 'CASA_CENTRAL':
        # Solo Casa Central
        return [s for s in todas_sucursales if s == 'CASA CENTRAL']

    return []


# =============================================================================
# HELPER: Contenido de badge de zona para HoverCard
# =============================================================================

def _build_zona_badge_content(nombre, n_total, resumen, total_act, total_ant, color_borde):
    """Construye el contenido HTML del HoverCard para una zona/ruta."""
    header_style = {
        'padding': '8px 12px',
        'backgroundColor': color_borde.replace('0.8', '0.25'),
        'borderBottom': f'1px solid {DARK["border"]}',
    }
    section_title = {
        'fontSize': '11px', 'fontWeight': '700', 'color': DARK['accent_blue'],
        'padding': '6px 12px 2px', 'textTransform': 'uppercase',
    }
    row_style = {
        'display': 'flex', 'justifyContent': 'space-between',
        'padding': '2px 12px', 'fontSize': '12px', 'color': DARK['text'],
    }
    total_row = {
        'display': 'flex', 'justifyContent': 'space-between',
        'padding': '4px 12px', 'fontSize': '12px', 'fontWeight': '700',
        'color': DARK['text'], 'borderTop': f'1px solid {DARK["border"]}',
    }

    content = [
        # Header
        html.Div([
            html.Div(nombre, style={'fontWeight': '700', 'fontSize': '13px', 'color': DARK['text']}),
            html.Div(f"{n_total} clientes", style={'fontSize': '11px', 'color': DARK['text_secondary']}),
        ], style=header_style),
        # Sección Ventas
        html.Div('Ventas (bultos) — MAct / MAnt', style=section_title),
    ]
    for gen, row in resumen.iterrows():
        content.append(html.Div([
            html.Span(gen, style={'flex': '1'}),
            html.Span(f"{row['bultos_act']:,.0f} / {row['bultos_ant']:,.0f}",
                       style={'fontWeight': '600', 'textAlign': 'right'}),
        ], style=row_style))
    content.append(html.Div([
        html.Span('Total', style={'flex': '1'}),
        html.Span(f"{total_act:,.0f} / {total_ant:,.0f}", style={'textAlign': 'right'}),
    ], style=total_row))

    # Sección Clientes compradores
    content.append(html.Div(f'Compradores — MAct / MAnt — Total: {n_total}', style=section_title))
    for gen, row in resumen.iterrows():
        c_act = int(row['cli_act'])
        c_ant = int(row['cli_ant'])
        content.append(html.Div([
            html.Span(gen, style={'flex': '1'}),
            html.Span(f"{c_act} / {c_ant}",
                       style={'fontWeight': '600', 'textAlign': 'right'}),
        ], style=row_style))

    return content


# =============================================================================
# CALLBACK MAPA DE BURBUJAS
# =============================================================================

@callback(
    [Output('mapa-ventas', 'figure'),
     Output('route-badges-overlay', 'children')],
    [Input('filtro-fechas', 'value'),
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
     Input('opcion-animacion', 'checked'),
     Input('granularidad-animacion', 'value'),
     Input('busqueda-cliente-store', 'data')]
)
def actualizar_mapa(fechas_value, canales, subcanales, localidades, listas_precio,
                    sucursales, metrica, genericos, marcas, rutas, preventistas,
                    fuerza_venta, opciones_zonas, opcion_animacion, granularidad,
                    cliente_buscado):
    """Actualiza el mapa y KPIs segun los filtros."""
    route_badges = []

    start_date, end_date = (fechas_value or [None, None])[:2]
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None
    usar_animacion = opcion_animacion or False
    granularidad = granularidad or 'semana'

    # Cargar datos
    if usar_animacion:
        df = cargar_ventas_animacion(start_date, end_date, genericos, marcas, rutas, preventistas, fv, granularidad)
    else:
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

    metrica_labels = METRICA_LABELS

    if len(df) > 0:
        # Filtrar clientes con coordenadas válidas SOLO para visualización del mapa
        df_mapa = df[
            (df['latitud'].notna()) &
            (df['longitud'].notna()) &
            (df['latitud'] != 0) &
            (df['longitud'] != 0)
        ].copy()

        # Calcular centro del mapa solo con coordenadas válidas
        if len(df_mapa) > 0:
            center_lat = df_mapa['latitud'].mean()
            center_lon = df_mapa['longitud'].mean()
        else:
            center_lat = -24.8
            center_lon = -65.4

        # Override centro/zoom si se buscó un cliente
        zoom_level = 8
        if (ctx.triggered_id == 'busqueda-cliente-store'
                and cliente_buscado and cliente_buscado.get('lat')):
            center_lat = cliente_buscado['lat']
            center_lon = cliente_buscado['lon']
            zoom_level = cliente_buscado.get('zoom', 16)

        # MAPA ANIMADO
        if usar_animacion and 'periodo' in df.columns:
            df_con_ventas = df_mapa[df_mapa['cantidad_total'] > 0].copy()
            if len(df_con_ventas) > 0:
                # Escala fija 0-15: tamaño y color
                df_con_ventas['size'] = 5 + (df_con_ventas[metrica].clip(upper=15) / 15 * 15)

                fig = px.scatter_map(
                    df_con_ventas,
                    lat='latitud', lon='longitud',
                    size='size', color=metrica,
                    color_continuous_scale=[[0, 'rgb(30, 80, 180)'], [0.35, 'rgb(0, 180, 220)'], [0.65, 'rgb(80, 200, 80)'], [1, 'rgb(240, 220, 0)']],
                    range_color=[0, 15],
                    animation_frame='periodo',
                    hover_name='razon_social',
                    hover_data={'latitud': False, 'longitud': False, 'size': False, 'periodo': True, metrica: ':,.0f'},
                    zoom=zoom_level, center=dict(lat=center_lat, lon=center_lon),
                    map_style='open-street-map', opacity=0.8
                )
                fig.update_layout(
                    margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                    coloraxis_colorbar=dict(title=metrica_labels[metrica], tickformat=',.0f'),
                    hoverlabel=dict(font=dict(family='monospace'))
                )
                fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300
            else:
                fig = px.scatter_map(lat=[-24.8], lon=[-65.4], zoom=7, map_style='open-street-map')
                fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

        # MAPA ESTATICO
        else:
            # Usar df_mapa (solo coordenadas válidas) para visualización
            df_con_ventas = df_mapa[df_mapa['cantidad_total'] > 0].copy()
            df_sin_ventas = df_mapa[df_mapa['cantidad_total'] == 0].copy()

            # Cargar desglose por genérico para hover (mes actual y anterior)
            df_generico = cargar_ventas_por_cliente_generico(
                genericos, marcas, rutas, preventistas, fv
            )
            # Formatear desglose como texto por cliente (MAct / MAnt)
            if len(df_generico) > 0:
                def _fmt_generico(grupo):
                    lines = ['<b>Genérico — MAct | MAnt</b>']
                    for _, row in grupo.iterrows():
                        act = f"{row['bultos_act']:,.0f}" if row['bultos_act'] else '0'
                        ant = f"{row['bultos_ant']:,.0f}" if row['bultos_ant'] else '0'
                        lines.append(f"{row['generico']}: <b>{act}</b> | {ant}")
                    return '<br>'.join(lines)
                desglose_map = df_generico.groupby('id_cliente').apply(_fmt_generico).to_dict()
            else:
                desglose_map = {}
            df_con_ventas['desglose_generico'] = df_con_ventas['id_cliente'].map(desglose_map).fillna('')

            fig = go.Figure()

            # Zonas (usar df_mapa con coordenadas válidas)
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df_mapa, tipo_zona)
                    for zona in zonas:
                        n_total = zona['n_clientes']

                        # Construir contenido para badge overlay
                        badge_content = []
                        if len(df_generico) > 0:
                            clientes_zona = set(zona.get('clientes', []))
                            df_zona_gen = df_generico[df_generico['id_cliente'].isin(clientes_zona)]
                            if len(df_zona_gen) > 0:
                                df_zg = df_zona_gen.copy()
                                df_zg['compro_act'] = df_zg['bultos_act'] > 0
                                df_zg['compro_ant'] = df_zg['bultos_ant'] > 0
                                resumen = df_zg.groupby('generico').agg(
                                    bultos_act=('bultos_act', 'sum'),
                                    bultos_ant=('bultos_ant', 'sum'),
                                    cli_act=('compro_act', 'sum'),
                                    cli_ant=('compro_ant', 'sum'),
                                ).sort_values('bultos_act', ascending=False)

                                total_act = resumen['bultos_act'].sum()
                                total_ant = resumen['bultos_ant'].sum()

                                badge_content = _build_zona_badge_content(
                                    zona['nombre'], n_total, resumen,
                                    total_act, total_ant, zona['color_borde']
                                )

                        if not badge_content:
                            badge_content = [html.Div(f"{zona['nombre']} — {n_total} clientes",
                                                      style={'padding': '8px', 'color': '#fff'})]

                        route_badges.append(
                            dmc.HoverCard(
                                position='bottom', withArrow=True, shadow='md',
                                children=[
                                    dmc.HoverCardTarget(
                                        html.Div(
                                            zona['nombre'],
                                            style={
                                                'padding': '4px 10px',
                                                'borderRadius': '12px',
                                                'fontSize': '11px',
                                                'fontWeight': '600',
                                                'color': '#fff',
                                                'backgroundColor': zona['color_borde'].replace('0.8', '0.65'),
                                                'cursor': 'pointer',
                                                'whiteSpace': 'nowrap',
                                                'border': f"1px solid {zona['color_borde']}",
                                            }
                                        )
                                    ),
                                    dmc.HoverCardDropdown(
                                        badge_content,
                                        style={
                                            'backgroundColor': DARK['card'],
                                            'border': f"1px solid {DARK['border']}",
                                            'padding': '0',
                                            'maxHeight': '400px',
                                            'overflowY': 'auto',
                                        }
                                    ),
                                ]
                            )
                        )

                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'], lon=zona['lons'],
                            mode='lines', fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({n_total} clientes)",
                            hoverinfo='name',
                            showlegend=True
                        ))

            # Clientes sin ventas (marcados con circulo rojo)
            if len(df_sin_ventas) > 0:
                df_sin_ventas = df_sin_ventas.copy()
                df_sin_ventas['desglose_generico'] = df_sin_ventas['id_cliente'].map(desglose_map).fillna('')
                fig.add_trace(go.Scattermap(
                    lat=df_sin_ventas['latitud'], lon=df_sin_ventas['longitud'],
                    mode='markers',
                    marker=dict(size=7, color='#ff0000', opacity=0.9),
                    name='Sin ventas',
                    text=df_sin_ventas['razon_social'],
                    hovertemplate=(
                        '<b>[%{customdata[6]}] %{text}</b><br>'
                        '%{customdata[9]}<br>'
                        'Ruta: %{customdata[1]} | Prev: %{customdata[7]}<br>'
                        'Canal: %{customdata[10]} | LP: %{customdata[8]}<br>'
                        'Localidad: %{customdata[0]} | Suc: %{customdata[11]}<br>'
                        '─────────────<br>'
                        '<b>Sin ventas en periodo</b><br>'
                        '─────────────<br>'
                        '%{customdata[5]}'
                        '<extra></extra>'
                    ),
                    customdata=df_sin_ventas[['localidad', 'ruta', 'cantidad_total', 'facturacion',
                                              'cantidad_documentos', 'desglose_generico', 'id_cliente',
                                              'preventista', 'lista_precio', 'fantasia', 'canal', 'sucursal']].values
                ))

            # Clientes con ventas
            if len(df_con_ventas) > 0:
                # Escala fija 0-15: tamaño y color
                size_normalized = 5 + (df_con_ventas[metrica].clip(upper=15) / 15 * 15)

                fig.add_trace(go.Scattermap(
                    lat=df_con_ventas['latitud'], lon=df_con_ventas['longitud'],
                    mode='markers',
                    marker=dict(
                        size=size_normalized,
                        color=df_con_ventas[metrica],
                        colorscale=[[0, 'rgb(30, 80, 180)'], [0.35, 'rgb(0, 180, 220)'], [0.65, 'rgb(80, 200, 80)'], [1, 'rgb(240, 220, 0)']],
                        cmin=0,
                        cmax=15,
                        showscale=True,
                        colorbar=dict(title=metrica_labels[metrica], tickformat=',.0f'),
                        opacity=0.8
                    ),
                    name='Con ventas',
                    text=df_con_ventas['razon_social'],
                    hovertemplate=(
                        '<b>%{text}</b> [%{customdata[6]}]<br>'
                        'Localidad: %{customdata[0]}<br>'
                        'Bultos: %{customdata[2]:,.0f} | Fact: $%{customdata[3]:,.2f}<br>'
                        '─────────────<br>'
                        '%{customdata[5]}'
                        '<extra></extra>'
                    ),
                    customdata=df_con_ventas[['localidad', 'subcanal', 'cantidad_total', 'facturacion', 'cantidad_documentos', 'desglose_generico', 'id_cliente']].values
                ))

            fig.update_layout(
                map=dict(style='open-street-map', center=dict(lat=center_lat, lon=center_lon), zoom=zoom_level),
                margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                showlegend=True,
                legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(255,255,255,0.8)'),
                hoverlabel=dict(font=dict(family='monospace'))
            )
    else:
        fig = px.scatter_map(lat=[-24.8], lon=[-65.4], zoom=7, map_style='open-street-map')
        fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

    return fig, route_badges


# =============================================================================
# CALLBACKS BUSQUEDA DE CLIENTE EN MAPA
# =============================================================================

@callback(
    Output('busqueda-cliente-mapa', 'options'),
    Input('busqueda-cliente-mapa', 'search_value'),
    prevent_initial_call=True,
)
def buscar_cliente_en_mapa(search_value):
    """Poblar opciones del dropdown de búsqueda de cliente."""
    if not search_value or len(search_value) < 2:
        return no_update
    df = buscar_clientes(search_value, limite=10)
    opciones = []
    for _, row in df.iterrows():
        lat = row.get('latitud')
        lon = row.get('longitud')
        has_coords = pd.notna(lat) and pd.notna(lon) and lat != 0 and lon != 0
        suffix = '' if has_coords else ' (sin ubicación)'
        label = f"[{row['id_cliente']}] {row['razon_social']} - {row['localidad']}{suffix}"
        value = f"{row['id_cliente']}|{lat}|{lon}" if has_coords else f"{row['id_cliente']}||"
        opciones.append({'label': label, 'value': value})
    return opciones


@callback(
    Output('busqueda-cliente-store', 'data'),
    Input('busqueda-cliente-mapa', 'value'),
    prevent_initial_call=True,
)
def seleccionar_cliente_buscado(value):
    """Escribir coordenadas del cliente seleccionado en el store."""
    if not value:
        return {}
    parts = value.split('|')
    id_cliente = parts[0]
    lat_str = parts[1] if len(parts) > 1 else ''
    lon_str = parts[2] if len(parts) > 2 else ''
    if lat_str and lon_str and lat_str != 'nan' and lon_str != 'nan':
        return {
            'lat': float(lat_str),
            'lon': float(lon_str),
            'zoom': 16,
            'id_cliente': int(id_cliente),
        }
    return {}


# =============================================================================
# CALLBACK MAPA DE CALOR
# =============================================================================

@callback(
    Output('mapa-calor', 'figure'),
    [Input('filtro-fechas', 'value'),
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
     Input('opcion-escala-log', 'checked'),
     Input('slider-precision', 'value'),
     Input('tipo-mapa-calor', 'value'),
     Input('slider-radio-difuso', 'value'),
     Input('tipo-normalizacion', 'value'),
     Input('opcion-animacion', 'checked'),
     Input('granularidad-animacion', 'value')]
)
def actualizar_mapa_calor(fechas_value, canales, subcanales, localidades, listas_precio,
                          sucursales, metrica, genericos, marcas, rutas, preventistas, fuerza_venta,
                          opciones_zonas, opcion_escala, precision, tipo_mapa, radio_difuso,
                          tipo_normalizacion, opcion_animacion, granularidad):
    """Actualiza el mapa de calor (difuso o grilla)."""

    start_date, end_date = (fechas_value or [None, None])[:2]
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None
    usar_animacion = opcion_animacion or False
    granularidad = granularidad or 'semana'

    if usar_animacion:
        df = cargar_ventas_animacion(start_date, end_date, genericos, marcas, rutas, preventistas, fv, granularidad)
    else:
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

    # Filtrar clientes con coordenadas válidas para el mapa de calor
    df_mapa = df[
        (df['latitud'].notna()) &
        (df['longitud'].notna()) &
        (df['latitud'] != 0) &
        (df['longitud'] != 0)
    ].copy()

    df_con_ventas = df_mapa[df_mapa['cantidad_total'] > 0].copy()

    metrica_labels = METRICA_LABELS
    usar_log = opcion_escala or False
    escala_texto = " (log)" if usar_log else ""

    precision = precision or 2
    tipo_mapa = tipo_mapa or 'density'
    radio_difuso = radio_difuso or 50
    tipo_normalizacion = tipo_normalizacion or 'normal'

    if len(df_con_ventas) > 0:
        center_lat = df_con_ventas['latitud'].mean()
        center_lon = df_con_ventas['longitud'].mean()

        # MAPA ANIMADO
        if usar_animacion and 'periodo' in df_con_ventas.columns:
            df_con_ventas['metrica_z'] = df_con_ventas[metrica]
            if usar_log:
                df_con_ventas['metrica_z'] = np.log1p(df_con_ventas['metrica_z'])

            # Rango dinamico basado en datos filtrados
            z_min = df_con_ventas['metrica_z'].min()
            z_max = df_con_ventas['metrica_z'].max()

            fig = px.density_map(
                df_con_ventas, lat='latitud', lon='longitud', z='metrica_z',
                radius=radio_difuso, opacity=0.5, animation_frame='periodo',
                center=dict(lat=center_lat, lon=center_lon), zoom=8,
                map_style='open-street-map',
                color_continuous_scale=[
                    [0.0, 'rgb(0, 0, 150)'], [0.15, 'rgb(0, 100, 255)'],
                    [0.3, 'rgb(0, 200, 255)'], [0.45, 'rgb(0, 255, 150)'],
                    [0.55, 'rgb(200, 255, 0)'], [0.7, 'rgb(255, 200, 0)'],
                    [0.85, 'rgb(255, 100, 0)'], [1.0, 'rgb(200, 0, 0)']
                ],
                range_color=[z_min, z_max]
            )
            fig.update_layout(
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                coloraxis_colorbar=dict(title=metrica_labels[metrica] + escala_texto, tickformat=',.0f')
            )
            if hasattr(fig.layout, 'updatemenus') and fig.layout.updatemenus:
                fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300

        elif tipo_mapa == 'density':
            # MAPA DIFUSO
            if tipo_normalizacion == 'percentil':
                df_con_ventas['metrica_z'] = df_con_ventas[metrica].rank(pct=True) * 100
                norm_texto = " [percentil]"
                range_color = [0, 100]
            elif tipo_normalizacion == 'limitado':
                p95 = df_con_ventas[metrica].quantile(0.95)
                df_con_ventas['metrica_z'] = df_con_ventas[metrica].clip(upper=p95)
                norm_texto = " [p95]"
                range_color = [0, p95]
            else:
                df_con_ventas['metrica_z'] = df_con_ventas[metrica]
                norm_texto = ""
                # Rango dinamico basado en datos filtrados
                range_color = [df_con_ventas[metrica].min(), df_con_ventas[metrica].max()]

            if usar_log and tipo_normalizacion == 'normal':
                df_con_ventas['metrica_z'] = np.log1p(df_con_ventas['metrica_z'])
                # Actualizar rango para escala logaritmica
                range_color = [df_con_ventas['metrica_z'].min(), df_con_ventas['metrica_z'].max()]

            fig = px.density_map(
                df_con_ventas, lat='latitud', lon='longitud', z='metrica_z',
                radius=radio_difuso, opacity=0.5,
                center=dict(lat=center_lat, lon=center_lon), zoom=8,
                map_style='open-street-map',
                color_continuous_scale=[
                    [0.0, 'rgb(0, 0, 150)'], [0.15, 'rgb(0, 100, 255)'],
                    [0.3, 'rgb(0, 200, 255)'], [0.45, 'rgb(0, 255, 150)'],
                    [0.55, 'rgb(200, 255, 0)'], [0.7, 'rgb(255, 200, 0)'],
                    [0.85, 'rgb(255, 100, 0)'], [1.0, 'rgb(200, 0, 0)']
                ],
                range_color=range_color
            )
            fig.update_layout(
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                coloraxis_colorbar=dict(title=metrica_labels[metrica] + escala_texto + norm_texto, tickformat=',.0f')
            )

            # Zonas (usar df_mapa con coordenadas válidas)
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df_mapa, tipo_zona)
                    for zona in zonas:
                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'], lon=zona['lons'],
                            mode='lines', fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                            hoverinfo='name', showlegend=True
                        ))

        else:
            # MAPA GRILLA
            grupos = crear_grilla_calor_optimizada(df_con_ventas, metrica, precision=precision, usar_log=usar_log)

            fig = go.Figure()

            for grupo_id, grupo in grupos.items():
                color = COLORES_CALOR[grupo_id]
                fig.add_trace(go.Scattermap(
                    lat=grupo['lats'], lon=grupo['lons'],
                    mode='lines', fill='toself',
                    fillcolor=color, line=dict(color=color, width=0),
                    name=f"Nivel {grupo_id + 1}",
                    hoverinfo='text',
                    hovertext=f"Celdas: {grupo['n_celdas']}<br>Clientes: {grupo['total_clientes']:,}",
                    showlegend=False
                ))

            # Colorbar
            val_min = df_con_ventas[metrica].min()
            val_max = df_con_ventas[metrica].max()
            fig.add_trace(go.Scattermap(
                lat=[None], lon=[None], mode='markers',
                marker=dict(
                    size=0, color=[val_min, val_max],
                    colorscale=[
                        [0.0, 'rgb(0, 50, 150)'], [0.14, 'rgb(0, 100, 255)'],
                        [0.28, 'rgb(0, 200, 255)'], [0.42, 'rgb(0, 255, 150)'],
                        [0.57, 'rgb(200, 255, 0)'], [0.71, 'rgb(255, 200, 0)'],
                        [0.85, 'rgb(255, 100, 0)'], [1.0, 'rgb(200, 0, 0)']
                    ],
                    showscale=True,
                    colorbar=dict(title=metrica_labels[metrica] + escala_texto, tickformat=',.0f')
                ),
                showlegend=False, hoverinfo='skip'
            ))

            # Zonas (usar df_mapa con coordenadas válidas)
            if opciones_zonas:
                for tipo_zona in opciones_zonas:
                    zonas = calcular_zonas(df_mapa, tipo_zona)
                    for zona in zonas:
                        fig.add_trace(go.Scattermap(
                            lat=zona['lats'], lon=zona['lons'],
                            mode='lines', fill='toself',
                            fillcolor=zona['color'],
                            line=dict(color=zona['color_borde'], width=2),
                            name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                            hoverinfo='name', showlegend=True
                        ))

            fig.update_layout(
                map=dict(style='open-street-map', center=dict(lat=center_lat, lon=center_lon), zoom=8),
                margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
                showlegend=True if opciones_zonas else False
            )
    else:
        fig = go.Figure()
        fig.add_trace(go.Scattermap(lat=[-24.8], lon=[-65.4], mode='markers', marker=dict(size=1), showlegend=False))
        fig.update_layout(
            map=dict(style='open-street-map', center=dict(lat=-24.8, lon=-65.4), zoom=7),
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0}
        )

    return fig


# =============================================================================
# CALLBACK PESTAÑAS PRINCIPALES
# =============================================================================

@callback(
    [Output('seccion-mapas', 'style'),
     Output('seccion-tablero', 'style')],
    [Input('tabs-principales', 'value')]
)
def toggle_secciones_principales(tab_seleccionada):
    """
    Alterna la visibilidad entre la seccion de Mapas y el Tablero de Ventas
    segun la pestania superior seleccionada.
    """
    if tab_seleccionada == 'tab-mapas':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}

# =============================================================================
# CALLBACKS TABLERO - COMPARACION ANUAL
# =============================================================================

# Colores para las lineas de años
COLORES_ANIOS = [
    '#3498db',  # Azul
    '#e74c3c',  # Rojo
    '#27ae60',  # Verde
    '#9b59b6',  # Purpura
    '#f39c12',  # Naranja
    '#1abc9c',  # Turquesa
    '#e91e63',  # Rosa
    '#34495e',  # Gris oscuro
]

# Nombres de meses en español
MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


@callback(
    Output('selector-anios', 'data'),
    [Input('tabs-principales', 'value')]
)
def actualizar_opciones_anios(tab_activa):
    """Genera las opciones de años disponibles desde la base de datos."""
    try:
        anios = obtener_anios_disponibles()
        opciones = [{'label': str(anio), 'value': str(anio)} for anio in anios]
        return opciones
    except Exception:
        return []


@callback(
    Output('grafico-linea-tiempo', 'figure'),
    [Input('selector-anios', 'value'),
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
def actualizar_grafico_comparacion_anual(anios_seleccionados, canales, subcanales, localidades,
                                          listas_precio, sucursales, metrica, genericos, marcas,
                                          rutas, preventistas, fuerza_venta):
    """Genera la grafica de comparacion anual con una linea por cada año seleccionado."""

    metrica_labels = {'cantidad_total': 'Cantidad (bultos)', 'facturacion': 'Facturacion ($)', 'cantidad_documentos': 'Documentos'}

    fig = go.Figure()

    if not anios_seleccionados or len(anios_seleccionados) == 0:
        fig.add_annotation(
            text="Seleccione uno o más años para comparar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=DARK['text_muted'])
        )
        fig.update_layout(
            margin=dict(t=30, b=50, l=60, r=30),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor=DARK['plot_bg'],
            paper_bgcolor=DARK['paper_bg'],
        )
        return fig

    # Ordenar años
    anios_seleccionados = sorted(anios_seleccionados)

    # Cargar y procesar datos para cada año
    for i, anio in enumerate(anios_seleccionados):
        color = COLORES_ANIOS[i % len(COLORES_ANIOS)]

        # Rango de fechas para el año completo
        fecha_inicio = f"{anio}-01-01"
        fecha_fin = f"{anio}-12-31"

        # Cargar datos
        fv = fuerza_venta if fuerza_venta != 'TODOS' else None
        df_fecha = cargar_ventas_por_fecha(
            fecha_inicio, fecha_fin,
            canales, subcanales, localidades, listas_precio, sucursales,
            genericos, marcas, rutas, preventistas, fv
        )

        if len(df_fecha) > 0:
            # Convertir fecha y extraer mes
            df_fecha['fecha'] = pd.to_datetime(df_fecha['fecha'])
            df_fecha['mes'] = df_fecha['fecha'].dt.month

            # Agregar por mes
            df_mensual = df_fecha.groupby('mes')[metrica].sum().reset_index()

            # Asegurar que todos los meses esten (1-12)
            df_completo = pd.DataFrame({'mes': range(1, 13)})
            df_mensual = df_completo.merge(df_mensual, on='mes', how='left').fillna(0)

            fig.add_trace(go.Scatter(
                x=df_mensual['mes'],
                y=df_mensual[metrica],
                mode='lines+markers',
                line=dict(color=color, width=3),
                marker=dict(size=8),
                name=str(anio),
                hovertemplate=f"<b>{anio}</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>"
            ))

    # Configurar layout
    fig.update_layout(
        margin=dict(t=30, b=50, l=70, r=30),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=MESES_ES,
            title='Mes',
            color=DARK['text_secondary']
        ),
        yaxis=dict(title=metrica_labels.get(metrica, metrica), color=DARK['text_secondary']),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=14, color=DARK['text'])
        ),
        plot_bgcolor=DARK['plot_bg'],
        paper_bgcolor=DARK['paper_bg'],
    )
    fig.update_yaxes(tickformat=',.0f', gridcolor=DARK['grid'])

    return fig


@callback(
    Output('tabla-comparativa-container', 'children'),
    [Input('selector-anios', 'value'),
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
def actualizar_tabla_comparativa(anios_seleccionados, canales, subcanales, localidades,
                                  listas_precio, sucursales, metrica, genericos, marcas,
                                  rutas, preventistas, fuerza_venta):
    """Genera la tabla comparativa por mes y año con porcentaje de crecimiento."""

    metrica_labels = {'cantidad_total': 'Cantidad (bultos)', 'facturacion': 'Facturacion ($)', 'cantidad_documentos': 'Documentos'}

    if not anios_seleccionados or len(anios_seleccionados) == 0:
        return html.P("Seleccione años para ver la comparación", style={'textAlign': 'center', 'color': DARK['text_muted']})

    # Ordenar años
    anios_seleccionados = sorted(anios_seleccionados)

    # Diccionario para almacenar datos por mes y año
    datos_por_anio = {}
    fv = fuerza_venta if fuerza_venta != 'TODOS' else None

    for anio in anios_seleccionados:
        fecha_inicio = f"{anio}-01-01"
        fecha_fin = f"{anio}-12-31"

        df_fecha = cargar_ventas_por_fecha(
            fecha_inicio, fecha_fin,
            canales, subcanales, localidades, listas_precio, sucursales,
            genericos, marcas, rutas, preventistas, fv
        )

        if len(df_fecha) > 0:
            df_fecha['fecha'] = pd.to_datetime(df_fecha['fecha'])
            df_fecha['mes'] = df_fecha['fecha'].dt.month
            df_mensual = df_fecha.groupby('mes')[metrica].sum().to_dict()
            datos_por_anio[anio] = df_mensual
        else:
            datos_por_anio[anio] = {}

    # Construir filas de la tabla
    filas = []
    totales_por_anio = {anio: 0 for anio in anios_seleccionados}

    for mes_num in range(1, 13):
        mes_nombre = MESES_ES[mes_num - 1]
        fila_celdas = [html.Td(mes_nombre, style={'fontWeight': 'bold', 'padding': '12px 15px', 'borderBottom': f'1px solid {DARK["border"]}', 'color': DARK['text']})]

        valor_anterior = None
        for i, anio in enumerate(anios_seleccionados):
            valor = datos_por_anio.get(anio, {}).get(mes_num, 0)
            totales_por_anio[anio] += valor

            # Calcular porcentaje de crecimiento vs año anterior
            if i == 0 or valor_anterior is None or valor_anterior == 0:
                texto = f"{valor:,.0f}"
                color = DARK['text']
            else:
                pct = ((valor - valor_anterior) / valor_anterior) * 100
                signo = '+' if pct >= 0 else ''
                texto = f"{valor:,.0f} ({signo}{pct:.0f}%)"
                color = '#27ae60' if pct >= 0 else '#e74c3c'

            fila_celdas.append(html.Td(
                texto,
                style={
                    'padding': '12px 15px',
                    'textAlign': 'right',
                    'borderBottom': f'1px solid {DARK["border"]}',
                    'color': color if i > 0 else DARK['text']
                }
            ))
            valor_anterior = valor

        filas.append(html.Tr(fila_celdas))

    # Fila de totales
    fila_totales = [html.Td("TOTAL", style={'fontWeight': 'bold', 'padding': '12px 15px', 'backgroundColor': DARK['surface'], 'borderTop': f'2px solid {DARK["text_secondary"]}', 'color': DARK['text']})]
    total_anterior = None
    for i, anio in enumerate(anios_seleccionados):
        total = totales_por_anio[anio]

        if i == 0 or total_anterior is None or total_anterior == 0:
            texto = f"{total:,.0f}"
            color = DARK['text']
        else:
            pct = ((total - total_anterior) / total_anterior) * 100
            signo = '+' if pct >= 0 else ''
            texto = f"{total:,.0f} ({signo}{pct:.0f}%)"
            color = '#27ae60' if pct >= 0 else '#e74c3c'

        fila_totales.append(html.Td(
            texto,
            style={
                'padding': '12px 15px',
                'textAlign': 'right',
                'fontWeight': 'bold',
                'backgroundColor': DARK['surface'],
                'borderTop': f'2px solid {DARK["text_secondary"]}',
                'color': color if i > 0 else DARK['text']
            }
        ))
        total_anterior = total

    filas.append(html.Tr(fila_totales))

    # Encabezado
    encabezado = [html.Th("Mes", style={'padding': '14px 15px', 'backgroundColor': DARK['surface'], 'color': DARK['text'], 'textAlign': 'left', 'fontSize': '17px'})]
    for anio in anios_seleccionados:
        encabezado.append(html.Th(
            str(anio),
            style={'padding': '14px 15px', 'backgroundColor': DARK['surface'], 'color': DARK['text'], 'textAlign': 'right', 'minWidth': '160px', 'fontSize': '17px'}
        ))

    tabla = html.Table([
        html.Thead(html.Tr(encabezado)),
        html.Tbody(filas)
    ], style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'fontSize': '16px'
    })

    # Retornar tabla con subtítulo de métrica
    return html.Div([
        html.P(f"Métrica: {metrica_labels.get(metrica, metrica)}",
               style={'textAlign': 'center', 'color': DARK['text_secondary'], 'marginBottom': '10px', 'fontSize': '14px'}),
        tabla
    ])


# =============================================================================
# CALLBACK MAPA COMPRO
# =============================================================================

@callback(
    Output('mapa-compro', 'figure'),
    [Input('filtro-fechas', 'value'),
     Input('filtro-canal', 'value'),
     Input('filtro-subcanal', 'value'),
     Input('filtro-localidad', 'value'),
     Input('filtro-lista-precio', 'value'),
     Input('filtro-sucursal', 'value'),
     Input('filtro-generico', 'value'),
     Input('filtro-marca', 'value'),
     Input('filtro-ruta', 'value'),
     Input('filtro-preventista', 'value'),
     Input('filtro-fuerza-venta', 'value'),
     Input('opciones-zonas', 'value')]
)
def actualizar_mapa_compro(fechas_value, canales, subcanales, localidades, listas_precio,
                            sucursales, genericos, marcas, rutas, preventistas, fuerza_venta,
                            opciones_zonas):
    """
    Mapa que muestra clientes que compraron (verde) vs no compraron (rojo) en el periodo.
    """
    start_date, end_date = (fechas_value or [None, None])[:2]
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

    if len(df) > 0:
        center_lat = df['latitud'].mean()
        center_lon = df['longitud'].mean()

        # Separar clientes
        df_compro = df[df['cantidad_total'] > 0].copy()
        df_no_compro = df[df['cantidad_total'] == 0].copy()

        fig = go.Figure()

        # Zonas (si estan habilitadas)
        if opciones_zonas:
            for tipo_zona in opciones_zonas:
                zonas = calcular_zonas(df, tipo_zona)
                for zona in zonas:
                    fig.add_trace(go.Scattermap(
                        lat=zona['lats'], lon=zona['lons'],
                        mode='lines', fill='toself',
                        fillcolor=zona['color'],
                        line=dict(color=zona['color_borde'], width=2),
                        name=f"{zona['nombre']} ({zona['n_clientes']} clientes)",
                        hoverinfo='name', showlegend=True
                    ))

        # Clientes que NO compraron (ROJO X)
        if len(df_no_compro) > 0:
            fig.add_trace(go.Scattermap(
                lat=df_no_compro['latitud'],
                lon=df_no_compro['longitud'],
                mode='markers',
                marker=dict(size=8, color='#ff0000', opacity=0.9),
                name=f'No compro ({len(df_no_compro):,})',
                text=df_no_compro['razon_social'],
                hovertemplate='<b>[%{customdata[2]}] %{text}</b><br>Localidad: %{customdata[0]}<br>Canal: %{customdata[1]}<br><b style="color:red">NO COMPRO</b><extra></extra>',
                customdata=df_no_compro[['localidad', 'canal', 'id_cliente']].values
            ))

        # Clientes que SI compraron (VERDE)
        if len(df_compro) > 0:
            fig.add_trace(go.Scattermap(
                lat=df_compro['latitud'],
                lon=df_compro['longitud'],
                mode='markers',
                marker=dict(size=10, color='#27ae60', opacity=0.7),
                name=f'Compro ({len(df_compro):,})',
                text=df_compro['razon_social'],
                hovertemplate='<b>%{text}</b><br>Localidad: %{customdata[0]}<br>Canal: %{customdata[1]}<br>Bultos: %{customdata[2]:,.0f}<br>Facturacion: $%{customdata[3]:,.2f}<extra></extra>',
                customdata=df_compro[['localidad', 'canal', 'cantidad_total', 'facturacion']].values
            ))

        fig.update_layout(
            map=dict(style='open-street-map', center=dict(lat=center_lat, lon=center_lon), zoom=8),
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
            showlegend=True,
            legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(255,255,255,0.9)')
        )
    else:
        fig = go.Figure()
        fig.add_trace(go.Scattermap(lat=[-24.8], lon=[-65.4], mode='markers', marker=dict(size=1), showlegend=False))
        fig.update_layout(
            map=dict(style='open-street-map', center=dict(lat=-24.8, lon=-65.4), zoom=7),
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0}
        )

    return fig


# =============================================================================
# CLIENTSIDE CALLBACK - CLICK EN MAPA ABRE DETALLE DE CLIENTE
# =============================================================================

clientside_callback(
    """
    function(clickData) {
        if (clickData && clickData.points && clickData.points.length > 0) {
            var point = clickData.points[0];
            if (point.customdata && point.customdata.length > 6) {
                var id_cliente = point.customdata[6];
                if (id_cliente) {
                    window.open('/cliente/' + id_cliente, '_blank');
                }
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('click-output-dummy', 'children'),
    Input('mapa-ventas', 'clickData'),
    prevent_initial_call=True
)
