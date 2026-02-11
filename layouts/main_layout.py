"""
Layout principal del dashboard de ventas.
"""
from dash import html, dcc
import dash_mantine_components as dmc


def create_ventas_layout(fecha_min, fecha_max, fecha_desde_default, lista_genericos, lista_marcas, lista_rutas, lista_preventistas):
    """Crea y retorna el layout del dashboard de ventas."""

    # Estilo común para labels de sección
    label_style = {'fontWeight': 'bold', 'fontSize': '14px', 'color': '#333'}

    # Helper: stack vertical de filtros con separación
    def filtro_stack(children):
        return dmc.Stack(children, gap="sm")

    return html.Div([
        # Div oculto para clientside callback de click en mapa
        html.Div(id='click-output-dummy', style={'display': 'none'}),

        # =================================================================
        # DRAWER DE FILTROS (panel lateral colapsable)
        # =================================================================
        dmc.Drawer(
            id='drawer-filtros',
            title=dmc.Text("Filtros", fw=700, size="lg"),
            position="left",
            size="370px",
            padding="md",
            zIndex=1000,
            children=[
                dmc.ScrollArea(
                    h="calc(100vh - 80px)",
                    children=[
                        dmc.Accordion(
                            multiple=True,
                            value=["fechas", "cliente", "producto", "metrica", "fuerza-ventas", "opciones-mapa"],
                            children=[
                                # --- Fechas ---
                                dmc.AccordionItem(
                                    value="fechas",
                                    children=[
                                        dmc.AccordionControl("Fechas"),
                                        dmc.AccordionPanel(
                                            dmc.DatePickerInput(
                                                id='filtro-fechas',
                                                label="Rango de Fechas",
                                                type="range",
                                                value=[str(fecha_desde_default), str(fecha_max)],
                                                valueFormat="DD/MM/YYYY",
                                                w="100%",
                                                popoverProps={"zIndex": 1100},
                                            ),
                                        ),
                                    ],
                                ),

                                # --- Cliente ---
                                dmc.AccordionItem(
                                    value="cliente",
                                    children=[
                                        dmc.AccordionControl("Cliente"),
                                        dmc.AccordionPanel(
                                            filtro_stack([
                                                dmc.MultiSelect(
                                                    id='filtro-canal',
                                                    label="Canal",
                                                    data=[],
                                                    value=[],
                                                    placeholder="Todos los canales",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                                dmc.MultiSelect(
                                                    id='filtro-subcanal',
                                                    label="Subcanal",
                                                    data=[],
                                                    value=[],
                                                    placeholder="Todos los subcanales",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                                dmc.MultiSelect(
                                                    id='filtro-localidad',
                                                    label="Localidad",
                                                    data=[],
                                                    value=[],
                                                    placeholder="Todas las localidades",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                                dmc.MultiSelect(
                                                    id='filtro-lista-precio',
                                                    label="Lista Precio",
                                                    data=[],
                                                    value=[],
                                                    placeholder="Todas las listas",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
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
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                            ]),
                                        ),
                                    ],
                                ),

                                # --- Producto ---
                                dmc.AccordionItem(
                                    value="producto",
                                    children=[
                                        dmc.AccordionControl("Producto"),
                                        dmc.AccordionPanel(
                                            filtro_stack([
                                                dmc.MultiSelect(
                                                    id='filtro-generico',
                                                    label="Generico",
                                                    data=[g for g in lista_genericos],
                                                    value=[],
                                                    placeholder="Todos los genericos",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                                dmc.MultiSelect(
                                                    id='filtro-marca',
                                                    label="Marca",
                                                    data=[m for m in lista_marcas],
                                                    value=[],
                                                    placeholder="Todas las marcas",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                            ]),
                                        ),
                                    ],
                                ),

                                # --- Metrica ---
                                dmc.AccordionItem(
                                    value="metrica",
                                    children=[
                                        dmc.AccordionControl("Metrica"),
                                        dmc.AccordionPanel(
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
                                            ),
                                        ),
                                    ],
                                ),

                                # --- Fuerza de Ventas ---
                                dmc.AccordionItem(
                                    value="fuerza-ventas",
                                    children=[
                                        dmc.AccordionControl("Fuerza de Ventas"),
                                        dmc.AccordionPanel(
                                            filtro_stack([
                                                html.Div([
                                                    html.Label("Fuerza de Ventas", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
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
                                                    ),
                                                ]),
                                                dmc.MultiSelect(
                                                    id='filtro-ruta',
                                                    label="Ruta",
                                                    data=lista_rutas,
                                                    value=[],
                                                    placeholder="Todas las rutas",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                                dmc.MultiSelect(
                                                    id='filtro-preventista',
                                                    label="Preventista",
                                                    data=[p for p in lista_preventistas],
                                                    value=[],
                                                    placeholder="Todos los preventistas",
                                                    searchable=True,
                                                    clearable=True,
                                                    comboboxProps={"zIndex": 1100},
                                                ),
                                            ]),
                                        ),
                                    ],
                                ),

                                # --- Opciones de Mapa ---
                                dmc.AccordionItem(
                                    value="opciones-mapa",
                                    children=[
                                        dmc.AccordionControl("Opciones de Mapa"),
                                        dmc.AccordionPanel(
                                            filtro_stack([
                                                html.Div([
                                                    html.Label("Mostrar zonas", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                                                    dmc.ChipGroup(
                                                        id='opciones-zonas',
                                                        children=[
                                                            dmc.Chip("Zonas por Ruta", value="ruta"),
                                                            dmc.Chip("Zonas por Preventista", value="preventista"),
                                                        ],
                                                        value=[],
                                                        multiple=True,
                                                    ),
                                                ]),
                                                dmc.Switch(
                                                    id='opcion-escala-log',
                                                    label="Escala Logaritmica",
                                                    checked=True,
                                                    size="sm",
                                                ),
                                                html.Div([
                                                    html.Label("Tipo mapa calor", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                                                    dmc.SegmentedControl(
                                                        id='tipo-mapa-calor',
                                                        data=[
                                                            {"label": "Difuso", "value": "density"},
                                                            {"label": "Grilla", "value": "grilla"},
                                                        ],
                                                        value="density",
                                                        size="sm",
                                                        fullWidth=True,
                                                    ),
                                                ]),
                                                html.Div([
                                                    html.Label("Tamano celda", style={**label_style, 'display': 'block', 'marginBottom': '8px'}),
                                                    dmc.Slider(
                                                        id='slider-precision',
                                                        min=1,
                                                        max=3,
                                                        step=0.25,
                                                        value=2,
                                                        marks=[
                                                            {"value": 1, "label": "10km"},
                                                            {"value": 2, "label": "1km"},
                                                            {"value": 3, "label": "100m"},
                                                        ],
                                                        mb="lg",
                                                    ),
                                                ]),
                                                html.Div([
                                                    html.Label("Radio difuso", style={**label_style, 'display': 'block', 'marginBottom': '8px'}),
                                                    dmc.Slider(
                                                        id='slider-radio-difuso',
                                                        min=10,
                                                        max=100,
                                                        step=10,
                                                        value=50,
                                                        marks=[
                                                            {"value": 10, "label": "10"},
                                                            {"value": 50, "label": "50"},
                                                            {"value": 100, "label": "100"},
                                                        ],
                                                        mb="lg",
                                                    ),
                                                ]),
                                                html.Div([
                                                    html.Label("Normalizacion", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                                                    dmc.SegmentedControl(
                                                        id='tipo-normalizacion',
                                                        data=[
                                                            {"label": "Normal", "value": "normal"},
                                                            {"label": "Percentil", "value": "percentil"},
                                                            {"label": "Limitado", "value": "limitado"},
                                                        ],
                                                        value="normal",
                                                        size="sm",
                                                        fullWidth=True,
                                                    ),
                                                ]),
                                                dmc.Switch(
                                                    id='opcion-animacion',
                                                    label="Activar animacion temporal",
                                                    checked=False,
                                                    size="sm",
                                                ),
                                                html.Div([
                                                    html.Label("Granularidad", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                                                    dmc.SegmentedControl(
                                                        id='granularidad-animacion',
                                                        data=[
                                                            {"label": "Dia", "value": "dia"},
                                                            {"label": "Semana", "value": "semana"},
                                                            {"label": "Mes", "value": "mes"},
                                                        ],
                                                        value="semana",
                                                        size="sm",
                                                        fullWidth=True,
                                                    ),
                                                ]),
                                            ]),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),

        # Header con navegación
        html.Div([
            html.Div([
                dcc.Link(
                    html.Span("← Inicio", style={
                        'color': '#aaa',
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
            html.H1("Dashboard de Ventas", style={'margin': '0', 'color': 'white'}),
            html.P("Medallion ETL - Visualizacion de datos de ventas",
                   style={'margin': '5px 0 0 0', 'color': '#ccc'})
        ], style={
            'backgroundColor': '#1a1a2e',
            'padding': '20px',
            'marginBottom': '0'
        }),

        # PESTANAS SUPERIORES PRINCIPALES
        dcc.Tabs(id='tabs-principales', value='tab-mapas', children=[
            dcc.Tab(label='Mapas', value='tab-mapas', style={'fontWeight': 'bold', 'padding': '10px 20px'}),
            dcc.Tab(label='Tablero de Ventas', value='tab-tablero-principal', style={'fontWeight': 'bold', 'padding': '10px 20px'}),
        ], style={
            'backgroundColor': '#2d2d44',
            'borderBottom': '3px solid #007bff'
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
            'backgroundColor': '#f8f9fa',
            'borderBottom': '1px solid #dee2e6',
        }),

        # KPIs
        html.Div(id='kpis-container', style={
            'padding': '20px 40px',
            'display': 'flex',
            'justifyContent': 'space-around',
            'alignItems': 'center',
            'backgroundColor': '#fff',
            'borderBottom': '1px solid #ddd'
        }),

        # =====================================================================
        # RESUMEN DE VENTAS (gráficos compactos arriba de los mapas)
        # =====================================================================
        html.Div(id='seccion-resumen', children=[
            # Fila 1: Evolución temporal (full width)
            html.Div([
                dcc.Loading(
                    type='circle',
                    children=[dcc.Graph(id='grafico-evolucion', style={'height': '260px'},
                                        config={'displayModeBar': False})]
                )
            ], style={'padding': '5px 10px 0 10px'}),
            # Fila 2: Top Genéricos + Top Marcas (50/50)
            html.Div([
                html.Div([
                    dcc.Loading(
                        type='circle',
                        children=[dcc.Graph(id='grafico-top-genericos', style={'height': '260px'},
                                            config={'displayModeBar': False})]
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div([
                    dcc.Loading(
                        type='circle',
                        children=[dcc.Graph(id='grafico-top-marcas', style={'height': '260px'},
                                            config={'displayModeBar': False})]
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '0 10px 5px 10px'}),
        ], style={
            'backgroundColor': '#fff',
            'borderBottom': '2px solid #dee2e6',
        }),

        # =====================================================================
        # SECCION MAPAS (visible cuando tab-mapas esta activo)
        # =====================================================================
        html.Div(id='seccion-mapas', children=[
            # Pestanas de mapas
            dcc.Tabs(id='tabs-mapas', value='tab-burbujas', children=[
                dcc.Tab(label='Mapa de Burbujas', value='tab-burbujas', children=[
                    html.Div([
                        dcc.Loading(
                            id='loading-mapa',
                            type='circle',
                            children=[dcc.Graph(id='mapa-ventas', style={'height': '87vh'})]
                        )
                    ], style={'padding': '10px'})
                ]),
                dcc.Tab(label='Mapa de Calor', value='tab-calor', children=[
                    html.Div([
                        dcc.Loading(
                            id='loading-mapa-calor',
                            type='circle',
                            children=[dcc.Graph(id='mapa-calor', style={'height': '87vh'})]
                        )
                    ], style={'padding': '10px'})
                ]),
                dcc.Tab(label='Compro', value='tab-compro', children=[
                    html.Div([
                        dcc.Loading(
                            id='loading-mapa-compro',
                            type='circle',
                            children=[dcc.Graph(id='mapa-compro', style={'height': '87vh'})]
                        )
                    ], style={'padding': '10px'})
                ]),
            ], style={'marginBottom': '0'}),
        ]),

        # =====================================================================
        # SECCION TABLERO (visible cuando tab-tablero-principal esta activo)
        # =====================================================================
        html.Div(id='seccion-tablero', children=[
            # Selector de años para comparar
            html.Div([
                html.Div([
                    dmc.MultiSelect(
                        id='selector-anios',
                        label="Seleccionar años a comparar",
                        data=[],
                        value=[],
                        placeholder="Seleccione uno o más años",
                        searchable=True,
                        w=400,
                    ),
                ], style={'display': 'inline-block', 'marginRight': '30px'}),
            ], style={'padding': '15px 20px', 'backgroundColor': '#e8f4f8', 'borderBottom': '2px solid #1a1a2e'}),

            # Grafica de lineas - Comparacion por Año
            html.Div([
                html.H5("Comparacion Anual (Enero - Diciembre)", style={'textAlign': 'center', 'marginBottom': '5px'}),
                dcc.Loading(
                    id='loading-grafico-linea',
                    type='circle',
                    children=[dcc.Graph(id='grafico-linea-tiempo', style={'height': '500px'})]
                )
            ], style={'padding': '20px'}),

            # Tabla comparativa
            html.Div([
                html.H5("Tabla Comparativa por Mes", style={'textAlign': 'center', 'marginBottom': '15px'}),
                html.Div(id='tabla-comparativa-container', children=[
                    html.P("Seleccione años para ver la comparación", style={'textAlign': 'center', 'color': 'gray'})
                ])
            ], style={'padding': '20px', 'backgroundColor': 'white', 'margin': '0 20px 20px 20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        ], style={'padding': '10px', 'backgroundColor': '#fafafa', 'display': 'none'}),

    ], style={'fontFamily': 'Arial, sans-serif'})
