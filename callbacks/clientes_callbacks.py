"""
Callbacks de la pagina de busqueda de clientes.
Busca clientes en dim_cliente y muestra resultados con links al detalle.
"""
from dash import callback, Output, Input, html, dcc, no_update, clientside_callback

from data.queries import buscar_clientes


# Debounce client-side: espera 350ms despues de la ultima tecla antes de disparar la busqueda
clientside_callback(
    """
    function(value) {
        if (window._searchDebounceTimer) {
            clearTimeout(window._searchDebounceTimer);
        }
        return new Promise(function(resolve) {
            window._searchDebounceTimer = setTimeout(function() {
                resolve(value || '');
            }, 350);
        });
    }
    """,
    Output('clientes-busqueda-debounced', 'data'),
    Input('clientes-busqueda-input', 'value'),
    prevent_initial_call=True
)


@callback(
    Output('clientes-resultados', 'children'),
    Input('clientes-busqueda-debounced', 'data'),
    prevent_initial_call=True
)
def buscar_y_mostrar_clientes(texto):
    """Busca clientes y muestra resultados como tabla."""
    if not texto or len(texto.strip()) < 2:
        return html.Div(
            "Escribi al menos 2 caracteres para buscar.",
            style={'textAlign': 'center', 'color': '#999', 'padding': '40px', 'fontSize': '15px'}
        )

    df = buscar_clientes(texto)

    if len(df) == 0:
        display_text = texto.strip()[:100]
        return html.Div(
            f'No se encontraron clientes para "{display_text}".',
            style={'textAlign': 'center', 'color': '#999', 'padding': '40px', 'fontSize': '15px'}
        )

    # Construir tabla de resultados
    th_style = {
        'padding': '10px 12px', 'backgroundColor': '#f0f0f0',
        'textAlign': 'left', 'fontSize': '13px', 'fontWeight': 'bold',
        'borderBottom': '2px solid #ddd',
    }
    td_style = {
        'padding': '10px 12px', 'borderBottom': '1px solid #eee',
        'fontSize': '13px', 'verticalAlign': 'middle',
    }

    header = html.Tr([
        html.Th("Cod", style={**th_style, 'width': '70px', 'textAlign': 'center'}),
        html.Th("Razon Social", style=th_style),
        html.Th("Fantasia", style=th_style),
        html.Th("Localidad", style=th_style),
        html.Th("Canal", style=th_style),
        html.Th("Sucursal", style=th_style),
    ])

    rows = []
    for row in df.itertuples(index=False):
        rows.append(html.Tr([
            html.Td(str(row.id_cliente), style={**td_style, 'textAlign': 'center', 'color': '#999'}),
            html.Td(
                dcc.Link(
                    row.razon_social,
                    href=f"/cliente/{row.id_cliente}",
                    target='_blank',
                    style={'color': '#2980b9', 'textDecoration': 'none', 'fontWeight': 'bold'}
                ),
                style=td_style
            ),
            html.Td(row.fantasia or '', style={**td_style, 'color': '#666'}),
            html.Td(row.localidad, style=td_style),
            html.Td(row.canal, style=td_style),
            html.Td(row.sucursal, style=td_style),
        ], style={'cursor': 'pointer', 'transition': 'background 0.15s'},
           className='fila-cliente'))

    tabla = html.Table(
        [html.Thead(header), html.Tbody(rows)],
        style={
            'width': '100%', 'borderCollapse': 'collapse',
            'backgroundColor': 'white', 'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        }
    )

    count_text = f"{len(df)} resultado{'s' if len(df) != 1 else ''}"
    if len(df) >= 50:
        count_text += " (mostrando primeros 50)"

    return html.Div([
        html.Div(count_text, style={
            'fontSize': '13px', 'color': '#999', 'marginBottom': '10px'
        }),
        tabla,
    ])
