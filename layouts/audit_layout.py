"""
Layout del panel de auditoría.
Solo accesible para usuarios con rol admin.
Muestra registros de actividad con filtros, paginación y exportación CSV.
"""
from dash import html, dcc
import dash_mantine_components as dmc
from config import DARK


def create_audit_layout():
    """Crea el layout del registro de auditoría."""

    dark_input_styles = {
        'input': {'backgroundColor': DARK['surface'], 'color': DARK['text'], 'borderColor': DARK['border']},
        'label': {'color': DARK['text_secondary']},
    }

    dark_select_styles = {
        **dark_input_styles,
        'dropdown': {'backgroundColor': DARK['surface'], 'borderColor': DARK['border']},
        'option': {'color': DARK['text']},
    }

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.Div([
                    dcc.Link("← Gestionar Usuarios", href='/admin/usuarios', style={
                        'color': DARK['accent_blue'], 'textDecoration': 'none',
                        'fontSize': '14px', 'fontWeight': '500',
                    }),
                ]),
                html.H2("Registro de Actividad", style={
                    'margin': '10px 0 0 0', 'color': DARK['text'], 'fontSize': '24px'
                }),
            ], style={'padding': '20px 40px'}),
        ], style={
            'backgroundColor': DARK['header'],
            'borderBottom': f'1px solid {DARK["border"]}'
        }),

        # Contenido principal
        html.Div([
            # Filtros
            html.Div([
                html.H3("Filtros", style={
                    'color': DARK['text'], 'marginBottom': '15px', 'fontSize': '18px'
                }),
                html.Div([
                    html.Div([
                        dmc.DatePickerInput(
                            id='audit-date-range',
                            type='range',
                            label='Rango de fechas',
                            placeholder='Seleccionar rango...',
                            styles=dark_input_styles,
                        ),
                    ], style={'flex': '1', 'minWidth': '220px'}),
                    html.Div([
                        dmc.Select(
                            id='audit-user-filter',
                            label='Usuario',
                            data=[],
                            placeholder='Todos',
                            clearable=True,
                            styles=dark_select_styles,
                        ),
                    ], style={'flex': '1', 'minWidth': '150px'}),
                    html.Div([
                        dmc.Select(
                            id='audit-action-filter',
                            label='Tipo de acción',
                            data=[
                                {'label': 'Todos', 'value': ''},
                                {'label': 'Vista de página', 'value': 'page_view'},
                                {'label': 'Inicio de sesión', 'value': 'login'},
                                {'label': 'Cierre de sesión', 'value': 'logout'},
                                {'label': 'Login fallido', 'value': 'login_failed'},
                                {'label': 'Cambio de filtro', 'value': 'filter_change'},
                                {'label': 'Acción admin', 'value': 'admin_action'},
                            ],
                            placeholder='Todos',
                            clearable=True,
                            styles=dark_select_styles,
                        ),
                    ], style={'flex': '1', 'minWidth': '160px'}),
                    html.Div([
                        dmc.TextInput(
                            id='audit-ip-filter',
                            label='Dirección IP',
                            placeholder='Filtrar por IP...',
                            styles=dark_input_styles,
                        ),
                    ], style={'flex': '1', 'minWidth': '140px'}),
                    html.Div([
                        dmc.Button(
                            "Buscar",
                            id='audit-search-btn',
                            color='blue',
                            style={'marginRight': '10px'},
                        ),
                        dmc.Button(
                            "Exportar CSV",
                            id='audit-export-btn',
                            variant='outline',
                            color='gray',
                        ),
                    ], style={
                        'display': 'flex', 'alignItems': 'flex-end',
                        'paddingBottom': '2px', 'gap': '8px',
                    }),
                ], style={
                    'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap',
                    'alignItems': 'flex-end',
                }),
            ], style={
                'backgroundColor': DARK['card'],
                'borderRadius': '10px',
                'padding': '25px',
                'marginBottom': '20px',
                'border': f'1px solid {DARK["border"]}'
            }),

            # Info de resultados
            html.Div(id='audit-results-info', style={
                'color': DARK['text_secondary'], 'fontSize': '14px',
                'marginBottom': '10px', 'padding': '0 5px',
            }),

            # Tabla de resultados
            html.Div([
                html.Div(id='audit-table-container'),
            ], style={
                'backgroundColor': DARK['card'],
                'borderRadius': '10px',
                'padding': '25px',
                'marginBottom': '20px',
                'border': f'1px solid {DARK["border"]}',
                'overflowX': 'auto',
            }),

            # Paginación
            html.Div([
                dmc.Button(
                    "← Anterior",
                    id='audit-prev-btn',
                    variant='outline',
                    color='gray',
                    size='sm',
                ),
                html.Span(id='audit-page-info', style={
                    'color': DARK['text_secondary'], 'fontSize': '14px',
                    'padding': '0 20px', 'alignSelf': 'center',
                }),
                dmc.Button(
                    "Siguiente →",
                    id='audit-next-btn',
                    variant='outline',
                    color='gray',
                    size='sm',
                ),
            ], style={
                'display': 'flex', 'justifyContent': 'center',
                'alignItems': 'center', 'marginBottom': '30px',
            }),

            # Hidden stores
            dcc.Store(id='audit-current-page', data=1),
            dcc.Store(id='audit-total-count', data=0),
            dcc.Download(id='audit-csv-download'),

        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '30px 20px',
        }),

    ], style={
        'backgroundColor': DARK['bg'],
        'minHeight': '100vh',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    })
