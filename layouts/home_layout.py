"""
Layout de página de inicio con tarjetas de navegación a tableros.
"""
from dash import html, dcc
from config import DARK


def create_home_layout(user=None):
    """Crea el layout de la página de inicio con cards para cada tablero.

    Args:
        user: objeto User si auth está activa, None si no.
    """

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
            'title': 'Mapa de Ventas',
            'description': 'Mapas de ventas, análisis geográfico y KPIs por cliente.',
            'color': '#3498db',
            'href': '/ventas'
        },
        {
            'id': 'clientes',
            'icon': '🔍',
            'title': 'Buscar Clientes',
            'description': 'Buscar clientes por nombre, fantasía o código para ver su detalle.',
            'color': '#27ae60',
            'href': '/clientes'
        },
    ]

    # Card de admin (solo visible para admin)
    if user and user.is_admin:
        tableros.append({
            'id': 'admin',
            'icon': '👥',
            'title': 'Gestión de Usuarios',
            'description': 'Crear, editar y administrar usuarios del sistema. Asignar roles y sucursales.',
            'color': '#8e44ad',
            'href': '/admin/usuarios'
        })

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

    # User info bar (solo si auth activa)
    user_bar = html.Div()
    if user:
        role_name = user.role.name.capitalize() if user.role else ''
        user_bar = html.Div([
            html.Div([
                html.Span(f"{user.full_name}", style={
                    'color': DARK['text'], 'fontWeight': '600', 'fontSize': '14px'
                }),
                html.Span(f"  ({role_name})", style={
                    'color': DARK['text_muted'], 'fontSize': '12px'
                }),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'}),
            dcc.Link("Cerrar sesión", href='/logout', style={
                'color': DARK['accent_red'], 'fontSize': '13px',
                'textDecoration': 'none', 'fontWeight': '500'
            }),
        ], style={
            'display': 'flex', 'justifyContent': 'space-between',
            'alignItems': 'center', 'padding': '10px 40px',
            'backgroundColor': DARK['surface'],
            'borderBottom': f'1px solid {DARK["border"]}',
        })

    return html.Div([
        user_bar,

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
