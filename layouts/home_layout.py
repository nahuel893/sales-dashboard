"""
Layout de página de inicio con tarjetas de navegación a tableros.
"""
from dash import html, dcc
from config import DARK


def create_home_layout():
    """Crea el layout de la página de inicio con cards para cada tablero."""

    card_style = {
        'backgroundColor': DARK['card'],
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'padding': '30px',
        'margin': '15px',
        'width': '300px',
        'minHeight': '200px',
        'cursor': 'pointer',
        'transition': 'transform 0.2s, box-shadow 0.2s',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-between',
        'textDecoration': 'none',
        'color': 'inherit',
        'border': f'1px solid {DARK["border"]}'
    }

    icon_style = {
        'fontSize': '48px',
        'marginBottom': '15px'
    }

    title_style = {
        'fontSize': '20px',
        'fontWeight': 'bold',
        'marginBottom': '10px',
        'color': DARK['text']
    }

    description_style = {
        'fontSize': '14px',
        'color': DARK['text_secondary'],
        'lineHeight': '1.5'
    }

    # Definición de tableros disponibles
    tableros = [
        {
            'id': 'ventas',
            'icon': '📊',
            'title': 'Dashboard de Ventas',
            'description': 'Mapas de ventas, análisis geográfico y KPIs por cliente.',
            'color': '#3498db',
            'href': '/ventas'
        },
        {
            'id': 'ytd',
            'icon': '📈',
            'title': 'Dashboard YTD',
            'description': 'Análisis acumulado anual: KPIs, comparación con objetivos, crecimiento y días de inventario.',
            'color': '#1a5276',
            'href': '/ytd'
        },
        {
            'id': 'clientes',
            'icon': '🔍',
            'title': 'Buscar Clientes',
            'description': 'Busca clientes por nombre, fantasia o codigo. Accede al detalle con su historial de ventas.',
            'color': '#27ae60',
            'href': '/clientes'
        },
        {
            'id': 'tablero',
            'icon': '📋',
            'title': 'Tablero de Ventas',
            'description': 'Comparación anual de ventas por mes. Gráficos y tablas con filtros de producto y zona.',
            'color': '#e67e22',
            'href': '/tablero'
        },
    ]

    cards = []
    for tablero in tableros:
        card = dcc.Link(
            html.Div([
                html.Div([
                    html.Span(tablero['icon'], style=icon_style),
                    html.Div(tablero['title'], style=title_style),
                    html.Div(tablero['description'], style=description_style),
                ]),
                html.Div([
                    html.Span("Abrir →", style={
                        'color': tablero['color'],
                        'fontWeight': 'bold',
                        'fontSize': '14px'
                    })
                ], style={'marginTop': '20px'})
            ], style={**card_style, 'borderTop': f"4px solid {tablero['color']}"},
               className='dashboard-card'),
            href=tablero['href'],
            style={'textDecoration': 'none'}
        )
        cards.append(card)

    return html.Div([
        # Header
        html.Div([
            html.H1("Medallion ETL", style={
                'margin': '0',
                'color': DARK['text'],
                'fontSize': '36px'
            }),
            html.P("Sistema de Análisis y Visualización de Datos",
                   style={'margin': '10px 0 0 0', 'color': DARK['text_secondary'], 'fontSize': '16px'})
        ], style={
            'backgroundColor': DARK['header'],
            'padding': '40px',
            'textAlign': 'center',
            'borderBottom': f'1px solid {DARK["border"]}'
        }),

        # Contenido principal
        html.Div([
            html.H2("Selecciona un tablero", style={
                'textAlign': 'center',
                'color': DARK['text'],
                'marginBottom': '10px',
                'marginTop': '40px'
            }),
            html.P("Elige el tablero que deseas visualizar", style={
                'textAlign': 'center',
                'color': DARK['text_secondary'],
                'marginBottom': '40px'
            }),

            # Grid de cards
            html.Div(
                cards,
                style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'justifyContent': 'center',
                    'maxWidth': '1200px',
                    'margin': '0 auto',
                    'padding': '20px'
                }
            )
        ], style={
            'backgroundColor': DARK['bg'],
            'minHeight': 'calc(100vh - 150px)',
            'padding': '20px'
        }),

        # Footer
        html.Div([
            html.P("© 2026 Medallion ETL Dashboard", style={
                'textAlign': 'center',
                'color': DARK['text_muted'],
                'margin': '0',
                'padding': '20px'
            })
        ], style={
            'backgroundColor': DARK['header'],
            'borderTop': f'1px solid {DARK["border"]}'
        })
    ], style={
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        'backgroundColor': DARK['bg']
    })
