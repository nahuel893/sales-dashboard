# Sales Dashboard - Guia para Claude

## Descripcion del Proyecto

Dashboard interactivo de ventas construido con Dash/Plotly que visualiza datos de un sistema ETL medallion (bronze -> silver -> gold). Conecta a PostgreSQL y presenta mapas geograficos, KPIs, analisis temporal, dashboard YTD y detalle por cliente.

**Version actual:** 1.0.0 (ver `VERSION`, `CHANGELOG.md`, `ROADMAP.md`)

## Estructura del Proyecto

```
sales-dashboard/
├── app.py                     # Punto de entrada, routing entre tableros
├── config.py                  # Configuracion central (colores, estilos, constantes, tema DARK)
├── database.py                # Conexion SQLAlchemy a PostgreSQL (carga .env local)
├── .env                       # Variables de entorno (NO commitear, esta en .gitignore)
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias Python
├── VERSION                    # Version actual del proyecto
├── CHANGELOG.md               # Historial de cambios por version
├── ROADMAP.md                 # Plan de versiones futuras
├── CONTEXT_IA.md              # Esquema completo de BD (fuente de verdad para datos)
│
├── layouts/
│   ├── home_layout.py         # Pagina de inicio con cards de navegacion
│   ├── main_layout.py         # Layout del dashboard de ventas (create_ventas_layout)
│   ├── ytd_layout.py          # Layout del dashboard YTD (create_ytd_layout)
│   ├── cliente_layout.py      # Layout detalle de cliente (create_cliente_layout)
│   └── clientes_layout.py     # Layout busqueda de clientes (create_clientes_layout)
│
├── callbacks/
│   ├── callbacks.py           # Callbacks del dashboard de ventas (~1300 lineas)
│   ├── ytd_callbacks.py       # Callbacks del dashboard YTD (~507 lineas)
│   ├── cliente_callbacks.py   # Callbacks del detalle de cliente (~895 lineas)
│   └── clientes_callbacks.py  # Callbacks de busqueda de clientes
│
├── data/
│   ├── queries.py             # Queries SQL del dashboard de ventas + clientes (~750 lineas)
│   └── ytd_queries.py         # Queries SQL del dashboard YTD (~353 lineas)
│
├── utils/
│   └── visualization.py       # Funciones de visualizacion (grillas, zonas convex hull)
│
├── components/                # (reservado para componentes reutilizables)
│
└── docs/
    ├── EVALUACION_TECNICA_DASHBOARD.md  # Evaluacion y propuestas de mejora
    └── TODO_CORRECCIONES.md             # Lista de correcciones y optimizaciones
```

## Base de Datos

### Conexion
- PostgreSQL configurado via `.env` en la raiz del proyecto
- Variables requeridas: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `database.py` usa `pydantic-settings` para cargar el `.env`

### Esquema de Datos (Gold Layer)

**`gold.fact_ventas`** - Hechos de ventas
- `id_cliente`, `id_articulo`, `fecha_comprobante`, `nro_doc`, `id_sucursal`
- `cantidades_total` (bultos), `subtotal_final` (facturacion)
- `anulado` (boolean) - NO filtrar por anulado, incluir todas las ventas en los calculos

**`gold.dim_cliente`** - Dimension clientes
- `id_cliente`, `razon_social`, `fantasia`
- `latitud`, `longitud` (coordenadas geograficas)
- `des_localidad`, `des_provincia`, `des_ramo`
- `des_canal_mkt`, `des_segmento_mkt`, `des_subcanal_mkt`
- `des_lista_precio`, `des_sucursal`, `id_sucursal`
- `id_ruta_fv1`, `id_ruta_fv4` (rutas por fuerza de venta)
- `des_personal_fv1`, `des_personal_fv4` (preventistas)
- `anulado` (boolean) - para mapas se filtra `anulado = FALSE` en dim_cliente

**`gold.dim_articulo`** - Dimension articulos
- `id_articulo`, `generico`, `marca`, `des_articulo`

**`gold.fact_stock`** - Stock actual (usado en dashboard YTD para dias de inventario)

**Ver `CONTEXT_IA.md` para el esquema completo (fuente de verdad).**

### Consideraciones Importantes de Datos

1. **Clientes sin coordenadas**: Algunos clientes no tienen `latitud`/`longitud`. Para mapas, filtrar coordenadas validas solo en visualizacion, NO en queries de datos.

2. **Mapas: partir de dim_cliente**: `cargar_ventas_por_cliente()` parte de `dim_cliente WHERE anulado = FALSE` y hace LEFT JOIN a una subquery de `fact_ventas` (con filtros de fecha/articulo). Asi aparecen TODOS los clientes activos en el mapa, incluso los que no compraron en el periodo. Los filtros de cliente (canal, ruta, etc.) van en WHERE sobre dim_cliente.

3. **Queries de metricas temporales**: `cargar_ventas_por_fecha()` y similares parten de `fact_ventas` con LEFT JOIN a `dim_cliente` (solo para aplicar filtros de cliente). JOIN simplificado: `f.id_cliente = c.id_cliente` (sin id_sucursal, ya que id_cliente es unico global).

4. **Fuerzas de Venta (FV)**:
   - FV1 y FV4 son fuerzas de venta independientes
   - Cada una tiene sus propias rutas (`id_ruta_fv1`, `id_ruta_fv4`) y preventistas (`des_personal_fv1`, `des_personal_fv4`)
   - Los filtros de ruta/preventista deben considerar la FV seleccionada

5. **Claves compuestas de rutas**: Los codigos de ruta NO son globalmente unicos — se repiten entre sucursales. La clave unica es `(id_sucursal, id_ruta)`. En filtros SQL usar tuplas: `(c.id_sucursal, c.id_ruta_fvX) IN ((suc1, ruta1), ...)`. Los valores del MultiSelect de rutas son strings compuestos `"id_sucursal|id_ruta"`.

6. **Clientes (`id_cliente`)**: Son globalmente unicos, NO necesitan clave compuesta.

## Sistema de Navegacion

El proyecto usa routing basado en URL:
- `/` -> Pagina de inicio (cards de tableros)
- `/ventas` -> Dashboard de ventas (mapas + tablero comparativo)
- `/ytd` -> Dashboard YTD (indicadores acumulados anuales)
- `/clientes` -> Busqueda de clientes
- `/cliente/<id>` -> Detalle de cliente (ventas por generico/marca/articulo)
- `/nuevo` -> Placeholder para nuevos tableros

Para agregar un nuevo tablero:
1. Crear layout en `layouts/nuevo_layout.py`
2. Crear callbacks en `callbacks/nuevo_callbacks.py`
3. Agregar ruta en `app.py` dentro de `display_page()`
4. Agregar card en `layouts/home_layout.py`

## Dashboard de Ventas (`/ventas`)

### Pestanas
- **Mapas**: Mapa de Burbujas, Mapa de Calor, Mapa Compro/No Compro
- **Tablero de Ventas**: Grafico de comparacion anual + tabla comparativa + top genericos/marcas

### Filtros compartidos (panel lateral dmc.Drawer con tema oscuro)
- Rango de fechas, Canal, Subcanal, Localidad
- Lista de Precio, Tipo Sucursal, Sucursal
- Generico, Marca (cascada)
- Fuerza de Venta, Ruta, Preventista
- Metrica (Bultos / Facturacion / Documentos)
- Opciones de zonas (Ruta / Preventista), Animacion temporal

### Mapa de Burbujas - Caracteristicas especiales
- **Escala fija 0-15**: Color y tamano de burbuja normalizados a rango [0, 15]
- **Sin ventas**: Circulos rojos (`#ff0000`) con hover mostrando id_cliente
- **Hover MAct/MAnt**: Top 5 genericos por cliente con bultos mes actual vs anterior
- **Click**: Abre `/cliente/<id>` en nueva pestana
- **Badges de ruta**: Overlay `dmc.HoverCard` sobre el mapa con info por zona:
  - Ventas (bultos) MAct / MAnt por generico + total
  - Cantidad de compradores por generico (MAct / MAnt)
- **Zonas**: Convex hull por ruta o preventista con colores distintos

### Callbacks (callbacks/callbacks.py)
- `toggle_drawer()`: Abrir/cerrar panel de filtros
- `actualizar_rutas_preventistas()`: Actualizar rutas y preventistas segun FV
- `actualizar_filtros()`: Actualizar opciones de dropdowns segun fechas
- `actualizar_marcas_por_generico()`: Filtro cascada generico -> marca
- `actualizar_sucursal_por_tipo()`: Auto-filtro tipo sucursal
- `actualizar_resumen_ventas()`: Graficos evolucion + top genericos + top marcas
- `actualizar_mapa()`: Mapa de burbujas + KPIs + badges de zona
- `actualizar_mapa_calor()`: Mapa de calor (difuso/grilla)
- `actualizar_mapa_compro()`: Mapa compro vs no compro
- `toggle_secciones_principales()`: Mostrar/ocultar mapas vs tablero
- `actualizar_opciones_anios()`: Cargar anos disponibles
- `actualizar_grafico_comparacion_anual()`: Grafico de lineas por ano
- `actualizar_tabla_comparativa()`: Tabla mensual con % crecimiento
- Click mapa -> `/cliente/<id>` (clientside callback)

### Funciones de datos (data/queries.py)
- `cargar_ventas_por_cliente()`: Ventas agregadas por cliente (mapas y KPIs). Parte de dim_cliente.
- `cargar_ventas_por_fecha()`: Ventas por fecha (graficos temporales). Parte de fact_ventas.
- `cargar_ventas_animacion()`: Ventas por cliente y periodo (animaciones)
- `cargar_ventas_por_cliente_generico()`: Top N genericos por cliente, MAct/MAnt (hover)
- `cargar_ventas_por_generico_top()`: Top genericos por metrica
- `cargar_ventas_por_marca_top()`: Top marcas por metrica
- `obtener_*()`: Funciones para poblar dropdowns

## Dashboard YTD (`/ytd`)

### Indicadores (KPIs)
- Ventas (Bultos), Interanual (YoY %)
- Objetivo de Ventas (ano anterior + 10%)
- Cumplimiento Objetivo (%)
- Ventas Ano Anterior
- Ganancia Bruta (placeholder)
- Margen de Ganancia (placeholder)

### Graficos
- Ventas por Generico (barras apiladas con target)
- Ventas Reales vs Objetivo (mensual, colores semaforo)
- Ventas por Sucursal (barras horizontales real vs objetivo)
- Ventas por Canal (dona)
- Crecimiento de Ventas (barras +/-)
- Dias de Inventario (gauge)

### Filtros
- Ano, Mes (hasta), Tipo Sucursal

### Target automatico
- `incremento_pct=10` hardcodeado en callbacks (ano anterior + 10%)
- Se aplica a: total, por mes, por generico, por sucursal

### Etiquetas
- Todas las etiquetas del dashboard YTD estan en **espanol**

### Funciones de datos (data/ytd_queries.py)
- `obtener_ventas_ytd()`: Ventas acumuladas YTD
- `obtener_ventas_por_mes()`: Ventas desglosadas por mes
- `obtener_ventas_por_generico()`: Ventas por categoria
- `obtener_ventas_por_sucursal()`: Ventas por sucursal
- `obtener_ventas_por_canal()`: Ventas por canal
- `calcular_target_automatico()`: Target total y por mes
- `calcular_targets_por_generico()`: Targets por generico
- `calcular_targets_por_sucursal()`: Targets por sucursal
- `calcular_crecimiento_mensual()`: Crecimiento % vs ano anterior
- `obtener_dias_inventario()`: Dias de inventario (stock / venta diaria)

## Detalle de Cliente (`/cliente/<id>`)

### Acceso
- Click en burbuja del mapa -> abre en nueva pestana
- Buscar en `/clientes` -> click en resultado

### Contenido
- **Header**: Nombre, codigo, localidad, canal, sucursal, preventista, ruta
- **KPIs**: Bultos mes actual, facturacion mes actual, documentos mes actual + texto explicativo
- **Tabla plana**: Jerarquia generico -> marca -> articulo con columnas de ultimos 12 meses calendario
  - Subtotales por marca y generico
  - Separacion entre articulos con/sin ventas
  - Jump-to dropdowns para navegar a un generico o marca especifica (scroll)
- **Export Excel**: 3 hojas (Por Generico, Por Marca, Detalle Articulos)

### Callbacks (callbacks/cliente_callbacks.py)
- `cargar_detalle_cliente()`: Carga info + tabla + KPIs
- `exportar_marca_excel()`: Export Excel de una marca
- `exportar_completo_excel()`: Export Excel completo (3 hojas)
- Clientside callbacks para scroll a generico/marca

### Funciones de datos (data/queries.py)
- `cargar_info_cliente()`: Datos maestros del cliente
- `cargar_ventas_cliente_detalle()`: Historico con jerarquia generico/marca/articulo

## Busqueda de Clientes (`/clientes`)

- Input de busqueda con debounce
- Busca por razon_social, fantasia o id_cliente
- Resultados como links a `/cliente/<id>`

## Convenciones de Codigo

### SQL
- NO filtrar por `anulado` en fact_ventas — incluir todas las ventas (anuladas y no anuladas)
- Mapas: partir de `dim_cliente WHERE anulado = FALSE` con LEFT JOIN a fact_ventas
- Metricas temporales: partir de `fact_ventas` con LEFT JOIN a dim_cliente
- Usar `COALESCE()` para valores por defecto en campos nullable
- Usar parametros escapados para prevenir SQL injection
- Claves compuestas de rutas: `(id_sucursal, id_ruta)` en tuplas SQL

### Callbacks
- Usar `prevent_initial_call=True` cuando no se necesite ejecucion inicial
- Manejar valores None/vacios en filtros con `if filtro and len(filtro) > 0`
- Para filtros numericos como rutas, convertir a lista de strings si es necesario

### Visualizacion
- Tema oscuro centralizado en `config.py` (dict `DARK` con 16+ colores)
- Colores definidos en `config.py` (COLOR_SCALE_*, ZONE_COLORS)
- Metricas con labels en `METRICA_LABELS`
- Mapas usan `map_style='open-street-map'`
- Fuentes del YTD Dashboard aumentadas 25% sobre tamano original
- Escala fija 0-15 en mapa de burbujas (color y tamano)

### Componentes dmc (dash-mantine-components v2.5.1)
- `data` en vez de `options` para MultiSelect/Select
- `checked` en vez de `value` para Switch
- `maxValues` (no `maxSelectedValues`) para MultiSelect
- `DatePickerInput(type="range")`: `value` retorna `[start, end]` como lista
- Estilos dark theme: `styles` prop con keys `input`, `label`, `dropdown`, `option`, `pill`
- SegmentedControl dark: `styles` con `root`, `label`, `indicator`

### Versionado
- Versionado semantico: `MAJOR.MINOR.PATCH`
- Solo una version en produccion (modelo milestones, no ramas paralelas)
- Bugs se corrigen como PATCH en la version actual
- Git tags anotados para cada release

## Ejecucion

```bash
cd ~/Desktop/sales-dashboard
# Configurar variables de entorno
cp .env.example .env  # completar credenciales
# Instalar dependencias
pip install -r requirements.txt
# Ejecutar
python3 app.py
# Acceder en http://localhost:8050
```

## Dependencias Principales
- dash, plotly, dash-mantine-components
- pandas, numpy
- sqlalchemy, psycopg2-binary
- pydantic, pydantic-settings
- scipy (para zonas convex hull)
- openpyxl (para export Excel en /cliente)

## Deployment

- **Repositorio**: GitHub (`github` remote) + servidor de produccion (`production` remote)
- **Produccion**: Push a `production` remote en `nahuel@100.72.221.10:/srv/git/sales-dashboard.git`
- **Branch unico**: `main` (trunk-based development)
