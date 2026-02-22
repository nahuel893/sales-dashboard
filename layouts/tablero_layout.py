"""
Layout del Tablero de Ventas — comparación anual con filtros.
"""
from dash import html, dcc
import dash_mantine_components as dmc
from config import DARK


def create_tablero_layout(fecha_min, fecha_max, fecha_desde_default, fecha_hasta_default,
                          lista_genericos, lista_marcas, lista_rutas, lista_preventistas,
                          lista_anios):
    """Crea y retorna el layout del Tablero de Ventas (comparación anual)."""

    # Estilo común para labels de sección
    label_style = {'fontWeight': 'bold', 'fontSize': '14px', 'color': DARK['text_secondary']}

    # Estilos oscuros para inputs dmc dentro del drawer
    dark_input_styles = {
        "input": {"backgroundColor": DARK['surface'], "borderColor": DARK['border'], "color": DARK['text']},
        "label": {"color": DARK['text_secondary']},
        "dropdown": {"backgroundColor": DARK['surface'], "borderColor": DARK['border']},
        "option": {"color": DARK['text'], "backgroundColor": DARK['surface']},
        "pill": {"backgroundColor": DARK['accent_blue'], "color": DARK['text']},
    }
    dark_combobox_props = {
        "zIndex": 1100,
        "styles": {
            "dropdown": {"backgroundColor": DARK['surface'], "borderColor": DARK['border']},
            "option": {"color": DARK['text'], "backgroundColor": DARK['surface']},
        },
    }
    dark_segmented_styles = {
        "root": {"backgroundColor": DARK['surface']},
        "label": {"color": DARK['text_secondary']},
        "indicator": {"backgroundColor": DARK['accent_blue']},
    }

    # Opciones de años pre-populadas
    anios_options = [{'label': str(a), 'value': str(a)} for a in lista_anios]

    return html.Div([
        # =================================================================
        # DRAWER DE FILTROS (mismo IDs que /ventas para reusar cascada)
        # =================================================================
        dmc.Drawer(
            id='drawer-filtros',
            title=dmc.Text("Filtros", fw=700, size="lg", c=DARK['text']),
            position="left",
            size="370px",
            padding="md",
            zIndex=1000,
            styles={
                "header": {"backgroundColor": DARK['card'], "borderBottom": f"1px solid {DARK['border']}"},
                "body": {"backgroundColor": DARK['card']},
                "content": {"backgroundColor": DARK['card']},
                "close": {"color": DARK['text_secondary']},
            },
            children=[
                dmc.ScrollArea(
                    h="calc(100vh - 80px)",
                    children=[
                        dmc.Stack(gap="md", children=[
                            # --- Fechas ---
                            dmc.Text("Fechas", fw=600, size="sm", c=DARK['text']),
                            dmc.DatePickerInput(
                                id='filtro-fechas',
                                label="Rango de Fechas",
                                type="range",
                                value=[str(fecha_desde_default), str(fecha_hasta_default)],
                                valueFormat="DD/MM/YYYY",
                                w="100%",
                                popoverProps={"zIndex": 1100},
                                styles=dark_input_styles,
                            ),
                            dmc.Divider(color=DARK['border']),

                            # --- Cliente ---
                            dmc.Text("Cliente", fw=600, size="sm", c=DARK['text']),
                            dmc.MultiSelect(
                                id='filtro-canal',
                                label="Canal",
                                data=[],
                                value=[],
                                placeholder="Todos los canales",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-subcanal',
                                label="Subcanal",
                                data=[],
                                value=[],
                                placeholder="Todos los subcanales",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-localidad',
                                label="Localidad",
                                data=[],
                                value=[],
                                placeholder="Todas las localidades",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-lista-precio',
                                label="Lista Precio",
                                data=[],
                                value=[],
                                placeholder="Todas las listas",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            html.Div([
                                html.Label("Tipo Sucursal", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                                dmc.SegmentedControl(
                                    id='filtro-tipo-sucursal',
                                    data=[
                                        {"label": "Todas", "value": "TODAS"},
                                        {"label": "Sucursales", "value": "SUCURSALES"},
                                        {"label": "Casa Central", "value": "CASA_CENTRAL"},
                                    ],
                                    value="TODAS",
                                    size="sm",
                                    fullWidth=True,
                                    styles=dark_segmented_styles,
                                ),
                            ]),
                            dmc.MultiSelect(
                                id='filtro-sucursal',
                                label="Sucursal",
                                data=[],
                                value=[],
                                placeholder="Todas las sucursales",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.Divider(color=DARK['border']),

                            # --- Producto ---
                            dmc.Text("Producto", fw=600, size="sm", c=DARK['text']),
                            dmc.MultiSelect(
                                id='filtro-generico',
                                label="Generico",
                                data=[g for g in lista_genericos],
                                value=[],
                                placeholder="Todos los genericos",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-marca',
                                label="Marca",
                                data=[m for m in lista_marcas],
                                value=[],
                                placeholder="Todas las marcas",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.Divider(color=DARK['border']),

                            # --- Metrica ---
                            dmc.Text("Metrica", fw=600, size="sm", c=DARK['text']),
                            dmc.SegmentedControl(
                                id='filtro-metrica',
                                data=[
                                    {"label": "Bultos", "value": "cantidad_total"},
                                    {"label": "Facturación", "value": "facturacion"},
                                    {"label": "Documentos", "value": "cantidad_documentos"},
                                ],
                                value="cantidad_total",
                                size="sm",
                                fullWidth=True,
                                styles=dark_segmented_styles,
                            ),
                            dmc.Divider(color=DARK['border']),

                            # --- Fuerza de Ventas ---
                            dmc.Text("Fuerza de Ventas", fw=600, size="sm", c=DARK['text']),
                            dmc.SegmentedControl(
                                id='filtro-fuerza-venta',
                                data=[
                                    {"label": "Todos", "value": "TODOS"},
                                    {"label": "FV1", "value": "FV1"},
                                    {"label": "FV4", "value": "FV4"},
                                ],
                                value="TODOS",
                                size="sm",
                                fullWidth=True,
                                styles=dark_segmented_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-ruta',
                                label="Ruta",
                                data=lista_rutas,
                                value=[],
                                placeholder="Todas las rutas",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                            dmc.MultiSelect(
                                id='filtro-preventista',
                                label="Preventista",
                                data=[p for p in lista_preventistas],
                                value=[],
                                placeholder="Todos los preventistas",
                                searchable=True,
                                clearable=True,
                                comboboxProps=dark_combobox_props,
                                styles=dark_input_styles,
                            ),
                        ]),
                    ],
                ),
            ],
        ),

        # Header con navegación
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Inicio", style={
                        'color': DARK['text_secondary'],
                        'fontSize': '14px',
                        'textDecoration': 'none',
                        'padding': '8px 15px',
                        'backgroundColor': 'rgba(255,255,255,0.1)',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }),
                    href='/',
                    style={'textDecoration': 'none'}
                ),
            ], style={'marginBottom': '10px'}),
            html.H1("Tablero de Ventas", style={'margin': '0', 'color': DARK['text']}),
            html.P("Comparación anual de ventas por mes",
                   style={'margin': '5px 0 0 0', 'color': DARK['text_secondary']})
        ], style={
            'backgroundColor': DARK['header'],
            'padding': '20px',
            'marginBottom': '0',
            'borderBottom': f'1px solid {DARK["border"]}'
        }),

        # Botón de Filtros
        html.Div([
            dmc.Button(
                "Filtros",
                id='btn-toggle-filtros',
                variant="light",
                leftSection=dmc.Text("☰", size="lg"),
                size="sm",
            ),
        ], style={
            'padding': '10px 20px',
            'backgroundColor': DARK['card'],
            'borderBottom': f'1px solid {DARK["border"]}',
        }),

        # =================================================================
        # CONTENIDO: Selector de años + gráfico + tabla
        # =================================================================

        # Selector de años para comparar
        html.Div([
            html.Div([
                dmc.MultiSelect(
                    id='selector-anios',
                    label="Seleccionar años a comparar",
                    data=anios_options,
                    value=[],
                    placeholder="Seleccione uno o más años",
                    searchable=True,
                    w=400,
                ),
            ], style={'display': 'inline-block', 'marginRight': '30px'}),
        ], style={'padding': '15px 20px', 'backgroundColor': DARK['surface'], 'borderBottom': f'2px solid {DARK["border"]}'}),

        # Gráfica de líneas - Comparación por Año
        html.Div([
            html.H5("Comparacion Anual (Enero - Diciembre)", style={'textAlign': 'center', 'marginBottom': '5px', 'color': DARK['text']}),
            dcc.Loading(
                id='loading-grafico-linea',
                type='circle',
                children=[dcc.Graph(id='grafico-linea-tiempo', style={'height': '500px'})]
            )
        ], style={'padding': '20px'}),

        # Tabla comparativa
        html.Div([
            html.H5("Tabla Comparativa por Mes", style={'textAlign': 'center', 'marginBottom': '15px', 'color': DARK['text']}),
            html.Div(id='tabla-comparativa-container', children=[
                html.P("Seleccione años para ver la comparación", style={'textAlign': 'center', 'color': DARK['text_muted']})
            ])
        ], style={'padding': '20px', 'backgroundColor': DARK['card'], 'margin': '0 20px 20px 20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.3)', 'border': f'1px solid {DARK["border"]}'}),

    ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': DARK['bg']})
