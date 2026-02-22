"""
Callbacks del Tablero de Ventas — comparación anual.
Movidos desde callbacks/callbacks.py al extraer el tablero a página independiente.
"""
import pandas as pd
import plotly.graph_objects as go
from dash import callback, Output, Input, html

from data.queries import cargar_ventas_por_fecha
from config import DARK

# Colores para las líneas de años
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
