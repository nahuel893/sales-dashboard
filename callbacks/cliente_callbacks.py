"""
Callbacks del detalle de cliente.
Carga informacion del cliente y construye arbol de ventas: generico -> marca -> articulo.
Muestra bultos por mes en columnas.
"""
from dash import callback, Output, Input, html
import dash_mantine_components as dmc
import pandas as pd

from data.queries import cargar_info_cliente, cargar_ventas_cliente_detalle

MESES_CORTOS = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


@callback(
    [Output('cliente-header-content', 'children'),
     Output('cliente-detail-content', 'children')],
    [Input('cliente-id-store', 'data')]
)
def cargar_detalle_cliente(store_data):
    """Carga datos del cliente y construye la vista de detalle."""
    if not store_data:
        return html.Div(), html.Div("No se encontro el cliente")

    id_cliente = store_data['id_cliente']

    # Cargar datos
    df_info = cargar_info_cliente(id_cliente)
    df_ventas = cargar_ventas_cliente_detalle(id_cliente)

    # === HEADER ===
    if len(df_info) > 0:
        info = df_info.iloc[0]
        header_children = [
            html.H1(info['razon_social'], style={
                'color': 'white', 'margin': '0', 'fontSize': '28px'
            }),
        ]
        if info.get('fantasia'):
            header_children.append(
                html.P(info['fantasia'], style={'color': '#ccc', 'margin': '5px 0 0 0', 'fontSize': '16px'})
            )
        # Badges de info
        badges = []
        for label, value in [
            ('Localidad', info['localidad']),
            ('Canal', info['canal']),
            ('Sucursal', info['sucursal']),
            ('Ramo', info['ramo']),
            ('Lista Precio', info['lista_precio']),
        ]:
            badges.append(html.Div([
                html.Span(f"{label}: ", style={'color': '#999', 'fontSize': '13px'}),
                html.Span(str(value), style={'color': 'white', 'fontSize': '13px', 'fontWeight': 'bold'}),
            ]))
        header_children.append(
            html.Div(badges, style={'display': 'flex', 'gap': '20px', 'marginTop': '12px', 'flexWrap': 'wrap'})
        )
        header = html.Div(header_children)
    else:
        header = html.H1(f"Cliente {id_cliente}", style={'color': 'white', 'margin': '0'})

    # === CONTENIDO ===
    if len(df_ventas) == 0:
        content = html.Div(
            "Este cliente no tiene ventas registradas.",
            style={'textAlign': 'center', 'color': '#666', 'padding': '60px', 'fontSize': '18px'}
        )
        return header, content

    # Obtener periodos ordenados cronologicamente
    periodos = sorted(df_ventas[['anio', 'mes']].drop_duplicates().values.tolist())

    # KPIs del mes corriente (ultimo periodo disponible)
    ultimo_anio, ultimo_mes = periodos[-1]
    df_mes = df_ventas[(df_ventas['anio'] == ultimo_anio) & (df_ventas['mes'] == ultimo_mes)]
    mes_bultos = df_mes['bultos'].sum()
    mes_genericos = df_mes['generico'].nunique()
    mes_articulos = df_mes['articulo'].nunique()
    mes_label = _periodo_label(ultimo_anio, ultimo_mes)

    resumen = html.Div([
        _resumen_card(f"Bultos {mes_label}", f"{mes_bultos:,.0f}"),
        _resumen_card(f"Categorias {mes_label}", f"{mes_genericos}"),
        _resumen_card(f"Articulos {mes_label}", f"{mes_articulos}"),
        _resumen_card("Meses con Ventas", f"{len(periodos)}"),
    ], style={
        'display': 'flex', 'gap': '20px', 'marginBottom': '25px', 'flexWrap': 'wrap'
    })

    # Arbol accordion
    tree = _build_generico_accordion(df_ventas, periodos)

    content = html.Div([resumen, tree])
    return header, content


def _resumen_card(label, value):
    """Crea una card de resumen."""
    return html.Div([
        html.Div(value, style={
            'fontSize': '28px', 'fontWeight': 'bold', 'color': '#1a1a2e'
        }),
        html.Div(label, style={'fontSize': '14px', 'color': '#666'}),
    ], style={
        'backgroundColor': 'white',
        'padding': '20px 30px',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'flex': '1',
        'minWidth': '150px',
    })


def _periodo_label(anio, mes):
    """Formatea un periodo como 'Ene 25'."""
    return f"{MESES_CORTOS[mes]} {str(anio)[2:]}"


def _build_generico_accordion(df_ventas, periodos):
    """Construye el accordion anidado: generico -> marca -> tabla articulos con meses."""
    generico_items = []

    # Agrupar por generico y ordenar por total de bultos desc
    gen_totals = df_ventas.groupby('generico')['bultos'].sum().sort_values(ascending=False)

    for generico in gen_totals.index:
        df_gen = df_ventas[df_ventas['generico'] == generico]
        gen_bultos = gen_totals[generico]

        # Accordion interno por marca
        marca_items = []
        marca_totals = df_gen.groupby('marca')['bultos'].sum().sort_values(ascending=False)

        for marca in marca_totals.index:
            df_marca = df_gen[df_gen['marca'] == marca]
            marca_bultos = marca_totals[marca]

            # Tabla de articulos con meses en columnas
            table = _build_articulo_table(df_marca, periodos)

            marca_items.append(
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        html.Div([
                            html.Span(marca, style={'fontWeight': 'bold'}),
                            html.Span(f" — {marca_bultos:,.0f} bultos",
                                      style={'color': '#666', 'marginLeft': '10px'}),
                        ]),
                    ),
                    dmc.AccordionPanel(table),
                ], value=f"{generico}-{marca}")
            )

        marca_accordion = dmc.Accordion(marca_items, variant="contained")

        generico_items.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    html.Div([
                        html.Span(generico, style={'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.Span(f" — {gen_bultos:,.0f} bultos",
                                  style={'color': '#666', 'marginLeft': '10px', 'fontSize': '14px'}),
                    ]),
                ),
                dmc.AccordionPanel(marca_accordion),
            ], value=generico)
        )

    return dmc.Accordion(generico_items, variant="separated")


def _build_articulo_table(df_marca, periodos):
    """Construye tabla HTML de articulos con columnas por mes."""
    th_style = {
        'padding': '8px 10px', 'backgroundColor': '#f0f0f0',
        'textAlign': 'center', 'fontSize': '12px', 'fontWeight': 'bold',
        'borderBottom': '2px solid #ddd', 'whiteSpace': 'nowrap'
    }
    th_left = {**th_style, 'textAlign': 'left', 'minWidth': '180px', 'position': 'sticky', 'left': '0', 'zIndex': '1'}
    th_total = {**th_style, 'backgroundColor': '#e0e7ef', 'minWidth': '70px'}
    td_style = {
        'padding': '6px 10px', 'borderBottom': '1px solid #eee', 'fontSize': '12px',
        'textAlign': 'right', 'whiteSpace': 'nowrap'
    }
    td_left = {
        'padding': '6px 10px', 'borderBottom': '1px solid #eee', 'fontSize': '12px',
        'textAlign': 'left', 'position': 'sticky', 'left': '0', 'backgroundColor': 'white', 'zIndex': '1'
    }
    td_total = {**td_style, 'fontWeight': 'bold', 'backgroundColor': '#f5f8fc'}

    # Header: Articulo | Ene 25 | Feb 25 | ... | Total
    header_cells = [html.Th("Articulo", style=th_left)]
    for anio, mes in periodos:
        header_cells.append(html.Th(_periodo_label(anio, mes), style=th_style))
    header_cells.append(html.Th("Total", style=th_total))
    header = html.Tr(header_cells)

    # Pivotar datos: articulo -> {(anio, mes): bultos}
    pivot = df_marca.groupby(['articulo', 'anio', 'mes'])['bultos'].sum()

    # Ordenar articulos por total desc
    art_totals = df_marca.groupby('articulo')['bultos'].sum().sort_values(ascending=False)

    rows = []
    for articulo in art_totals.index:
        total = art_totals[articulo]
        cells = [html.Td(articulo, style=td_left)]
        for anio, mes in periodos:
            try:
                val = pivot.loc[(articulo, anio, mes)]
                cells.append(html.Td(f"{val:,.0f}", style=td_style))
            except KeyError:
                cells.append(html.Td("", style=td_style))
        cells.append(html.Td(f"{total:,.0f}", style=td_total))
        rows.append(html.Tr(cells))

    # Fila de totales por mes
    total_cells = [html.Td("Total", style={**td_left, 'fontWeight': 'bold'})]
    mes_totals = df_marca.groupby(['anio', 'mes'])['bultos'].sum()
    for anio, mes in periodos:
        try:
            val = mes_totals.loc[(anio, mes)]
            total_cells.append(html.Td(f"{val:,.0f}", style={**td_style, 'fontWeight': 'bold'}))
        except KeyError:
            total_cells.append(html.Td("", style=td_style))
    total_cells.append(html.Td(f"{df_marca['bultos'].sum():,.0f}", style={**td_total, 'borderTop': '2px solid #999'}))
    rows.append(html.Tr(total_cells, style={'backgroundColor': '#f9f9f9'}))

    return html.Div(
        html.Table(
            [html.Thead(header), html.Tbody(rows)],
            style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'}
        ),
        style={'overflowX': 'auto', 'maxWidth': '100%'}
    )
