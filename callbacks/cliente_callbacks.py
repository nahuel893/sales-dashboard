"""
Callbacks del detalle de cliente.
Carga informacion del cliente y construye arbol de ventas: generico -> marca -> articulo.
Muestra bultos por mes en columnas. Articulos sin venta aparecen con 0.
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

    # Cargar datos (2 queries: info cliente + todos los articulos con/sin venta)
    df_info = cargar_info_cliente(id_cliente)
    df_all = cargar_ventas_cliente_detalle(id_cliente)

    # === HEADER ===
    if len(df_info) > 0:
        info = df_info.iloc[0]
        header_children = [
            html.H1([
                info['razon_social'],
                html.Span(f"  [{id_cliente}]", style={'fontSize': '16px', 'color': '#999', 'fontWeight': 'normal'}),
            ], style={
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
    if len(df_all) == 0:
        content = html.Div(
            "No hay articulos disponibles.",
            style={'textAlign': 'center', 'color': '#666', 'padding': '60px', 'fontSize': '18px'}
        )
        return header, content

    # Separar articulos con y sin venta (bultos NULL = sin venta)
    df_con_venta = df_all.dropna(subset=['bultos'])
    df_con_venta = df_con_venta.copy()
    df_con_venta['bultos'] = df_con_venta['bultos'].astype(float)

    # Articulos sin venta: filas con bultos NULL (sin ningun periodo)
    arts_con_venta = set(df_con_venta['id_articulo'].unique())
    df_sin_venta_arts = df_all[~df_all['id_articulo'].isin(arts_con_venta)].drop_duplicates(subset=['id_articulo'])

    # Periodos solo de articulos con venta
    periodos = sorted(
        df_con_venta[['anio', 'mes']].drop_duplicates().values.tolist()
    ) if len(df_con_venta) > 0 else []

    # Rearmar df_all: con_venta + sin_venta con bultos=0
    if len(df_sin_venta_arts) > 0:
        df_sv = df_sin_venta_arts[['id_articulo', 'generico', 'marca', 'articulo']].copy()
        df_sv['anio'] = pd.NA
        df_sv['mes'] = pd.NA
        df_sv['bultos'] = 0.0
        df_all = pd.concat([df_con_venta, df_sv], ignore_index=True)
    else:
        df_all = df_con_venta

    # KPIs del mes corriente (ultimo periodo disponible)
    if len(periodos) > 0:
        ultimo_anio, ultimo_mes = periodos[-1]
        df_mes = df_con_venta[(df_con_venta['anio'] == ultimo_anio) & (df_con_venta['mes'] == ultimo_mes)]
        mes_bultos = df_mes['bultos'].sum()
        mes_genericos = df_mes['generico'].nunique()
        mes_articulos = df_mes['articulo'].nunique()
        mes_label = _periodo_label(int(ultimo_anio), int(ultimo_mes))
    else:
        mes_bultos = 0
        mes_genericos = 0
        mes_articulos = 0
        mes_label = "—"

    n_con_venta = df_con_venta['id_articulo'].nunique() if len(df_con_venta) > 0 else 0
    n_sin_venta = len(df_sin_venta_arts)

    resumen = html.Div([
        _resumen_card(f"Bultos {mes_label}", f"{mes_bultos:,.0f}"),
        _resumen_card(f"Categorias {mes_label}", f"{mes_genericos}"),
        _resumen_card(f"Articulos {mes_label}", f"{mes_articulos}"),
        _resumen_card("Con Venta", f"{n_con_venta}"),
        _resumen_card("Sin Venta", f"{n_sin_venta}"),
    ], style={
        'display': 'flex', 'gap': '20px', 'marginBottom': '25px', 'flexWrap': 'wrap'
    })

    # Arbol accordion con todos los articulos
    tree = _build_generico_accordion(df_all, periodos)

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


def _build_generico_accordion(df_all, periodos):
    """Construye el accordion anidado: generico -> marca -> tabla articulos con meses."""
    generico_items = []

    # Agrupar por generico y ordenar por total de bultos desc
    gen_totals = df_all.groupby('generico')['bultos'].sum().sort_values(ascending=False)

    for generico in gen_totals.index:
        df_gen = df_all[df_all['generico'] == generico]
        gen_bultos = gen_totals[generico]

        # Accordion interno por marca
        marca_items = []
        marca_totals = df_gen.groupby('marca')['bultos'].sum().sort_values(ascending=False)

        for marca in marca_totals.index:
            df_marca = df_gen[df_gen['marca'] == marca]
            marca_bultos = marca_totals[marca]

            # Tabla de articulos con meses en columnas
            table = _build_articulo_table(df_marca, periodos)

            btn_style = {
                'padding': '4px 12px', 'fontSize': '12px', 'cursor': 'pointer',
                'border': '1px solid #ccc', 'borderRadius': '4px', 'backgroundColor': '#fff',
            }
            botones = html.Div([
                html.Button("Imprimir", className='btn-imprimir-marca',
                            **{'data-generico': generico, 'data-marca': marca},
                            style=btn_style),
                html.Button("Descargar PNG", className='btn-descargar-marca',
                            **{'data-generico': generico, 'data-marca': marca},
                            style=btn_style),
            ], style={'marginBottom': '8px', 'display': 'flex', 'gap': '8px'})

            marca_items.append(
                dmc.AccordionItem([
                    dmc.AccordionControl(
                        html.Div([
                            html.Span(marca, style={'fontWeight': 'bold'}),
                            html.Span(f" — {marca_bultos:,.0f} bultos",
                                      style={'color': '#666', 'marginLeft': '10px'}),
                        ]),
                    ),
                    dmc.AccordionPanel(html.Div([
                        botones,
                        html.Div(table, className='tabla-marca-content'),
                    ])),
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
    td_zero = {**td_style, 'color': '#ccc'}
    td_total_zero = {**td_total, 'color': '#ccc'}

    # Mapa de id_articulo por nombre
    art_ids = df_marca.groupby('articulo')['id_articulo'].first().to_dict()

    # Header: Cod | Articulo | Ene 25 | Feb 25 | ... | Total
    th_cod = {**th_style, 'textAlign': 'center', 'minWidth': '60px'}
    header_cells = [html.Th("Cod", style=th_cod), html.Th("Articulo", style=th_left)]
    for anio, mes in periodos:
        header_cells.append(html.Th(_periodo_label(anio, mes), style=th_style))
    header_cells.append(html.Th("Total", style=th_total))
    header = html.Tr(header_cells)

    # Filtrar solo filas con anio/mes valido para pivot
    df_con_periodos = df_marca.dropna(subset=['anio', 'mes'])
    if len(df_con_periodos) > 0:
        pivot = df_con_periodos.groupby(['articulo', 'anio', 'mes'])['bultos'].sum().to_dict()
    else:
        pivot = {}

    # Totales por articulo (incluye sin venta con 0)
    art_totals = df_marca.groupby('articulo')['bultos'].sum().sort_values(ascending=False)

    rows = []
    for articulo in art_totals.index:
        total = art_totals[articulo]
        is_zero = total == 0
        cod = art_ids.get(articulo, '')
        td_cod = {'padding': '6px 10px', 'borderBottom': '1px solid #eee', 'fontSize': '11px',
                  'textAlign': 'center', 'color': '#999'}
        cells = [
            html.Td(str(cod), style={**td_cod, 'color': '#ccc'} if is_zero else td_cod),
            html.Td(articulo, style={**td_left, 'color': '#bbb'} if is_zero else td_left),
        ]
        for anio, mes in periodos:
            val = pivot.get((articulo, anio, mes))
            if val is not None:
                cells.append(html.Td(f"{val:,.0f}", style=td_zero if val == 0 else td_style))
            else:
                cells.append(html.Td("", style=td_style))
        cells.append(html.Td(f"{total:,.0f}", style=td_total_zero if is_zero else td_total))
        rows.append(html.Tr(cells))

    # Fila de totales por mes
    if len(df_con_periodos) > 0:
        total_cells = [html.Td("", style={'padding': '6px 10px', 'borderBottom': '1px solid #eee'}),
                       html.Td("Total", style={**td_left, 'fontWeight': 'bold'})]
        mes_totals = df_con_periodos.groupby(['anio', 'mes'])['bultos'].sum().to_dict()
        for anio, mes in periodos:
            val = mes_totals.get((anio, mes))
            if val is not None:
                total_cells.append(html.Td(f"{val:,.0f}", style={**td_style, 'fontWeight': 'bold'}))
            else:
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
