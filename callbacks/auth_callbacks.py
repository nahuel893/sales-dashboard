"""
Callbacks de autenticación: login y logout.
"""
from dash import callback, Output, Input, State, no_update
from flask import request as flask_request
from flask_login import login_user, logout_user, current_user

from auth.models import User
from auth.utils import check_password
from database import SessionLocal


@callback(
    [Output('login-error', 'children'),
     Output('login-url', 'href')],
    Input('login-button', 'n_clicks'),
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Valida credenciales y hace login."""
    if not n_clicks:
        return no_update, no_update

    if not username or not password:
        return "Ingrese usuario y contraseña", no_update

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if user and user.is_active and check_password(password, user.password_hash):
            login_user(user, remember=True)
            return "", "/"
        return "Usuario o contraseña incorrectos", no_update
    finally:
        db.close()
