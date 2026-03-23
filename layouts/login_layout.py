"""
Layout de la página de login.
"""
from dash import html, dcc
import dash_mantine_components as dmc
from config import DARK


def create_login_layout():
    """Crea el layout de la página de login con dark theme."""
    input_styles = {
        'input': {'backgroundColor': DARK['surface'], 'borderColor': DARK['border'], 'color': DARK['text']},
        'label': {'color': DARK['text_secondary']},
    }

    return html.Div([
        html.Div(id='login-redirect'),
        html.Div([
            html.Div([
                html.H1("Medallion ETL", style={
                    'textAlign': 'center', 'color': DARK['text'],
                    'marginBottom': '5px', 'fontSize': '28px'
                }),
                html.P("Iniciar sesión", style={
                    'textAlign': 'center', 'color': DARK['text_secondary'],
                    'marginBottom': '30px', 'fontSize': '14px'
                }),

                dmc.TextInput(
                    id='login-username',
                    label='Usuario',
                    placeholder='Ingrese su usuario',
                    styles=input_styles,
                    mb='md',
                ),
                dmc.PasswordInput(
                    id='login-password',
                    label='Contraseña',
                    placeholder='Ingrese su contraseña',
                    styles=input_styles,
                    mb='lg',
                ),

                html.Div(id='login-error', style={
                    'color': DARK['accent_red'], 'textAlign': 'center',
                    'marginBottom': '15px', 'fontSize': '13px'
                }),

                dmc.Button(
                    'Ingresar',
                    id='login-button',
                    fullWidth=True,
                    color='blue',
                    size='md',
                ),

            ], style={
                'backgroundColor': DARK['card'],
                'padding': '40px',
                'borderRadius': '12px',
                'width': '380px',
                'border': f'1px solid {DARK["border"]}',
                'boxShadow': '0 8px 32px rgba(0, 0, 0, 0.4)',
            }),
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'minHeight': '100vh',
            'backgroundColor': DARK['bg'],
        })
    ], style={
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    })
