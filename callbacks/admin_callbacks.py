"""
Callbacks de administración de usuarios.
CRUD de usuarios, asignación de roles y sucursales.
"""
from dash import callback, Output, Input, State, html, no_update
from sqlalchemy.orm import Session

from config import DARK
from database import SessionLocal
from auth.models import User, Role, UserSucursal
from auth.utils import hash_password


def _obtener_sucursales_disponibles():
    """Obtiene las sucursales disponibles desde dim_cliente."""
    from database import engine
    import pandas as pd
    query = """
        SELECT DISTINCT id_sucursal, des_sucursal
        FROM gold.dim_cliente
        WHERE id_sucursal IS NOT NULL AND des_sucursal IS NOT NULL
        ORDER BY des_sucursal
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return [{'label': f"{row['des_sucursal']} ({row['id_sucursal']})",
                 'value': str(row['id_sucursal'])}
                for _, row in df.iterrows()]
    except Exception:
        return []


@callback(
    Output('admin-sucursales', 'data'),
    Input('admin-form-title', 'children'),  # trigger al cargar
)
def cargar_sucursales_disponibles(_):
    """Carga las sucursales para el MultiSelect."""
    return _obtener_sucursales_disponibles()


@callback(
    [Output('admin-users-table', 'children'),
     Output('admin-feedback', 'children')],
    [Input('admin-save-btn', 'n_clicks'),
     Input('admin-clear-btn', 'n_clicks')],
    [State('admin-edit-user-id', 'data'),
     State('admin-username', 'value'),
     State('admin-fullname', 'value'),
     State('admin-password', 'value'),
     State('admin-role', 'value'),
     State('admin-sucursales', 'value')],
)
def gestionar_usuarios(save_clicks, clear_clicks, edit_user_id,
                       username, fullname, password, role_name, sucursales_ids):
    """Guarda/crea usuario y refresca tabla."""
    from dash import ctx

    feedback = html.Div()

    # Si fue click en guardar
    if ctx.triggered_id == 'admin-save-btn' and save_clicks:
        feedback = _guardar_usuario(edit_user_id, username, fullname, password, role_name, sucursales_ids)

    # Generar tabla de usuarios
    tabla = _generar_tabla_usuarios()

    return tabla, feedback


def _guardar_usuario(edit_user_id, username, fullname, password, role_name, sucursales_ids):
    """Crea o actualiza un usuario."""
    if not username or not username.strip():
        return _feedback("Usuario requerido", 'error')
    if not fullname or not fullname.strip():
        return _feedback("Nombre completo requerido", 'error')

    db = SessionLocal()
    try:
        # Obtener rol
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return _feedback(f"Rol '{role_name}' no encontrado", 'error')

        if edit_user_id:
            # Editar existente
            user = db.query(User).get(edit_user_id)
            if not user:
                return _feedback("Usuario no encontrado", 'error')
            user.username = username.strip()
            user.full_name = fullname.strip()
            user.role_id = role.id
            if password and password.strip():
                user.password_hash = hash_password(password.strip())
            # Actualizar sucursales
            db.query(UserSucursal).filter(UserSucursal.user_id == user.id).delete()
            if sucursales_ids and role_name == 'supervisor':
                for sid in sucursales_ids:
                    db.add(UserSucursal(user_id=user.id, id_sucursal=int(sid)))
            db.commit()
            return _feedback(f"Usuario '{username}' actualizado", 'success')
        else:
            # Crear nuevo
            if not password or not password.strip():
                return _feedback("Contraseña requerida para nuevo usuario", 'error')
            existing = db.query(User).filter(User.username == username.strip()).first()
            if existing:
                return _feedback(f"El usuario '{username}' ya existe", 'error')

            user = User(
                username=username.strip(),
                full_name=fullname.strip(),
                password_hash=hash_password(password.strip()),
                role_id=role.id,
                is_active=True
            )
            db.add(user)
            db.flush()  # para obtener user.id

            if sucursales_ids and role_name == 'supervisor':
                for sid in sucursales_ids:
                    db.add(UserSucursal(user_id=user.id, id_sucursal=int(sid)))
            db.commit()
            return _feedback(f"Usuario '{username}' creado", 'success')
    except Exception as e:
        db.rollback()
        return _feedback(f"Error: {str(e)[:80]}", 'error')
    finally:
        db.close()


@callback(
    [Output('admin-edit-user-id', 'data'),
     Output('admin-username', 'value'),
     Output('admin-fullname', 'value'),
     Output('admin-password', 'value'),
     Output('admin-role', 'value'),
     Output('admin-sucursales', 'value'),
     Output('admin-form-title', 'children')],
    [Input('admin-clear-btn', 'n_clicks')],
    prevent_initial_call=True,
)
def limpiar_form(_):
    """Limpia el formulario."""
    return None, '', '', '', 'supervisor', [], 'Nuevo Usuario'


@callback(
    [Output('admin-edit-user-id', 'data', allow_duplicate=True),
     Output('admin-username', 'value', allow_duplicate=True),
     Output('admin-fullname', 'value', allow_duplicate=True),
     Output('admin-password', 'value', allow_duplicate=True),
     Output('admin-role', 'value', allow_duplicate=True),
     Output('admin-sucursales', 'value', allow_duplicate=True),
     Output('admin-form-title', 'children', allow_duplicate=True)],
    Input({'type': 'admin-edit-btn', 'index': __import__('dash').ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def editar_usuario(n_clicks_list):
    """Carga un usuario en el form para edición."""
    from dash import ctx

    if not ctx.triggered_id or not any(n for n in n_clicks_list if n):
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    user_id = ctx.triggered_id['index']

    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update

        sucursales_vals = [str(us.id_sucursal) for us in user.sucursales]
        return (
            user.id,
            user.username,
            user.full_name,
            '',  # no mostrar password
            user.role.name,
            sucursales_vals,
            f'Editando: {user.full_name}'
        )
    finally:
        db.close()


@callback(
    Output('admin-users-table', 'children', allow_duplicate=True),
    Input({'type': 'admin-toggle-btn', 'index': __import__('dash').ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def toggle_usuario_activo(n_clicks_list):
    """Activa/desactiva un usuario."""
    from dash import ctx

    if not ctx.triggered_id or not any(n for n in n_clicks_list if n):
        return no_update

    user_id = ctx.triggered_id['index']

    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if user:
            user.is_active = not user.is_active
            db.commit()
    finally:
        db.close()

    return _generar_tabla_usuarios()


def _generar_tabla_usuarios():
    """Genera la tabla HTML de usuarios."""
    db = SessionLocal()
    try:
        users = db.query(User).join(Role).order_by(Role.name, User.username).all()

        if not users:
            return html.P("No hay usuarios registrados.", style={'color': DARK['text_muted']})

        th_style = {
            'padding': '10px 12px', 'backgroundColor': DARK['surface'],
            'textAlign': 'left', 'fontSize': '13px', 'fontWeight': 'bold',
            'borderBottom': f'2px solid {DARK["border"]}', 'color': DARK['text_secondary'],
        }
        td_style = {
            'padding': '10px 12px', 'borderBottom': f'1px solid {DARK["border"]}',
            'fontSize': '13px', 'color': DARK['text'],
        }

        header = html.Tr([
            html.Th("Usuario", style=th_style),
            html.Th("Nombre", style=th_style),
            html.Th("Rol", style=th_style),
            html.Th("Sucursales", style=th_style),
            html.Th("Estado", style=th_style),
            html.Th("Acciones", style={**th_style, 'textAlign': 'center'}),
        ])

        rows = []
        for user in users:
            sucs = ', '.join(str(s) for s in user.sucursales_ids) if user.sucursales_ids else '-'
            estado_color = '#27ae60' if user.is_active else '#e74c3c'
            estado_text = 'Activo' if user.is_active else 'Inactivo'

            rows.append(html.Tr([
                html.Td(user.username, style=td_style),
                html.Td(user.full_name, style=td_style),
                html.Td(user.role.name.capitalize(), style={**td_style, 'fontWeight': 'bold'}),
                html.Td(sucs, style={**td_style, 'fontSize': '12px', 'color': DARK['text_muted']}),
                html.Td(estado_text, style={**td_style, 'color': estado_color, 'fontWeight': 'bold'}),
                html.Td([
                    html.Button("Editar", id={'type': 'admin-edit-btn', 'index': user.id},
                                style={
                                    'backgroundColor': DARK['accent_blue'], 'color': '#fff',
                                    'border': 'none', 'borderRadius': '4px', 'padding': '4px 10px',
                                    'cursor': 'pointer', 'fontSize': '12px', 'marginRight': '5px'
                                }),
                    html.Button(
                        "Desactivar" if user.is_active else "Activar",
                        id={'type': 'admin-toggle-btn', 'index': user.id},
                        style={
                            'backgroundColor': '#e74c3c' if user.is_active else '#27ae60',
                            'color': '#fff', 'border': 'none', 'borderRadius': '4px',
                            'padding': '4px 10px', 'cursor': 'pointer', 'fontSize': '12px'
                        }
                    ),
                ], style={**td_style, 'textAlign': 'center'}),
            ]))

        return html.Table(
            [html.Thead(header), html.Tbody(rows)],
            style={
                'width': '100%', 'borderCollapse': 'collapse',
                'backgroundColor': DARK['card'],
            }
        )
    finally:
        db.close()


def _feedback(msg, tipo='info'):
    """Crea un div de feedback con color según tipo."""
    colors = {
        'success': '#27ae60',
        'error': '#e74c3c',
        'info': DARK['text_secondary'],
    }
    return html.Div(msg, style={
        'color': colors.get(tipo, DARK['text']),
        'fontSize': '14px', 'fontWeight': '500',
        'padding': '8px 12px',
        'backgroundColor': DARK['surface'],
        'borderRadius': '6px',
        'border': f'1px solid {colors.get(tipo, DARK["border"])}',
    })
