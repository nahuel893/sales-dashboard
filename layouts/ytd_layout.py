"""
Layout del YTD Dashboard.
Dashboard de indicadores Year-To-Date con KPIs, gráficos y comparación con targets.
"""
from dash import html, dcc
from config import DARK


# Nombres de meses en español
MESES = {
    1: 'ENE', 2: 'FEB', 3: 'MAR', 4: 'ABR', 5: 'MAY', 6: 'JUN',
    7: 'JUL', 8: 'AGO', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DIC'
}


def create_ytd_layout(anio_actual, mes_actual, anios_disponibles):
    """Crea el layout del YTD Dashboard."""

    # Estilos (aumentados 25%)
    kpi_card_style = {
        'backgroundColor': DARK['card'],
        'padding': '18px',
        'marginBottom': '12px',
        'borderLeft': f'5px solid {DARK["accent_blue"]}',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.3)',
        'borderRadius': '4px'
    }

    kpi_value_style = {
        'fontSize': '53px',
        'fontWeight': 'bold',
        'color': DARK['text'],
        'margin': '0'
    }

    kpi_label_style = {
        'fontSize': '15px',
        'color': DARK['text_secondary'],
        'margin': '5px 0 0 0',
        'textTransform': 'uppercase'
    }

    chart_card_style = {
        'backgroundColor': DARK['card'],
        'padding': '18px',
        'margin': '6px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.3)',
        'height': '100%',
        'borderRadius': '4px',
        'border': f'1px solid {DARK["border"]}'
    }

    chart_title_style = {
        'fontSize': '18px',
        'fontWeight': 'bold',
        'color': DARK['accent_blue'],
        'marginBottom': '12px',
        'borderBottom': f'2px solid {DARK["border"]}',
        'paddingBottom': '6px'
    }

    return html.Div([
        # Header
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Inicio", style={
                        'color': DARK['text_secondary'],
                        'fontSize': '14px',
                        'padding': '8px 15px',
                        'backgroundColor': 'rgba(255,255,255,0.1)',
                        'borderRadius': '5px'
                    }),
                    href='/',
                    style={'textDecoration': 'none'}
                ),
            ], style={'marginBottom': '10px'}),

            html.Div([
                html.Div([
                    html.H1("Dashboard YTD", style={
                        'margin': '0',
                        'color': DARK['text'],
                        'fontSize': '30px'
                    }),
                    html.P("Análisis de Rendimiento Acumulado Anual",
                           style={'margin': '5px 0 0 0', 'color': DARK['text_secondary'], 'fontSize': '15px'})
                ], style={'flex': '1'}),

                # Filtros
                html.Div([
                    html.Div([
                        html.Label("Tipo Sucursal:", style={'color': DARK['text_secondary'], 'fontSize': '14px', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='ytd-tipo-sucursal',
                            options=[
                                {'label': 'Todas', 'value': 'TODAS'},
                                {'label': 'Solo Sucursales', 'value': 'SUCURSALES'},
                                {'label': 'Solo Casa Central', 'value': 'CASA_CENTRAL'}
                            ],
                            value='TODAS',
                            clearable=False,
                            style={'width': '170px', 'fontSize': '14px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),

                    html.Div([
                        html.Label("Año:", style={'color': DARK['text_secondary'], 'fontSize': '14px', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='ytd-anio',
                            options=[{'label': str(a), 'value': a} for a in anios_disponibles],
                            value=anio_actual,
                            clearable=False,
                            style={'width': '110px', 'fontSize': '14px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),

                    html.Div([
                        html.Label("Hasta Mes:", style={'color': DARK['text_secondary'], 'fontSize': '14px', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='ytd-mes',
                            options=[{'label': MESES[m], 'value': m} for m in range(1, 13)],
                            value=mes_actual,
                            clearable=False,
                            style={'width': '110px', 'fontSize': '14px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
        ], style={
            'backgroundColor': DARK['card_alt'],
            'padding': '15px 20px',
            'marginBottom': '0',
            'borderBottom': f'1px solid {DARK["border"]}'
        }),

        # Contenido principal
        html.Div([
            # Columna izquierda - KPIs
            html.Div([
                html.Div("Indicadores", style={
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'color': DARK['accent_blue'],
                    'padding': '12px 18px',
                    'backgroundColor': DARK['card'],
                    'borderBottom': f'2px solid {DARK["border"]}',
                    'marginBottom': '12px'
                }),

                # Ventas
                html.Div([
                    html.Div([
                        html.P(id='ytd-kpi-sales', children="0", style=kpi_value_style),
                        html.Div([
                            html.Span("Interanual ", style={'fontSize': '21px', 'color': DARK['text_secondary']}),
                            html.Span(id='ytd-kpi-yoy', children="0%", style={
                                'fontSize': '21px',
                                'fontWeight': 'bold'
                            })
                        ])
                    ]),
                    html.P("Ventas (Bultos)", style=kpi_label_style)
                ], style=kpi_card_style),

                # Objetivo de Ventas
                html.Div([
                    html.P(id='ytd-kpi-target', children="0", style=kpi_value_style),
                    html.P("Objetivo de Ventas", style=kpi_label_style)
                ], style=kpi_card_style),

                # Cumplimiento de Objetivo
                html.Div([
                    html.Div(id='ytd-kpi-achievement', children=[
                        html.Div("0%", style={
                            'fontSize': '45px',
                            'fontWeight': 'bold',
                            'color': '#27ae60',
                            'textAlign': 'center'
                        })
                    ]),
                    html.P("Cumplimiento Objetivo", style=kpi_label_style)
                ], style=kpi_card_style),

                # Ventas Año Anterior
                html.Div([
                    html.P(id='ytd-kpi-lastyear', children="0", style=kpi_value_style),
                    html.P("Ventas Año Anterior", style=kpi_label_style)
                ], style=kpi_card_style),

                # Ganancia Bruta (placeholder)
                html.Div([
                    html.P(id='ytd-kpi-profit', children="--", style={**kpi_value_style, 'color': DARK['text_muted']}),
                    html.P("Ganancia Bruta", style=kpi_label_style),
                    html.Span("(Próximamente)", style={'fontSize': '13px', 'color': DARK['text_muted']})
                ], style={**kpi_card_style, 'borderLeftColor': DARK['border']}),

                # Margen de Ganancia (placeholder)
                html.Div([
                    html.P(id='ytd-kpi-margin', children="--%", style={**kpi_value_style, 'color': DARK['text_muted']}),
                    html.P("Margen de Ganancia", style=kpi_label_style),
                    html.Span("(Próximamente)", style={'fontSize': '13px', 'color': DARK['text_muted']})
                ], style={**kpi_card_style, 'borderLeftColor': DARK['border']}),

            ], style={
                'width': '220px',
                'backgroundColor': DARK['surface'],
                'padding': '12px',
                'minHeight': 'calc(100vh - 100px)'
            }),

            # Área de gráficos
            html.Div([
                # Fila 1: Ventas por Producto + Real vs Objetivo
                html.Div([
                    # Ventas por Genérico
                    html.Div([
                        html.Div("Ventas (Bultos) por Genérico", style=chart_title_style),
                        dcc.Graph(id='ytd-chart-generico', config={'displayModeBar': False},
                                  style={'height': '310px'})
                    ], style={**chart_card_style, 'flex': '1', 'marginRight': '6px'}),

                    # Ventas Reales vs Objetivo por Mes
                    html.Div([
                        html.Div("Ventas Reales vs Objetivo", style=chart_title_style),
                        dcc.Graph(id='ytd-chart-monthly', config={'displayModeBar': False},
                                  style={'height': '310px'})
                    ], style={**chart_card_style, 'flex': '1.5'})
                ], style={'display': 'flex', 'marginBottom': '12px'}),

                # Fila 2: Ventas por Región + Ventas por Canal + Días de Inventario
                html.Div([
                    # Ventas por Sucursal
                    html.Div([
                        html.Div("Ventas (Bultos) por Sucursal", style=chart_title_style),
                        dcc.Graph(id='ytd-chart-sucursal', config={'displayModeBar': False},
                                  style={'height': '275px'})
                    ], style={**chart_card_style, 'padding': '8px', 'paddingTop': '12px', 'flex': '1', 'marginRight': '6px'}),

                    # Ventas por Canal
                    html.Div([
                        html.Div("Ventas por Canal", style=chart_title_style),
                        dcc.Graph(id='ytd-chart-canal', config={'displayModeBar': False},
                                  style={'height': '275px'})
                    ], style={**chart_card_style, 'flex': '1', 'marginRight': '6px'}),

                    # Días de Inventario
                    html.Div([
                        html.Div("Días de Inventario", style=chart_title_style),
                        dcc.Graph(id='ytd-gauge-inventario', config={'displayModeBar': False},
                                  style={'height': '225px'}),
                        html.Div(id='ytd-inventory-info', style={
                            'textAlign': 'center',
                            'fontSize': '14px',
                            'color': DARK['text_secondary']
                        })
                    ], style={**chart_card_style, 'flex': '0.8'})
                ], style={'display': 'flex', 'marginBottom': '12px'}),

                # Fila 3: Crecimiento + Días de Cobranza
                html.Div([
                    # Crecimiento de Ventas
                    html.Div([
                        html.Div("Crecimiento de Ventas (%)", style=chart_title_style),
                        dcc.Graph(id='ytd-chart-growth', config={'displayModeBar': False},
                                  style={'height': '275px'})
                    ], style={**chart_card_style, 'flex': '2', 'marginRight': '6px'}),

                    # Días de Cuentas por Cobrar (placeholder)
                    html.Div([
                        html.Div("Días de Cuentas por Cobrar", style=chart_title_style),
                        html.Div([
                            html.Div("--", style={
                                'fontSize': '68px',
                                'fontWeight': 'bold',
                                'color': DARK['text_muted'],
                                'textAlign': 'center',
                                'marginTop': '50px'
                            }),
                            html.Div("Días", style={'textAlign': 'center', 'color': DARK['text_muted'], 'fontSize': '16px'}),
                            html.Div("(Próximamente)", style={
                                'textAlign': 'center',
                                'fontSize': '14px',
                                'color': DARK['text_muted'],
                                'marginTop': '25px'
                            })
                        ])
                    ], style={**chart_card_style, 'flex': '0.8'})
                ], style={'display': 'flex'})

            ], style={
                'flex': '1',
                'padding': '10px',
                'backgroundColor': DARK['bg'],
                'overflowY': 'auto'
            })

        ], style={
            'display': 'flex',
            'minHeight': 'calc(100vh - 100px)'
        })

    ], style={
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'backgroundColor': DARK['bg']
    })
