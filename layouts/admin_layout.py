"""
Layout de administración de usuarios.
Solo accesible para usuarios con rol admin.
"""
from dash import html, dcc
import dash_mantine_components as dmc
from config import DARK


def create_admin_layout():
    """Crea el layout de gestión de usuarios."""

    dark_input_styles = {
        'input': {'backgroundColor': DARK['surface'], 'color': DARK['text'], 'borderColor': DARK['border']},
        'label': {'color': DARK['text_secondary']},
    }

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.Div([
                    dcc.Link("← Inicio", href='/', style={
                        'color': DARK['accent_blue'], 'textDecoration': 'none',
                        'fontSize': '14px', 'fontWeight': '500',
                    }),
                    html.Span(" | ", style={'color': DARK['text_muted'], 'margin': '0 8px'}),
                    dcc.Link("Ver Actividad →", href='/admin/audit', style={
                        'color': DARK['accent_blue'], 'textDecoration': 'none',
                        'fontSize': '14px', 'fontWeight': '500',
                    }),
                ]),
                html.H2("Gestión de Usuarios", style={
                    'margin': '10px 0 0 0', 'color': DARK['text'], 'fontSize': '24px'
                }),
            ], style={'padding': '20px 40px'}),
        ], style={
            'backgroundColor': DARK['header'],
            'borderBottom': f'1px solid {DARK["border"]}'
        }),

        # Contenido principal
        html.Div([
            # Form crear/editar usuario
            html.Div([
                html.H3("Nuevo Usuario", id='admin-form-title', style={
                    'color': DARK['text'], 'marginBottom': '20px', 'fontSize': '18px'
                }),

                dmc.TextInput(
                    id='admin-username',
                    label='Usuario',
                    placeholder='nombre.usuario',
                    styles=dark_input_styles,
                ),
                dmc.TextInput(
                    id='admin-fullname',
                    label='Nombre Completo',
                    placeholder='Nombre Apellido',
                    styles=dark_input_styles,
                    style={'marginTop': '12px'},
                ),
                dmc.PasswordInput(
                    id='admin-password',
                    label='Contraseña',
                    placeholder='Dejar vacío para no cambiar (edición)',
                    styles=dark_input_styles,
                    style={'marginTop': '12px'},
                ),
                dmc.Select(
                    id='admin-role',
                    label='Rol',
                    data=[
                        {'label': 'Admin', 'value': 'admin'},
                        {'label': 'Gerente', 'value': 'gerente'},
                        {'label': 'Supervisor', 'value': 'supervisor'},
                    ],
                    value='supervisor',
                    styles=dark_input_styles,
                    style={'marginTop': '12px'},
                ),
                dmc.MultiSelect(
                    id='admin-sucursales',
                    label='Sucursales (solo para Supervisor)',
                    data=[],  # se llena via callback
                    placeholder='Seleccionar sucursales...',
                    styles={
                        **dark_input_styles,
                        'dropdown': {'backgroundColor': DARK['surface'], 'borderColor': DARK['border']},
                        'option': {'color': DARK['text']},
                        'pill': {'backgroundColor': DARK['accent_blue'], 'color': DARK['text']},
                    },
                    style={'marginTop': '12px'},
                ),

                html.Div([
                    dmc.Button("Guardar", id='admin-save-btn', color='blue', style={'marginRight': '10px'}),
                    dmc.Button("Limpiar", id='admin-clear-btn', variant='outline', color='gray'),
                ], style={'marginTop': '20px', 'display': 'flex'}),

                # Store para modo edición
                dcc.Store(id='admin-edit-user-id', data=None),

                # Mensaje de feedback
                html.Div(id='admin-feedback', style={'marginTop': '15px'}),

            ], style={
                'backgroundColor': DARK['card'],
                'borderRadius': '10px',
                'padding': '25px',
                'marginBottom': '30px',
                'border': f'1px solid {DARK["border"]}'
            }),

            # Tabla de usuarios
            html.Div([
                html.H3("Usuarios", style={
                    'color': DARK['text'], 'marginBottom': '15px', 'fontSize': '18px'
                }),
                html.Div(id='admin-users-table'),
            ], style={
                'backgroundColor': DARK['card'],
                'borderRadius': '10px',
                'padding': '25px',
                'border': f'1px solid {DARK["border"]}'
            }),

        ], style={
            'maxWidth': '900px',
            'margin': '0 auto',
            'padding': '30px 20px',
        }),

    ], style={
        'backgroundColor': DARK['bg'],
        'minHeight': '100vh',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    })
