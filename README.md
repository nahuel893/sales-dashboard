# Sales Dashboard - Medallion ETL

Dashboard interactivo multi-tablero de ventas con mapas geolocalizados, construido con Dash/Plotly. Conecta a un sistema ETL medallion (PostgreSQL) y presenta análisis geográficos, KPIs y evolución temporal.

## Características Principales

- **Sistema de navegación multi-tablero**: Página de inicio con cards para seleccionar entre diferentes dashboards
- **Mapas interactivos**: Burbujas y calor con datos geolocalizados
- **KPIs en tiempo real**: Clientes, bultos, facturación, documentos
- **Filtros avanzados**: Cascada entre genérico→marca, fuerza de venta→ruta→preventista
- **Animaciones temporales**: Visualización por día/semana/mes
- **Zonas geográficas**: Convex hull por ruta o preventista
- **Comparación anual**: Gráficos de evolución año vs año

## Estructura del Proyecto

```
sales-dashboard/
├── app.py                    # Punto de entrada, routing entre tableros
├── config.py                 # Configuración central (colores, estilos)
├── database.py               # Conexión SQLAlchemy a PostgreSQL
├── CLAUDE.md                 # Guía para asistentes AI
│
├── layouts/
│   ├── home_layout.py        # Página de inicio con cards
│   └── main_layout.py        # Layout del dashboard de ventas
│
├── callbacks/
│   └── callbacks.py          # Callbacks de interactividad
│
├── data/
│   └── queries.py            # Funciones de consulta SQL
│
├── utils/
│   └── visualization.py      # Utilidades (grillas, zonas convex hull)
│
└── components/               # (reservado para componentes reutilizables)
```

## Instalación

### Requisitos
- Python 3.8+
- PostgreSQL con esquema medallion (gold layer)
- Archivo `.env` en `~/Desktop/medallion-etl/`

### Dependencias

```bash
pip install dash plotly pandas numpy sqlalchemy psycopg2-binary pydantic-settings scipy
```

### Variables de Entorno

El archivo `~/Desktop/medallion-etl/.env` debe contener:

```env
POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
DATABASE=nombre_db
IP_SERVER=192.168.1.x
```

## Ejecución

```bash
cd ~/Desktop/sales-dashboard
python3 app.py
```

Acceder en: http://localhost:8050

## Sistema de Navegación

El dashboard usa un sistema de routing basado en URL:

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio con cards de selección |
| `/ventas` | Dashboard de ventas (mapas, KPIs, análisis) |
| `/nuevo` | Placeholder para futuros tableros |

### Agregar un Nuevo Tablero

1. Crear layout en `layouts/nuevo_tablero_layout.py`
2. Crear callbacks en `callbacks/nuevo_tablero_callbacks.py`
3. Agregar ruta en `app.py` dentro de `display_page()`
4. Agregar card en `layouts/home_layout.py`

## Módulos

### app.py

Punto de entrada principal con routing:
- Carga datos iniciales (filtros, fechas)
- Define rutas URL
- Importa callbacks

### config.py

Configuración centralizada:
- `SERVER_CONFIG`: host, port, debug
- `METRICA_LABELS`: Labels para métricas
- `COLOR_SCALE_*`: Escalas de colores para mapas
- `ZONE_COLORS`: Colores para zonas geográficas
- `GRANULARIDAD_CONFIG`: Configuración temporal
- `STYLES`: Estilos CSS comunes

### database.py

Conexión a PostgreSQL:
- Lee credenciales desde `.env`
- Exporta `engine` para queries
- Función `get_db()` para sesiones

### data/queries.py

Funciones de acceso a datos:

| Función | Descripción |
|---------|-------------|
| `obtener_genericos()` | Lista de genéricos de artículos |
| `obtener_marcas(genericos)` | Marcas (filtradas por genéricos) |
| `obtener_rutas(fv)` | Rutas según fuerza de venta |
| `obtener_preventistas(fv)` | Preventistas según fuerza de venta |
| `obtener_rango_fechas()` | Rango min/max de fechas |
| `obtener_anios_disponibles()` | Años con datos |
| `cargar_ventas_por_cliente(...)` | Ventas agregadas por cliente |
| `cargar_ventas_por_fecha(...)` | Ventas agregadas por fecha |
| `cargar_ventas_animacion(...)` | Ventas por cliente y período |

### utils/visualization.py

Funciones de visualización:

| Función | Descripción |
|---------|-------------|
| `crear_grilla_calor_optimizada()` | Grilla de celdas para mapa de calor |
| `calcular_zonas()` | Convex hull para zonas geográficas |
| `_filtrar_outliers_iqr()` | Filtra outliers por IQR |

### layouts/

- **home_layout.py**: `create_home_layout()` - Cards de navegación
- **main_layout.py**: `create_ventas_layout()` - Dashboard de ventas completo

### callbacks/callbacks.py

Callbacks principales:

| Callback | Descripción |
|----------|-------------|
| `actualizar_marcas_por_generico` | Filtro cascada genérico→marca |
| `actualizar_rutas_preventistas` | Actualiza según fuerza de venta |
| `actualizar_filtros` | Actualiza opciones de filtros |
| `actualizar_mapa` | Mapa de burbujas + KPIs |
| `actualizar_mapa_calor` | Mapa de calor |
| `actualizar_grafico_anios` | Gráfico comparación anual |
| `actualizar_tabla_comparativa` | Tabla meses vs años |

## Modelo de Datos

### Tablas Gold Layer

**gold.fact_ventas**
```
id_cliente, id_articulo, fecha_comprobante, nro_doc
cantidades_total (bultos), subtotal_final (facturación)
anulado (boolean)
```

**gold.dim_cliente**
```
id_cliente, razon_social, fantasia
latitud, longitud
des_localidad, des_provincia, des_ramo
des_canal_mkt, des_segmento_mkt, des_subcanal_mkt
des_lista_precio, des_sucursal
id_ruta_fv1, id_ruta_fv4
des_personal_fv1, des_personal_fv4
```

**gold.dim_articulo**
```
id_articulo, generico, marca
```

### Consideraciones de Datos

1. **Ventas anuladas**: Filtrar siempre con `f.anulado = FALSE`
2. **Clientes sin coordenadas**: Incluir en totales, filtrar solo para visualización de mapas
3. **Clientes no en dim_cliente**: Las queries parten de `fact_ventas` con `LEFT JOIN` a `dim_cliente`

## Funcionalidades

### Página de Inicio
- Cards clickeables para cada tablero
- Diseño responsive
- Navegación por URL

### Dashboard de Ventas

#### Mapa de Burbujas
- Clientes con ventas: burbujas coloreadas según métrica
- Clientes sin ventas: puntos grises
- Zonas por ruta/preventista (convex hull)
- Animación temporal

#### Mapa de Calor
- **Modo Difuso**: density_map de Plotly
- **Modo Grilla**: celdas agrupadas por color
- Opciones: escala log, normalización
- Animación temporal

#### Tablero de Ventas
- Selector de años (multi-select)
- Gráfico de líneas: meses vs años
- Tabla comparativa con crecimiento %

#### KPIs
- Total clientes (activos/inactivos)
- Bultos vendidos
- Facturación total
- Documentos emitidos

### Filtros

| Categoría | Filtros |
|-----------|---------|
| Temporal | Rango de fechas, Años |
| Cliente | Canal, Subcanal, Localidad, Lista Precio, Sucursal |
| Producto | Genérico, Marca (cascada) |
| Fuerza de Venta | FV1/FV4/TODOS, Ruta, Preventista |
| Métrica | Bultos, Facturación, Documentos |

## Flujo de Datos

```
Usuario → Filtros → Callback → Query SQL → DataFrame → Plotly → UI
```

1. Usuario cambia filtros
2. Callback detecta cambio (Input)
3. Query a PostgreSQL vía SQLAlchemy
4. Procesamiento en pandas
5. Creación de figura Plotly
6. Actualización del componente (Output)

## Configuración Avanzada

### Cambiar Puerto/Host

Editar `config.py`:
```python
SERVER_CONFIG = {
    'host': '0.0.0.0',  # Para acceso en red
    'port': 8050,
    'debug': False      # Desactivar en producción
}
```

### Agregar Nueva Métrica

1. Agregar campo en query SQL
2. Agregar label en `config.py` → `METRICA_LABELS`
3. Agregar opción en dropdown de métrica en layout

## Troubleshooting

### Error de conexión a base de datos
- Verificar que el archivo `.env` existe en `~/Desktop/medallion-etl/`
- Verificar credenciales y accesibilidad del servidor PostgreSQL

### scipy no disponible
- Las zonas (convex hull) requieren scipy
- Instalar con: `pip install scipy`

### Datos no coinciden entre KPIs y tablas
- Verificar que las queries usen `fact_ventas` como tabla base
- Verificar filtro `anulado = FALSE`

## Licencia

Proyecto interno - Medallion ETL
