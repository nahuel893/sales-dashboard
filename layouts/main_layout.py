"""
Layout principal del dashboard de ventas.
"""
from dash import html, dcc
import dash_mantine_components as dmc


def create_ventas_layout(fecha_min, fecha_max, fecha_desde_default, lista_genericos, lista_marcas, lista_rutas, lista_preventistas):
    """Crea y retorna el layout del dashboard de ventas."""

    # Estilo común para labels de sección
    label_style = {'fontWeight': 'bold', 'fontSize': '14px', 'color': '#333'}

    return html.Div([
        # Div oculto para clientside callback de click en mapa
        html.Div(id='click-output-dummy', style={'display': 'none'}),

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

        # =====================================================================
        # FILTROS COMUNES (compartidos entre Mapas y Tablero)
        # =====================================================================

        # Filtro de fechas
        html.Div([
            html.Div([
                dmc.DatePickerInput(
                    id='filtro-fechas',
                    label="Rango de Fechas",
                    type="range",
                    value=[str(fecha_desde_default), str(fecha_max)],
                    valueFormat="DD/MM/YYYY",
                    w=320,
                ),
            ], style={'display': 'flex', 'alignItems': 'flex-end'}),
        ], style={'padding': '15px 20px', 'backgroundColor': '#e8f4f8', 'borderBottom': '2px solid #1a1a2e'}),

        # Fila 1: Filtros de cliente (Canal, Subcanal, Localidad)
        html.Div([
            html.Div([
                dmc.MultiSelect(
                    id='filtro-canal',
                    label="Canal",
                    data=[],
                    value=[],
                    placeholder="Todos los canales",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-subcanal',
                    label="Subcanal",
                    data=[],
                    value=[],
                    placeholder="Todos los subcanales",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-localidad',
                    label="Localidad",
                    data=[],
                    value=[],
                    placeholder="Todas las localidades",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#f5f5f5'}),

        # Fila 2: Filtros de cliente (Lista Precio, Tipo Sucursal, Sucursal, Metrica)
        html.Div([
            html.Div([
                dmc.MultiSelect(
                    id='filtro-lista-precio',
                    label="Lista Precio",
                    data=[],
                    value=[],
                    placeholder="Todas las listas",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'verticalAlign': 'top'}),

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
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-sucursal',
                    label="Sucursal",
                    data=[],
                    value=[],
                    placeholder="Todas las sucursales",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Metrica", style={**label_style, 'display': 'block', 'marginBottom': '5px'}),
                dmc.SegmentedControl(
                    id='filtro-metrica',
                    data=[
                        {"label": "Bultos", "value": "cantidad_total"},
                        {"label": "Facturación", "value": "facturacion"},
                        {"label": "Documentos", "value": "cantidad_documentos"},
                    ],
                    value="cantidad_total",
                    size="sm",
                ),
            ], style={'width': '24%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#f5f5f5'}),

        # Fila 3: Filtros de producto (Generico, Marca)
        html.Div([
            html.Div([
                dmc.MultiSelect(
                    id='filtro-generico',
                    label="Generico",
                    data=[g for g in lista_genericos],
                    value=[],
                    placeholder="Todos los genericos",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-marca',
                    label="Marca",
                    data=[m for m in lista_marcas],
                    value=[],
                    placeholder="Todas las marcas",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '15px 20px', 'backgroundColor': '#fff3cd', 'borderBottom': '1px solid #ffc107'}),

        # Fila 4: Filtros de fuerza de ventas, ruta y preventista
        html.Div([
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
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-ruta',
                    label="Ruta",
                    data=[{"label": str(r), "value": str(r)} for r in lista_rutas],
                    value=[],
                    placeholder="Todas las rutas",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                dmc.MultiSelect(
                    id='filtro-preventista',
                    label="Preventista",
                    data=[p for p in lista_preventistas],
                    value=[],
                    placeholder="Todos los preventistas",
                    searchable=True,
                    clearable=True,
                ),
            ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '15px 20px', 'backgroundColor': '#d4edda', 'borderBottom': '1px solid #28a745'}),

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
        # SECCION MAPAS (visible cuando tab-mapas esta activo)
        # =====================================================================
        html.Div(id='seccion-mapas', children=[
            # Opciones de visualizacion - Fila 1 (Zonas, Escala, Tipo mapa)
            html.Div([
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
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

                html.Div([
                    dmc.Switch(
                        id='opcion-escala-log',
                        label="Escala Logaritmica",
                        checked=True,
                        size="sm",
                    ),
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top', 'paddingTop': '8px'}),

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
                    ),
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#e7f3ff'}),

            # Opciones de visualizacion - Fila 2 (Tamano celda, Radio difuso, Normalizacion)
            html.Div([
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
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

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
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

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
                    ),
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#e7f3ff'}),

            # Opciones de animacion
            html.Div([
                html.Div([
                    dmc.Switch(
                        id='opcion-animacion',
                        label="Activar animacion temporal",
                        checked=False,
                        size="sm",
                    ),
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingTop': '5px'}),
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
                    ),
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '10px 20px', 'backgroundColor': '#fff3e0', 'borderBottom': '1px solid #007bff'}),

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
