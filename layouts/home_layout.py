"""
Layout de página de inicio con tarjetas de navegación a tableros.
"""
from dash import html, dcc


def create_home_layout():
    """Crea el layout de la página de inicio con cards para cada tablero."""

    card_style = {
        'backgroundColor': 'white',
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
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
        'color': 'inherit'
    }

    icon_style = {
        'fontSize': '48px',
        'marginBottom': '15px'
    }

    title_style = {
        'fontSize': '20px',
        'fontWeight': 'bold',
        'marginBottom': '10px',
        'color': '#1a1a2e'
    }

    description_style = {
        'fontSize': '14px',
        'color': '#666',
        'lineHeight': '1.5'
    }

    # Definición de tableros disponibles
    tableros = [
        {
            'id': 'ventas',
            'icon': '📊',
            'title': 'Dashboard de Ventas',
            'description': 'Mapas de ventas, análisis geográfico, KPIs y evolución temporal de ventas por cliente.',
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
            'id': 'nuevo',
            'icon': '🚧',
            'title': 'Nuevo Tablero',
            'description': 'Próximamente: Nuevo tablero de análisis. Haz clic para crear uno nuevo.',
            'color': '#95a5a6',
            'href': '/nuevo'
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
                'color': 'white',
                'fontSize': '36px'
            }),
            html.P("Sistema de Análisis y Visualización de Datos",
                   style={'margin': '10px 0 0 0', 'color': '#ccc', 'fontSize': '16px'})
        ], style={
            'backgroundColor': '#1a1a2e',
            'padding': '40px',
            'textAlign': 'center'
        }),

        # Contenido principal
        html.Div([
            html.H2("Selecciona un tablero", style={
                'textAlign': 'center',
                'color': '#333',
                'marginBottom': '10px',
                'marginTop': '40px'
            }),
            html.P("Elige el tablero que deseas visualizar", style={
                'textAlign': 'center',
                'color': '#666',
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
            'backgroundColor': '#f5f7fa',
            'minHeight': 'calc(100vh - 150px)',
            'padding': '20px'
        }),

        # Footer
        html.Div([
            html.P("© 2025 Medallion ETL Dashboard", style={
                'textAlign': 'center',
                'color': '#999',
                'margin': '0',
                'padding': '20px'
            })
        ], style={
            'backgroundColor': '#1a1a2e'
        })
    ], style={
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
    })
