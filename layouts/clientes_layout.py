"""
Layout de busqueda de clientes.
Permite buscar clientes por razon social, fantasia o ID y navegar a su detalle.
"""
from dash import html, dcc
from config import DARK


def create_clientes_layout():
    """Crea el layout de la pagina de busqueda de clientes."""
    return html.Div([
        # Header
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Inicio", style={
                        'color': DARK['text_secondary'],
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
            html.H1("Buscar Clientes", style={
                'margin': '0', 'color': DARK['text'], 'fontSize': '28px'
            }),
            html.P("Busca por razon social, nombre de fantasia o codigo de cliente. Presiona Enter para buscar.",
                   style={'margin': '5px 0 0 0', 'color': DARK['text_secondary'], 'fontSize': '14px'}),
        ], style={
            'backgroundColor': DARK['header'],
            'padding': '20px',
            'borderBottom': f'1px solid {DARK["border"]}',
        }),

        # Buscador
        html.Div([
            html.Div([
                dcc.Input(
                    id='clientes-busqueda',
                    placeholder='Escribi el nombre o codigo del cliente y presiona Enter...',
                    type='text',
                    debounce=True,
                    style={
                        'width': '100%', 'padding': '12px 16px', 'fontSize': '16px',
                        'border': f'1px solid {DARK["border"]}', 'borderRadius': '8px',
                        'outline': 'none',
                        'backgroundColor': DARK['surface'],
                        'color': DARK['text'],
                    },
                ),
            ], style={
                'maxWidth': '600px',
                'margin': '0 auto',
                'padding': '30px 20px 20px 20px',
            }),

            # Resultados
            html.Div(id='clientes-resultados', style={
                'maxWidth': '900px',
                'margin': '0 auto',
                'padding': '0 20px 30px 20px',
            }),
        ], style={
            'backgroundColor': DARK['bg'],
            'minHeight': 'calc(100vh - 130px)',
        }),
    ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': DARK['bg']})
