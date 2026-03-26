"""
Callbacks del panel de auditoría.
Consulta, paginación y exportación CSV de registros de actividad.
"""
import json
from datetime import datetime, date

import pandas as pd
from dash import callback, Output, Input, State, html, no_update, ctx
from sqlalchemy import func

from config import DARK
from database import AuthSessionLocal
from auth.models import AuditLog

PAGE_SIZE = 50


def _build_audit_query(db, date_range, username, action_type, ip_filter):
    """Construye la query base con filtros aplicados."""
    query = db.query(AuditLog)

    if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
        try:
            fecha_desde = date_range[0]
            fecha_hasta = date_range[1]
            if isinstance(fecha_desde, str):
                fecha_desde = datetime.fromisoformat(fecha_desde.replace('Z', ''))
            if isinstance(fecha_hasta, str):
                fecha_hasta = datetime.fromisoformat(fecha_hasta.replace('Z', ''))
            # Si es date, convertir a datetime al final del día para fecha_hasta
            if isinstance(fecha_desde, date) and not isinstance(fecha_desde, datetime):
                fecha_desde = datetime.combine(fecha_desde, datetime.min.time())
            if isinstance(fecha_hasta, date) and not isinstance(fecha_hasta, datetime):
                fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())
            query = query.filter(AuditLog.timestamp >= fecha_desde)
            query = query.filter(AuditLog.timestamp <= fecha_hasta)
        except (ValueError, TypeError):
            pass

    if username and username.strip():
        query = query.filter(AuditLog.username == username.strip())

    if action_type and action_type.strip():
        query = query.filter(AuditLog.action_type == action_type.strip())

    if ip_filter and ip_filter.strip():
        query = query.filter(AuditLog.ip_address.contains(ip_filter.strip()))

    return query


def _generar_tabla_audit(registros):
    """Genera la tabla HTML de registros de auditoría."""
    if not registros:
        return html.P("No se encontraron registros.", style={'color': DARK['text_muted']})

    th_style = {
        'padding': '10px 12px', 'backgroundColor': DARK['surface'],
        'textAlign': 'left', 'fontSize': '12px', 'fontWeight': 'bold',
        'borderBottom': f'2px solid {DARK["border"]}', 'color': DARK['text_secondary'],
        'whiteSpace': 'nowrap',
    }
    td_style = {
        'padding': '8px 12px', 'borderBottom': f'1px solid {DARK["border"]}',
        'fontSize': '12px', 'color': DARK['text'], 'verticalAlign': 'top',
    }

    header = html.Tr([
        html.Th("Fecha/Hora", style=th_style),
        html.Th("Usuario", style=th_style),
        html.Th("IP", style=th_style),
        html.Th("Acción", style=th_style),
        html.Th("Ruta", style=th_style),
        html.Th("User-Agent", style=th_style),
        html.Th("Filtros", style=th_style),
        html.Th("Status", style=th_style),
    ])

    action_labels = {
        'page_view': ('Vista', DARK['accent_blue']),
        'login': ('Login', DARK['accent_green']),
        'logout': ('Logout', DARK['accent_orange']),
        'login_failed': ('Login fallido', DARK['accent_red']),
        'filter_change': ('Filtro', DARK['accent_purple']),
        'admin_action': ('Admin', DARK['accent_yellow']),
    }

    rows = []
    for reg in registros:
        # Formato de timestamp
        ts = reg.timestamp.strftime('%d/%m/%Y %H:%M:%S') if reg.timestamp else '—'

        # Acción con color
        label, color = action_labels.get(reg.action_type, (reg.action_type, DARK['text']))
        action_cell = html.Span(label, style={
            'color': color, 'fontWeight': 'bold', 'fontSize': '11px',
            'backgroundColor': DARK['surface'], 'padding': '2px 8px',
            'borderRadius': '4px',
        })

        # User-Agent truncado
        ua = reg.user_agent or '—'
        if len(ua) > 40:
            ua = ua[:40] + '...'

        # Filter data truncado
        filter_text = '—'
        if reg.filter_data:
            try:
                data = json.loads(reg.filter_data)
                filter_text = json.dumps(data, ensure_ascii=False)
                if len(filter_text) > 60:
                    filter_text = filter_text[:60] + '...'
            except (json.JSONDecodeError, TypeError):
                filter_text = str(reg.filter_data)[:60]

        rows.append(html.Tr([
            html.Td(ts, style=td_style),
            html.Td(reg.username or '—', style=td_style),
            html.Td(reg.ip_address or '—', style={**td_style, 'fontFamily': 'monospace', 'fontSize': '11px'}),
            html.Td(action_cell, style=td_style),
            html.Td(reg.path or '—', style={**td_style, 'fontFamily': 'monospace', 'fontSize': '11px'}),
            html.Td(ua, style={**td_style, 'fontSize': '11px', 'color': DARK['text_muted'], 'maxWidth': '200px'}),
            html.Td(filter_text, style={**td_style, 'fontSize': '11px', 'color': DARK['text_muted'], 'maxWidth': '250px'}),
            html.Td(str(reg.response_status) if reg.response_status else '—', style=td_style),
        ]))

    return html.Table(
        [html.Thead(header), html.Tbody(rows)],
        style={
            'width': '100%', 'borderCollapse': 'collapse',
            'backgroundColor': DARK['card'],
        }
    )


@callback(
    Output('audit-user-filter', 'data'),
    Input('audit-search-btn', 'n_clicks'),
    prevent_initial_call=False,
)
def cargar_usuarios_audit(_):
    """Carga la lista de usuarios distintos en el filtro."""
    db = AuthSessionLocal()
    try:
        usernames = (
            db.query(AuditLog.username)
            .filter(AuditLog.username.isnot(None))
            .distinct()
            .order_by(AuditLog.username)
            .all()
        )
        return [{'label': u[0], 'value': u[0]} for u in usernames if u[0]]
    except Exception:
        return []
    finally:
        db.close()


@callback(
    [Output('audit-table-container', 'children'),
     Output('audit-results-info', 'children'),
     Output('audit-page-info', 'children'),
     Output('audit-total-count', 'data')],
    [Input('audit-search-btn', 'n_clicks'),
     Input('audit-current-page', 'data')],
    [State('audit-date-range', 'value'),
     State('audit-user-filter', 'value'),
     State('audit-action-filter', 'value'),
     State('audit-ip-filter', 'value')],
)
def buscar_audit_logs(_, page, date_range, username, action_type, ip_filter):
    """Busca registros de auditoría con filtros y paginación."""
    if page is None or page < 1:
        page = 1

    db = AuthSessionLocal()
    try:
        query = _build_audit_query(db, date_range, username, action_type, ip_filter)

        # Total de registros
        total = query.count()
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        # Asegurar página válida
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * PAGE_SIZE
        registros = (
            query
            .order_by(AuditLog.timestamp.desc())
            .offset(offset)
            .limit(PAGE_SIZE)
            .all()
        )

        tabla = _generar_tabla_audit(registros)
        info = f"Mostrando {len(registros)} de {total} registros"
        page_info = f"Página {page} de {total_pages}"

        return tabla, info, page_info, total
    except Exception as e:
        return (
            html.P(f"Error al cargar registros: {str(e)[:100]}", style={'color': DARK['accent_red']}),
            "", "Página 1 de 1", 0
        )
    finally:
        db.close()


@callback(
    Output('audit-current-page', 'data'),
    [Input('audit-prev-btn', 'n_clicks'),
     Input('audit-next-btn', 'n_clicks')],
    [State('audit-current-page', 'data'),
     State('audit-total-count', 'data')],
    prevent_initial_call=True,
)
def actualizar_pagina(prev_clicks, next_clicks, current_page, total_count):
    """Actualiza el número de página al hacer click en anterior/siguiente."""
    if current_page is None:
        current_page = 1
    if total_count is None:
        total_count = 0

    total_pages = max(1, (total_count + PAGE_SIZE - 1) // PAGE_SIZE)

    triggered = ctx.triggered_id

    if triggered == 'audit-prev-btn':
        return max(1, current_page - 1)
    elif triggered == 'audit-next-btn':
        return min(total_pages, current_page + 1)

    return current_page


@callback(
    Output('audit-csv-download', 'data'),
    Input('audit-export-btn', 'n_clicks'),
    [State('audit-date-range', 'value'),
     State('audit-user-filter', 'value'),
     State('audit-action-filter', 'value'),
     State('audit-ip-filter', 'value')],
    prevent_initial_call=True,
)
def exportar_csv(n_clicks, date_range, username, action_type, ip_filter):
    """Exporta los registros filtrados a CSV."""
    if not n_clicks:
        return no_update

    db = AuthSessionLocal()
    try:
        query = _build_audit_query(db, date_range, username, action_type, ip_filter)
        registros = query.order_by(AuditLog.timestamp.desc()).limit(5000).all()

        if not registros:
            return no_update

        data = [{
            'Fecha/Hora': r.timestamp.strftime('%d/%m/%Y %H:%M:%S') if r.timestamp else '',
            'Usuario': r.username or '',
            'IP': r.ip_address or '',
            'Acción': r.action_type or '',
            'Ruta': r.path or '',
            'User-Agent': r.user_agent or '',
            'Filtros': r.filter_data or '',
            'Status': r.response_status or '',
        } for r in registros]

        df = pd.DataFrame(data)
        from dash import dcc
        return dcc.send_data_frame(df.to_csv, "audit_log.csv", index=False)
    except Exception:
        return no_update
    finally:
        db.close()
