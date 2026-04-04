"""
Callbacks de autenticación: login y logout.
"""
from dash import callback, Output, Input, State, no_update
from flask import request as flask_request
from flask_login import login_user, logout_user, current_user

from auth.models import User
from auth.utils import check_password, hash_password, log_audit
from database import AuthSessionLocal


@callback(
    [Output('login-error', 'children'),
     Output('login-redirect', 'children')],
    Input('login-button', 'n_clicks'),
    [State('login-username', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Valida credenciales y hace login."""
    from dash import dcc
    if not n_clicks:
        return no_update, no_update

    if not username or not password:
        return "Ingrese usuario y contraseña", no_update

    db = AuthSessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if user and user.is_active and check_password(password, user.password_hash):
            if not user.password_hash.startswith('$2b$'):
                user.password_hash = hash_password(password)
                db.commit()
            login_user(user, remember=False)
            log_audit('login', path='/login')
            return "", dcc.Location(href='/', id='login-nav', refresh=True)
        log_audit('login_failed', path='/login')
        return "Usuario o contraseña incorrectos", no_update
    finally:
        db.close()
