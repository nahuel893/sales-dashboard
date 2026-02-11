"""
Layout de busqueda de clientes.
Permite buscar clientes por razon social, fantasia o ID y navegar a su detalle.
"""
from dash import html, dcc
import dash_mantine_components as dmc


def create_clientes_layout():
    """Crea el layout de la pagina de busqueda de clientes."""
    return html.Div([
        # Header
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Inicio", style={
                        'color': '#aaa',
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
                'margin': '0', 'color': 'white', 'fontSize': '28px'
            }),
            html.P("Busca por razon social, nombre de fantasia o codigo de cliente",
                   style={'margin': '5px 0 0 0', 'color': '#ccc', 'fontSize': '14px'}),
        ], style={
            'backgroundColor': '#1a1a2e',
            'padding': '20px',
        }),

        # Buscador
        html.Div([
            html.Div([
                dmc.TextInput(
                    id='clientes-busqueda-input',
                    placeholder='Escribi el nombre o codigo del cliente...',
                    size='lg',
                    style={'width': '100%'},
                ),
                # Store para debounce (el clientside_callback lo actualiza con delay)
                dcc.Store(id='clientes-busqueda-debounced', data=''),
            ], style={
                'maxWidth': '600px',
                'margin': '0 auto',
                'padding': '30px 20px 20px 20px',
            }),

            # Resultados con loading indicator
            dcc.Loading(
                type='circle',
                color='#2980b9',
                children=html.Div(id='clientes-resultados', style={
                    'maxWidth': '900px',
                    'margin': '0 auto',
                    'padding': '0 20px 30px 20px',
                }),
            ),
        ], style={
            'backgroundColor': '#f5f7fa',
            'minHeight': 'calc(100vh - 130px)',
        }),
    ], style={'fontFamily': 'Arial, sans-serif'})
