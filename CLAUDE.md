# Sales Dashboard - Guía para Claude

## Descripción del Proyecto

Dashboard interactivo de ventas construido con Dash/Plotly que visualiza datos de un sistema ETL medallion (bronze → silver → gold). Conecta a PostgreSQL y presenta mapas geográficos, KPIs y análisis temporal de ventas.

## Estructura del Proyecto

```
sales-dashboard/
├── app.py                 # Punto de entrada, routing entre tableros
├── config.py              # Configuración central (colores, estilos, constantes)
├── database.py            # Conexión SQLAlchemy a PostgreSQL
├── layouts/
│   ├── home_layout.py     # Página de inicio con cards de navegación
│   └── main_layout.py     # Layout del dashboard de ventas (create_ventas_layout)
├── callbacks/
│   └── callbacks.py       # Todos los callbacks de Dash (interactividad)
├── data/
│   └── queries.py         # Funciones de consulta SQL a PostgreSQL
├── utils/
│   └── visualization.py   # Funciones de visualización (grillas, zonas convex hull)
└── components/            # (reservado para componentes reutilizables)
```

## Base de Datos

### Conexión
- PostgreSQL en `192.168.1.132:5432`
- Credenciales en `.env` del proyecto `medallion-etl` (ruta: `~/Desktop/medallion-etl/.env`)
- Variables requeridas: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE`, `IP_SERVER`

### Esquema de Datos (Gold Layer)

**`gold.fact_ventas`** - Hechos de ventas
- `id_cliente`, `id_articulo`, `fecha_comprobante`, `nro_doc`
- `cantidades_total` (bultos), `subtotal_final` (facturación)
- `anulado` (boolean) - filtrar con `anulado = FALSE`

**`gold.dim_cliente`** - Dimensión clientes
- `id_cliente`, `razon_social`, `fantasia`
- `latitud`, `longitud` (coordenadas geográficas)
- `des_localidad`, `des_provincia`, `des_ramo`
- `des_canal_mkt`, `des_segmento_mkt`, `des_subcanal_mkt`
- `des_lista_precio`, `des_sucursal`
- `id_ruta_fv1`, `id_ruta_fv4` (rutas por fuerza de venta)
- `des_personal_fv1`, `des_personal_fv4` (preventistas)

**`gold.dim_articulo`** - Dimensión artículos
- `id_articulo`, `generico`, `marca`

### Consideraciones Importantes de Datos

1. **Clientes sin coordenadas**: Algunos clientes no tienen `latitud`/`longitud`. Para mapas, filtrar coordenadas válidas solo en visualización, NO en queries de datos.

2. **Clientes no en dim_cliente**: Hay ventas en `fact_ventas` para clientes que no existen en `dim_cliente` (clientes anulados). Las queries DEBEN partir de `fact_ventas` con `LEFT JOIN` a `dim_cliente` para incluir todas las ventas.

3. **Fuerzas de Venta (FV)**:
   - FV1 y FV4 son fuerzas de venta independientes
   - Cada una tiene sus propias rutas (`id_ruta_fv1`, `id_ruta_fv4`) y preventistas (`des_personal_fv1`, `des_personal_fv4`)
   - Los filtros de ruta/preventista deben considerar la FV seleccionada

## Arquitectura de Callbacks

### Patrón de Filtrado
Los callbacks siguen este patrón:
1. Reciben valores de filtros como `Input`
2. Llaman a funciones de `data/queries.py` para obtener datos
3. Aplican filtros adicionales en Python (canal, subcanal, localidad, etc.)
4. Para mapas: filtran coordenadas válidas SOLO para visualización
5. Retornan figuras Plotly y/o componentes HTML

### IDs de Componentes Importantes
- `filtro-fechas`: DatePickerRange
- `filtro-canal`, `filtro-subcanal`, `filtro-localidad`: Dropdowns multi-select
- `filtro-generico`, `filtro-marca`: Dropdowns con filtro cascada
- `filtro-ruta`, `filtro-preventista`: Dropdowns dependientes de `filtro-fuerza-venta`
- `filtro-metrica`: cantidad_total | facturacion | cantidad_documentos
- `mapa-ventas`, `mapa-calor`: Figuras de mapas
- `kpis-container`: Contenedor de KPIs

### Callbacks Cascada
- `filtro-generico` → actualiza opciones de `filtro-marca`
- `filtro-fuerza-venta` → actualiza opciones de `filtro-ruta` y `filtro-preventista`

## Funciones Clave

### data/queries.py
- `cargar_ventas_por_cliente()`: Ventas agregadas por cliente (para mapas y KPIs)
- `cargar_ventas_por_fecha()`: Ventas agregadas por fecha (para gráficos temporales)
- `cargar_ventas_animacion()`: Ventas por cliente y período (para animaciones)
- `obtener_*()`: Funciones para poblar dropdowns de filtros

### utils/visualization.py
- `crear_grilla_calor_optimizada()`: Crea grilla hexagonal para mapa de calor
- `calcular_zonas()`: Calcula polígonos convex hull para zonas de ruta/preventista

## Sistema de Navegación

El proyecto usa routing basado en URL:
- `/` → Página de inicio (cards de tableros)
- `/ventas` → Dashboard de ventas
- `/nuevo` → Placeholder para nuevos tableros

Para agregar un nuevo tablero:
1. Crear layout en `layouts/nuevo_layout.py`
2. Crear callbacks en `callbacks/nuevo_callbacks.py`
3. Agregar ruta en `app.py` dentro de `display_page()`
4. Agregar card en `layouts/home_layout.py`

## Convenciones de Código

### SQL
- Usar parámetros escapados para prevenir SQL injection
- Siempre filtrar `f.anulado = FALSE` en fact_ventas
- Usar `COALESCE()` para valores por defecto en campos nullable

### Callbacks
- Usar `prevent_initial_call=True` cuando no se necesite ejecución inicial
- Manejar valores None/vacíos en filtros con `if filtro and len(filtro) > 0`
- Para filtros numéricos como rutas, convertir a lista de strings si es necesario

### Visualización
- Colores definidos en `config.py` (COLOR_SCALE_*, ZONE_COLORS)
- Métricas con labels en `METRICA_LABELS`
- Mapas usan `map_style='open-street-map'`

## Ejecución

```bash
cd ~/Desktop/sales-dashboard
python3 app.py
# Acceder en http://localhost:8050
```

## Dependencias Principales
- dash, plotly
- pandas
- sqlalchemy, psycopg2
- pydantic-settings
- scipy (opcional, para zonas convex hull)
- numpy
