"""
Callbacks del YTD Dashboard.
Maneja la interactividad y actualización de gráficos y KPIs.
"""
import plotly.graph_objects as go
import plotly.express as px
from dash import callback, Output, Input, html

from data.ytd_queries import (
    obtener_ventas_ytd,
    obtener_ventas_por_mes,
    obtener_ventas_por_generico,
    obtener_ventas_por_sucursal,
    obtener_ventas_por_canal,
    calcular_target_automatico,
    calcular_targets_por_generico,
    calcular_targets_por_sucursal,
    calcular_crecimiento_mensual,
    obtener_dias_inventario
)


# Nombres de meses
MESES_NOMBRES = {
    1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
    7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
}


@callback(
    [Output('ytd-kpi-sales', 'children'),
     Output('ytd-kpi-yoy', 'children'),
     Output('ytd-kpi-yoy', 'style'),
     Output('ytd-kpi-target', 'children'),
     Output('ytd-kpi-achievement', 'children'),
     Output('ytd-kpi-lastyear', 'children')],
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_kpis(anio, mes, tipo_sucursal):
    """Actualiza los KPIs principales del dashboard."""
    try:
        # Ventas actuales
        df_actual = obtener_ventas_ytd(anio, mes, tipo_sucursal)
        ventas_actual = df_actual['bultos'].iloc[0] if len(df_actual) > 0 and df_actual['bultos'].iloc[0] else 0

        # Target y año anterior
        targets = calcular_target_automatico(anio, mes, incremento_pct=10, tipo_sucursal=tipo_sucursal)
        target = targets['target_total']
        ventas_anterior = targets['ventas_anio_anterior']

        # Calcular YoY
        if ventas_anterior > 0:
            yoy = ((ventas_actual - ventas_anterior) / ventas_anterior) * 100
            yoy_text = f"{yoy:+.0f}% {'↑' if yoy >= 0 else '↓'}"
            yoy_color = '#27ae60' if yoy >= 0 else '#e74c3c'
        else:
            yoy_text = "N/A"
            yoy_color = '#666'

        # Achievement
        if target > 0:
            achievement = (ventas_actual / target) * 100
            ach_color = '#27ae60' if achievement >= 100 else '#f39c12' if achievement >= 90 else '#e74c3c'
            achievement_content = html.Div([
                html.Div(f"{achievement:.0f}%", style={
                    'fontSize': '30px',
                    'fontWeight': 'bold',
                    'color': ach_color,
                    'textAlign': 'center'
                })
            ])
        else:
            achievement_content = html.Div("N/A", style={'textAlign': 'center', 'color': '#999'})

        return (
            f"{ventas_actual:,.0f}",
            yoy_text,
            {'fontSize': '14px', 'fontWeight': 'bold', 'color': yoy_color},
            f"{target:,.0f}",
            achievement_content,
            f"{ventas_anterior:,.0f}"
        )

    except Exception as e:
        return "Error", "N/A", {'color': '#999'}, "Error", html.Div("Error"), "Error"


@callback(
    Output('ytd-chart-generico', 'figure'),
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_grafico_generico(anio, mes, tipo_sucursal):
    """Gráfico de barras por genérico con targets."""
    try:
        df = obtener_ventas_por_generico(anio, mes, top_n=5, tipo_sucursal=tipo_sucursal)
        targets = calcular_targets_por_generico(anio, mes, incremento_pct=10, top_n=5, tipo_sucursal=tipo_sucursal)

        if len(df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        # Preparar datos
        categorias = df['generico'].tolist()
        valores = df['bultos'].tolist()
        targets_vals = [targets.get(c, 0) for c in categorias]

        # Colores según cumplimiento
        colores = []
        above_target = []
        below_target = []

        for v, t in zip(valores, targets_vals):
            if t > 0:
                if v >= t:
                    colores.append('#27ae60')  # Verde - above target
                    above_target.append(v - t)
                    below_target.append(t)
                else:
                    colores.append('#3498db')  # Azul - below target
                    above_target.append(0)
                    below_target.append(v)
            else:
                colores.append('#3498db')
                above_target.append(0)
                below_target.append(v)

        fig = go.Figure()

        # Barras principales
        fig.add_trace(go.Bar(
            x=categorias,
            y=below_target,
            name='Bajo Objetivo',
            marker_color='#3498db',
            text=[f'{v:,.0f}' for v in valores],
            textposition='outside'
        ))

        # Parte above target
        fig.add_trace(go.Bar(
            x=categorias,
            y=above_target,
            name='Sobre Objetivo',
            marker_color='#27ae60'
        ))

        # Línea de target
        fig.add_trace(go.Scatter(
            x=categorias,
            y=targets_vals,
            mode='markers',
            name='Objetivo',
            marker=dict(symbol='line-ew', size=15, color='#2c3e50', line_width=3)
        ))

        fig.update_layout(
            barmode='stack',
            margin=dict(l=10, r=10, t=10, b=50),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=14)),
            xaxis=dict(tickfont=dict(size=14)),
            yaxis=dict(tickfont=dict(size=14))
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {str(e)[:30]}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig


@callback(
    Output('ytd-chart-monthly', 'figure'),
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_grafico_mensual(anio, mes, tipo_sucursal):
    """Gráfico de barras mensual con colores según cumplimiento de target."""
    try:
        df = obtener_ventas_por_mes(anio, mes, tipo_sucursal)
        targets = calcular_target_automatico(anio, mes, incremento_pct=10, tipo_sucursal=tipo_sucursal)
        targets_mes = targets['targets_por_mes']

        if len(df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        meses = [MESES_NOMBRES.get(int(m), str(m)) for m in df['mes']]
        valores = df['bultos'].tolist()
        targets_list = [targets_mes.get(int(m), 0) for m in df['mes']]

        # Colores según cumplimiento
        colores = []
        for v, t in zip(valores, targets_list):
            if t > 0:
                pct = (v / t) * 100
                if pct >= 100:
                    colores.append('#27ae60')  # Verde >= 100%
                elif pct >= 90:
                    colores.append('#f1c40f')  # Amarillo >= 90%
                else:
                    colores.append('#e74c3c')  # Rojo < 90%
            else:
                colores.append('#3498db')

        fig = go.Figure()

        # Barras
        fig.add_trace(go.Bar(
            x=meses,
            y=valores,
            marker_color=colores,
            text=[f'{v:,.0f}' for v in valores],
            textposition='outside',
            textfont=dict(size=10),
            name='Real'
        ))

        # Línea de target
        fig.add_trace(go.Scatter(
            x=meses,
            y=targets_list,
            mode='lines+markers',
            name='Objetivo',
            line=dict(color='#2c3e50', width=2, dash='dot'),
            marker=dict(size=6, symbol='square')
        ))

        # Leyenda personalizada
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(size=10, color='#27ae60'), name='>= 100% Obj.'))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(size=10, color='#f1c40f'), name='>= 90% Obj.'))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(size=10, color='#e74c3c'), name='< 90% Obj.'))

        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=40),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=10)),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11))
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig


@callback(
    Output('ytd-chart-sucursal', 'figure'),
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_grafico_sucursal(anio, mes, tipo_sucursal):
    """Gráfico de barras horizontales por sucursal con actual vs target."""
    try:
        df = obtener_ventas_por_sucursal(anio, mes, tipo_sucursal)
        targets = calcular_targets_por_sucursal(anio, mes, incremento_pct=10, tipo_sucursal=tipo_sucursal)

        if len(df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        # Limitar a top 6 sucursales
        df = df.head(6)
        sucursales = df['sucursal'].tolist()
        valores = df['bultos'].tolist()
        targets_list = [targets.get(s, 0) for s in sucursales]

        # Simplificar nombres de sucursal
        sucursales_cortos = [s.replace('SUCURSAL ', '').title() if 'SUCURSAL' in s else s.title()
                            for s in sucursales]

        fig = go.Figure()

        # Barras actuales
        fig.add_trace(go.Bar(
            y=sucursales_cortos,
            x=valores,
            orientation='h',
            name='Real',
            marker_color='#1a5276',
            text=[f'{v:,.0f}' for v in valores],
            textposition='outside',
            textfont=dict(size=11)
        ))

        # Barras target (más claras)
        fig.add_trace(go.Bar(
            y=sucursales_cortos,
            x=targets_list,
            orientation='h',
            name='Objetivo',
            marker_color='#aed6f1',
            text=[f'{t:,.0f}' for t in targets_list],
            textposition='outside',
            textfont=dict(size=11)
        ))

        fig.update_layout(
            barmode='group',
            margin=dict(l=10, r=50, t=10, b=30),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=11)),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11), autorange='reversed')
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text="Error", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig


@callback(
    Output('ytd-chart-canal', 'figure'),
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_grafico_canal(anio, mes, tipo_sucursal):
    """Gráfico de dona por canal."""
    try:
        df = obtener_ventas_por_canal(anio, mes, tipo_sucursal)

        if len(df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        colores = ['#1a5276', '#2980b9', '#3498db', '#5dade2', '#85c1e9', '#aed6f1']

        fig = go.Figure(data=[go.Pie(
            labels=df['canal'],
            values=df['bultos'],
            hole=0.5,
            marker_colors=colores[:len(df)],
            textinfo='label+percent',
            textfont=dict(size=11),
            insidetextorientation='horizontal'
        )])

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text="Error", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig


@callback(
    Output('ytd-chart-growth', 'figure'),
    [Input('ytd-anio', 'value'),
     Input('ytd-mes', 'value'),
     Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_grafico_crecimiento(anio, mes, tipo_sucursal):
    """Gráfico de barras de crecimiento mensual."""
    try:
        df = calcular_crecimiento_mensual(anio, mes, tipo_sucursal)

        if len(df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            return fig

        meses = [MESES_NOMBRES.get(int(m), str(m)) for m in df['mes']]
        valores = df['crecimiento_pct'].tolist()

        # Colores según positivo/negativo
        colores = ['#27ae60' if v >= 0 else '#e74c3c' for v in valores]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=meses,
            y=valores,
            marker_color=colores,
            text=[f'{v:+.0f}%' for v in valores],
            textposition='outside',
            textfont=dict(size=11)
        ))

        # Línea en 0
        fig.add_hline(y=0, line_dash="solid", line_color="#2c3e50", line_width=1)

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=40),
            showlegend=False,
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11), ticksuffix='%')
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text="Error", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig


@callback(
    [Output('ytd-gauge-inventario', 'figure'),
     Output('ytd-inventory-info', 'children')],
    [Input('ytd-tipo-sucursal', 'value')]
)
def actualizar_gauge_inventario(tipo_sucursal):
    """Gauge de días de inventario."""
    try:
        data = obtener_dias_inventario(tipo_sucursal)
        dias = data['dias_inventario']

        # Determinar color según días
        if dias <= 30:
            color = '#27ae60'  # Verde - bien
        elif dias <= 45:
            color = '#f1c40f'  # Amarillo - atención
        else:
            color = '#e74c3c'  # Rojo - exceso

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dias,
            title={'text': "Días", 'font': {'size': 15}},
            number={'font': {'size': 45}},
            gauge={
                'axis': {'range': [0, 180], 'tickwidth': 1, 'tickfont': {'size': 11}},
                'bar': {'color': color},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': '#ddd',
                'steps': [
                    {'range': [0, 30], 'color': '#d5f5e3'},
                    {'range': [30, 45], 'color': '#fcf3cf'},
                    {'range': [45, 180], 'color': '#fadbd8'}
                ],
                'threshold': {
                    'line': {'color': '#2c3e50', 'width': 2},
                    'thickness': 0.75,
                    'value': 33  # Objetivo
                }
            }
        ))

        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=10),
            height=225
        )

        info_text = html.Div([
            html.Span("Objetivo: 33 Días", style={'color': '#27ae60', 'fontWeight': 'bold'}),
            html.Br(),
            html.Span("Stock: {:,.0f} | Vta/día: {:,.0f}".format(
                data.get('stock_total', 0),
                data.get('promedio_diario', 0)
            ))
        ])

        return fig, info_text

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text="Error", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=225)
        return fig, "Error al cargar datos"
