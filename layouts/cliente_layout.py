"""
Layout de detalle de cliente.
Muestra ventas historicas en estructura de arbol: generico -> marca -> articulo.
"""
from dash import html, dcc
from config import DARK


def create_cliente_layout(id_cliente):
    """Crea el layout del detalle de cliente con store para el ID."""
    return html.Div([
        dcc.Store(id='cliente-id-store', data={'id_cliente': id_cliente}),
        dcc.Store(id='excel-marca-trigger', data=''),
        dcc.Download(id='download-excel-marca'),
        dcc.Download(id='download-excel-completo'),

        # Header
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Volver a Ventas", style={
                        'color': DARK['text_secondary'],
                        'fontSize': '14px',
                        'textDecoration': 'none',
                        'padding': '8px 15px',
                        'backgroundColor': 'rgba(255,255,255,0.1)',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }),
                    href='/ventas',
                    style={'textDecoration': 'none'}
                ),
            ], style={'marginBottom': '10px'}),
            html.Div(id='cliente-header-content'),
        ], style={
            'backgroundColor': DARK['header'],
            'padding': '20px',
            'borderBottom': f'1px solid {DARK["border"]}',
        }),

        # Contenido principal
        html.Div(id='cliente-detail-content', style={
            'padding': '20px',
            'backgroundColor': DARK['bg'],
            'minHeight': 'calc(100vh - 150px)',
        }),
    ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': DARK['bg']})
