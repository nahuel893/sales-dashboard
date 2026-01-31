"""
Layout principal del dashboard de ventas.
"""
from dash import html, dcc


def create_ventas_layout(fecha_min, fecha_max, fecha_desde_default, lista_genericos, lista_marcas, lista_rutas, lista_preventistas):
    """Crea y retorna el layout del dashboard de ventas."""

    return html.Div([
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
                html.Label("Rango de Fechas:", style={'fontWeight': 'bold', 'marginRight': '15px'}),
                dcc.DatePickerRange(
                    id='filtro-fechas',
                    min_date_allowed=fecha_min,
                    max_date_allowed=fecha_max,
                    start_date=fecha_desde_default,
                    end_date=fecha_max,
                    display_format='DD/MM/YYYY'
                ),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], style={'padding': '15px 20px', 'backgroundColor': '#e8f4f8', 'borderBottom': '2px solid #1a1a2e'}),

        # Fila 1: Filtros de cliente (Canal, Subcanal, Localidad)
        html.Div([
            html.Div([
                html.Label("Canal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-canal',
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Todos los canales",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Subcanal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-subcanal',
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Todos los subcanales",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Localidad:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-localidad',
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Todas las localidades",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#f5f5f5'}),

        # Fila 2: Filtros de cliente (Lista Precio, Sucursal, Metrica)
        html.Div([
            html.Div([
                html.Label("Lista Precio:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-lista-precio',
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Todas las listas",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Tipo Sucursal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-tipo-sucursal',
                    options=[
                        {'label': 'Todas', 'value': 'TODAS'},
                        {'label': 'Solo Sucursales', 'value': 'SUCURSALES'},
                        {'label': 'Solo Casa Central', 'value': 'CASA_CENTRAL'}
                    ],
                    value='TODAS',
                    clearable=False,
                    style={'fontSize': '14px'}
                )
            ], style={'width': '15%', 'display': 'inline-block', 'marginRight': '1%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Sucursal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-sucursal',
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Todas las sucursales",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '17%', 'display': 'inline-block', 'marginRight': '1%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Metrica:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-metrica',
                    options=[
                        {'label': 'Cantidad (bultos)', 'value': 'cantidad_total'},
                        {'label': 'Facturacion ($)', 'value': 'facturacion'},
                        {'label': 'Documentos', 'value': 'cantidad_documentos'}
                    ],
                    value='cantidad_total',
                    clearable=False,
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#f5f5f5'}),

        # Fila 3: Filtros de producto (Generico, Marca)
        html.Div([
            html.Div([
                html.Label("Generico:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-generico',
                    options=[{'label': g, 'value': g} for g in lista_genericos],
                    value=[],
                    multi=True,
                    placeholder="Todos los genericos",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Marca:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-marca',
                    options=[{'label': m, 'value': m} for m in lista_marcas],
                    value=[],
                    multi=True,
                    placeholder="Todas las marcas",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'padding': '15px 20px', 'backgroundColor': '#fff3cd', 'borderBottom': '1px solid #ffc107'}),

        # Fila 4: Filtros de fuerza de ventas, ruta y preventista
        html.Div([
            html.Div([
                html.Label("Fuerza de Ventas:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.RadioItems(
                    id='filtro-fuerza-venta',
                    options=[
                        {'label': ' Todos', 'value': 'TODOS'},
                        {'label': ' FV1', 'value': 'FV1'},
                        {'label': ' FV4', 'value': 'FV4'}
                    ],
                    value='TODOS',
                    inline=True,
                    inputStyle={'marginRight': '8px'},
                    labelStyle={'marginRight': '20px', 'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Ruta:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-ruta',
                    options=[{'label': str(r), 'value': r} for r in lista_rutas],
                    value=[],
                    multi=True,
                    placeholder="Todas las rutas",
                    style={'fontSize': '14px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

            html.Div([
                html.Label("Preventista:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='filtro-preventista',
                    options=[{'label': p, 'value': p} for p in lista_preventistas],
                    value=[],
                    multi=True,
                    placeholder="Todos los preventistas",
                    style={'fontSize': '14px'}
                )
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
                    html.Label("Mostrar zonas:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Checklist(
                        id='opciones-zonas',
                        options=[
                            {'label': ' Zonas por Ruta', 'value': 'ruta'},
                            {'label': ' Zonas por Preventista', 'value': 'preventista'}
                        ],
                        value=[],
                        inline=True,
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'marginRight': '20px', 'fontSize': '14px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

                html.Div([
                    html.Label("Escala:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Checklist(
                        id='opcion-escala-log',
                        options=[
                            {'label': ' Logaritmica', 'value': 'log'}
                        ],
                        value=['log'],
                        inline=True,
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'fontSize': '14px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

                html.Div([
                    html.Label("Tipo mapa calor:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.RadioItems(
                        id='tipo-mapa-calor',
                        options=[
                            {'label': ' Difuso', 'value': 'density'},
                            {'label': ' Grilla', 'value': 'grilla'}
                        ],
                        value='density',
                        inline=True,
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'marginRight': '20px', 'fontSize': '14px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '15px 20px 8px 20px', 'backgroundColor': '#e7f3ff'}),

            # Opciones de visualizacion - Fila 2 (Tamano celda, Radio difuso, Normalizacion)
            html.Div([
                html.Div([
                    html.Label("Tamano celda:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Slider(
                        id='slider-precision',
                        min=1,
                        max=3,
                        step=0.25,
                        value=2,
                        marks={
                            1: {'label': '10km', 'style': {'fontSize': '12px'}},
                            2: {'label': '1km', 'style': {'fontSize': '12px'}},
                            3: {'label': '100m', 'style': {'fontSize': '12px'}}
                        },
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

                html.Div([
                    html.Label("Radio difuso:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Slider(
                        id='slider-radio-difuso',
                        min=10,
                        max=100,
                        step=10,
                        value=50,
                        marks={
                            10: {'label': '10', 'style': {'fontSize': '12px'}},
                            50: {'label': '50', 'style': {'fontSize': '12px'}},
                            100: {'label': '100', 'style': {'fontSize': '12px'}}
                        },
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),

                html.Div([
                    html.Label("Normalizacion:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.RadioItems(
                        id='tipo-normalizacion',
                        options=[
                            {'label': ' Normal', 'value': 'normal'},
                            {'label': ' Percentil', 'value': 'percentil'},
                            {'label': ' Limitado', 'value': 'limitado'}
                        ],
                        value='normal',
                        inline=True,
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'marginRight': '15px', 'fontSize': '14px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ], style={'padding': '8px 20px 15px 20px', 'backgroundColor': '#e7f3ff'}),

            # Opciones de animacion
            html.Div([
                html.Div([
                    html.Label("Animacion temporal:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Checklist(
                        id='opcion-animacion',
                        options=[
                            {'label': ' Activar animacion', 'value': 'animar'}
                        ],
                        value=[],
                        inline=True,
                        inputStyle={'marginRight': '8px'},
                        labelStyle={'fontSize': '14px'}
                    )
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div([
                    html.Label("Granularidad:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.RadioItems(
                        id='granularidad-animacion',
                        options=[
                            {'label': ' Dia', 'value': 'dia'},
                            {'label': ' Semana', 'value': 'semana'},
                            {'label': ' Mes', 'value': 'mes'}
                        ],
                        value='semana',
                        inline=True,
                        inputStyle={'marginRight': '5px'},
                        labelStyle={'fontSize': '14px', 'marginRight': '15px'}
                    )
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
                    html.Label("Seleccionar años a comparar:", style={'fontWeight': 'bold', 'marginBottom': '8px', 'fontSize': '14px'}),
                    dcc.Dropdown(
                        id='selector-anios',
                        options=[],  # Se llena dinamicamente
                        value=[],
                        multi=True,
                        placeholder="Seleccione uno o más años",
                        style={'fontSize': '14px', 'width': '400px'}
                    )
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
