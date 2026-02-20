# Sales Dashboard - Medallion ETL

Dashboard interactivo multi-tablero de ventas con mapas geolocalizados, construido con Dash/Plotly. Conecta a un sistema ETL medallion (PostgreSQL) y presenta analisis geograficos, KPIs, evolucion temporal, dashboard YTD y detalle por cliente.

## Caracteristicas Principales

- **Sistema de navegacion multi-tablero**: Home, Ventas, YTD, Clientes, Detalle Cliente
- **Tema oscuro completo**: Paleta dark centralizada en config.py aplicada a toda la UI
- **Mapas interactivos**: Burbujas (escala fija 0-15), calor (difuso/grilla), compro/no compro
- **KPIs en tiempo real**: Clientes, bultos, facturacion, documentos
- **Filtros avanzados**: Panel lateral con cascada generico->marca, FV->ruta->preventista
- **Hover enriquecido**: Top 5 genericos por cliente con MAct/MAnt (mes actual vs anterior)
- **Badges de ruta**: Overlay sobre el mapa con desglose ventas y compradores por zona
- **Zonas geograficas**: Convex hull por ruta o preventista con colores distintos
- **Animaciones temporales**: Visualizacion por dia/semana/mes
- **Comparacion anual**: Graficos de evolucion ano vs ano + tabla comparativa
- **Detalle de cliente**: Tabla jerarquica generico->marca->articulo, ultimos 12 meses
- **Export Excel**: 3 hojas (por generico, por marca, detalle articulos)
- **Dashboard YTD**: 7 KPIs + 6 graficos con target automatico (+10% interanual)

## Estructura del Proyecto

```
sales-dashboard/
├── app.py                     # Punto de entrada, routing entre tableros
├── config.py                  # Configuracion central (colores, estilos, tema DARK)
├── database.py                # Conexion SQLAlchemy a PostgreSQL
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias Python
├── VERSION                    # Version actual del proyecto
├── CHANGELOG.md               # Historial de cambios
├── ROADMAP.md                 # Plan de versiones futuras
├── CLAUDE.md                  # Guia para asistentes AI
├── CONTEXT_IA.md              # Esquema de BD y contexto de datos
│
├── layouts/
│   ├── home_layout.py         # Pagina de inicio con cards de navegacion
│   ├── main_layout.py         # Dashboard de ventas (mapas + filtros + KPIs)
│   ├── ytd_layout.py          # Dashboard YTD (KPIs + graficos)
│   ├── cliente_layout.py      # Detalle de cliente individual
│   └── clientes_layout.py     # Busqueda de clientes
│
├── callbacks/
│   ├── callbacks.py           # Callbacks del dashboard de ventas
│   ├── ytd_callbacks.py       # Callbacks del dashboard YTD
│   ├── cliente_callbacks.py   # Callbacks del detalle de cliente
│   └── clientes_callbacks.py  # Callbacks de busqueda de clientes
│
├── data/
│   ├── queries.py             # Queries SQL (ventas + clientes)
│   └── ytd_queries.py         # Queries SQL del dashboard YTD
│
├── utils/
│   └── visualization.py       # Grillas de calor, zonas convex hull
│
├── components/                # (reservado para componentes reutilizables)
│
└── docs/
    ├── EVALUACION_TECNICA_DASHBOARD.md
    └── TODO_CORRECCIONES.md
```

## Instalacion

### Requisitos
- Python 3.8+
- PostgreSQL con esquema medallion (gold layer)

### Configuracion

```bash
cd ~/Desktop/sales-dashboard

# Configurar variables de entorno
cp .env.example .env
# Editar .env con las credenciales reales
```

El archivo `.env` debe contener:

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=tu_base_de_datos
POSTGRES_HOST=192.168.1.x
POSTGRES_PORT=5432
```

### Dependencias

```bash
pip install -r requirements.txt
```

Dependencias principales:
- `dash`, `plotly`, `dash-mantine-components` (UI y graficos)
- `pandas`, `numpy` (procesamiento de datos)
- `sqlalchemy`, `psycopg2-binary` (conexion PostgreSQL)
- `pydantic`, `pydantic-settings` (configuracion)
- `scipy` (zonas convex hull)
- `openpyxl` (export Excel)

## Ejecucion

```bash
python3 app.py
```

Acceder en: http://localhost:8050

Para acceso en red local, `config.py` tiene `host: '0.0.0.0'`.

## Sistema de Navegacion

| URL | Pagina | Descripcion |
|-----|--------|-------------|
| `/` | Home | Cards de seleccion de tableros |
| `/ventas` | Dashboard Ventas | Mapas interactivos, KPIs, comparacion anual |
| `/ytd` | Dashboard YTD | Indicadores acumulados anuales, targets |
| `/clientes` | Buscar Clientes | Busqueda por nombre o codigo |
| `/cliente/<id>` | Detalle Cliente | Ventas por generico/marca/articulo, export Excel |
| `/nuevo` | Placeholder | Reservado para futuros tableros |

## Modulos

### app.py
Punto de entrada principal:
- Inicializa Dash con `dmc.MantineProvider`
- Pre-carga datos iniciales (filtros, fechas, listas)
- Define routing URL -> layout
- Importa todos los callbacks
- Exporta `server` para gunicorn

### config.py
Configuracion centralizada:
- `SERVER_CONFIG`: host, port, debug
- `DARK`: Paleta de colores del tema oscuro (16+ colores)
- `METRICA_LABELS`: Labels para metricas (Bultos, Facturacion, Documentos)
- `COLOR_SCALE_*`: Escalas de colores para mapas
- `ZONE_COLORS`: Colores para zonas geograficas
- `GRANULARIDAD_CONFIG`: Opciones de granularidad temporal
- `STYLES`: Estilos CSS comunes

### database.py
Conexion a PostgreSQL:
- `Settings` con `pydantic-settings` (lee `.env`)
- Exporta `engine` (SQLAlchemy) para queries
- Funcion `get_db()` para sesiones

### data/queries.py
Funciones de acceso a datos del dashboard de ventas y clientes:

| Funcion | Descripcion |
|---------|-------------|
| `cargar_ventas_por_cliente(...)` | Ventas por cliente (mapas). Parte de dim_cliente |
| `cargar_ventas_por_fecha(...)` | Ventas por fecha (graficos). Parte de fact_ventas |
| `cargar_ventas_animacion(...)` | Ventas por periodo (animaciones) |
| `cargar_ventas_por_cliente_generico(...)` | Top N genericos por cliente, MAct/MAnt |
| `cargar_ventas_por_generico_top(...)` | Top genericos por metrica |
| `cargar_ventas_por_marca_top(...)` | Top marcas por metrica |
| `buscar_clientes(texto)` | Busqueda por nombre/codigo |
| `cargar_info_cliente(id)` | Datos maestros del cliente |
| `cargar_ventas_cliente_detalle(id)` | Historico con jerarquia generico/marca/articulo |
| `obtener_genericos()` | Lista de genericos |
| `obtener_marcas(genericos)` | Marcas filtradas por generico |
| `obtener_rutas(fv)` | Rutas con clave compuesta |
| `obtener_preventistas(fv)` | Preventistas por FV |
| `obtener_rango_fechas()` | Min/max fechas |

### data/ytd_queries.py
Funciones del dashboard YTD:

| Funcion | Descripcion |
|---------|-------------|
| `obtener_ventas_ytd(...)` | Acumulado YTD |
| `obtener_ventas_por_mes(...)` | Desglose mensual |
| `obtener_ventas_por_generico(...)` | Por categoria |
| `obtener_ventas_por_sucursal(...)` | Por sucursal |
| `obtener_ventas_por_canal(...)` | Por canal |
| `calcular_target_automatico(...)` | Target (ano anterior +10%) |
| `calcular_crecimiento_mensual(...)` | Crecimiento % YoY |
| `obtener_dias_inventario(...)` | Stock / venta diaria |

### utils/visualization.py
Funciones de visualizacion:

| Funcion | Descripcion |
|---------|-------------|
| `crear_grilla_calor_optimizada()` | Grilla de celdas para mapa de calor |
| `calcular_zonas()` | Convex hull por ruta o preventista |
| `_filtrar_outliers_iqr()` | Filtra outliers por IQR |

## Dashboard de Ventas

### Mapas
- **Mapa de Burbujas**: Escala fija 0-15, hover con top 5 genericos MAct/MAnt, click abre detalle cliente, badges overlay con info de zona
- **Mapa de Calor**: Modo difuso (density) o grilla, escala log, normalizacion configurable
- **Mapa Compro/No Compro**: Verde (con ventas) vs rojo (sin ventas)

### Tablero Comparativo
- Selector de anos (multi-select)
- Grafico de lineas: evolucion mensual por ano
- Tabla: meses x anos con crecimiento %
- Top 10 genericos y marcas

### Filtros (Panel lateral dmc.Drawer)
Todos los componentes con tema oscuro (dark_input_styles):
- Rango de fechas (DatePickerInput)
- Canal, Subcanal, Localidad, Lista Precio (MultiSelect)
- Tipo Sucursal, Sucursal (SegmentedControl + MultiSelect)
- Generico, Marca (MultiSelect cascada)
- Fuerza de Venta (SegmentedControl), Ruta, Preventista (MultiSelect)
- Metrica (SegmentedControl: Bultos/Facturacion/Documentos)
- Opciones de zonas (Switch), Animacion (Switch + SegmentedControl granularidad)

## Dashboard YTD

### KPIs (7 indicadores)
- Ventas YTD (bultos), Interanual (%), Objetivo, Cumplimiento (%), Ventas Ano Anterior
- Ganancia Bruta y Margen (placeholders)

### Graficos (6 tipos)
- Ventas por Generico (barras apiladas + target)
- Real vs Objetivo mensual (semaforo: verde >=100%, amarillo 90-99%, rojo <90%)
- Ventas por Sucursal (barras horizontales, top 6)
- Ventas por Canal (dona)
- Crecimiento mensual (barras +/-)
- Dias de Inventario (gauge: verde <=30, amarillo 30-45, rojo >45)

### Filtros
- Ano, Mes (hasta), Tipo Sucursal (TODAS/SUCURSALES/CASA_CENTRAL)

## Detalle de Cliente

- **Header**: Info completa del cliente (nombre, codigo, canal, sucursal, ruta, preventista)
- **KPIs**: 3 metricas del mes actual con texto explicativo
- **Tabla plana**: Jerarquia generico->marca->articulo, ultimos 12 meses calendario
  - Subtotales por marca y generico
  - Jump-to dropdowns para navegar rapidamente
  - Separacion articulos con/sin ventas
- **Export Excel**: Boton para descarga completa (3 hojas) o por marca individual

## Modelo de Datos

### Tablas Gold Layer

**gold.fact_ventas** (hechos de ventas)
```
id_cliente, id_articulo, id_sucursal, fecha_comprobante, nro_doc
cantidades_total (bultos), subtotal_final (facturacion)
anulado (boolean) - NO se filtra
```

**gold.dim_cliente** (dimension clientes)
```
id_cliente (unico global), razon_social, fantasia
latitud, longitud, id_sucursal
des_localidad, des_provincia, des_ramo
des_canal_mkt, des_segmento_mkt, des_subcanal_mkt
des_lista_precio, des_sucursal
id_ruta_fv1, id_ruta_fv4, des_personal_fv1, des_personal_fv4
anulado (boolean) - se filtra en queries de mapa
```

**gold.dim_articulo** (dimension articulos)
```
id_articulo, des_articulo, generico, marca
```

**gold.fact_stock** (stock actual - usado en YTD)

### Consideraciones de Datos

1. **Ventas anuladas**: NO filtrar `anulado` en fact_ventas — incluir todas
2. **Clientes en mapa**: Partir de `dim_cliente WHERE anulado = FALSE`, LEFT JOIN a fact_ventas
3. **Metricas temporales**: Partir de `fact_ventas`, LEFT JOIN a dim_cliente
4. **Claves compuestas**: Rutas usan `(id_sucursal, id_ruta)`. Clientes son unicos globales.
5. **Clientes sin coordenadas**: Incluir en totales, filtrar solo para mapa

Ver `CONTEXT_IA.md` para esquema completo.

## Flujo de Datos

```
Usuario -> Filtros -> Callback -> Query SQL -> DataFrame -> Plotly -> UI
                                  (PostgreSQL)   (pandas)   (dash)
```

## Configuracion Avanzada

### Cambiar Puerto/Host
Editar `config.py` -> `SERVER_CONFIG`

### Agregar Nueva Metrica
1. Agregar campo en query SQL
2. Agregar label en `config.py` -> `METRICA_LABELS`
3. Agregar opcion en dropdown de metrica en layout

### Agregar Nuevo Tablero
1. Crear layout en `layouts/`
2. Crear callbacks en `callbacks/`
3. Agregar ruta en `app.py` -> `display_page()`
4. Agregar card en `layouts/home_layout.py`

## Deployment

- **Repositorio**: GitHub (`github`) + servidor produccion (`production`)
- **Produccion**: `nahuel@100.72.221.10:/srv/git/sales-dashboard.git`
- **Branch**: `main` (trunk-based development, version unica en produccion)
- **Versionado**: Semantico (`MAJOR.MINOR.PATCH`) con git tags anotados

## Troubleshooting

### Error de conexion a BD
- Verificar que `.env` existe en la raiz del proyecto (NO en medallion-etl)
- Verificar credenciales y accesibilidad del servidor PostgreSQL

### scipy no disponible
- Las zonas (convex hull) requieren scipy: `pip install scipy`

### openpyxl no disponible
- El export Excel requiere openpyxl: `pip install openpyxl`

### Datos no coinciden entre KPIs y tablas
- Verificar que las queries NO filtren por `anulado`
- Verificar que mapas partan de `dim_cliente` y metricas de `fact_ventas`

## Licencia

Proyecto interno - Medallion ETL
