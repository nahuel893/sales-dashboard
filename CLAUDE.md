# Sales Dashboard - Guía para Claude

## Descripción del Proyecto

Dashboard interactivo de ventas construido con Dash/Plotly que visualiza datos de un sistema ETL medallion (bronze → silver → gold). Conecta a PostgreSQL y presenta mapas geográficos, KPIs, análisis temporal y dashboard YTD.

**Versión actual:** 1.0.0 (ver `VERSION`, `CHANGELOG.md`, `ROADMAP.md`)

## Estructura del Proyecto

```
sales-dashboard/
├── app.py                     # Punto de entrada, routing entre tableros
├── config.py                  # Configuración central (colores, estilos, constantes)
├── database.py                # Conexión SQLAlchemy a PostgreSQL (carga .env local)
├── .env                       # Variables de entorno (NO commitear, está en .gitignore)
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias Python
├── VERSION                    # Versión actual del proyecto
├── CHANGELOG.md               # Historial de cambios por versión
├── ROADMAP.md                 # Plan de versiones futuras
├── layouts/
│   ├── home_layout.py         # Página de inicio con cards de navegación
│   ├── main_layout.py         # Layout del dashboard de ventas (create_ventas_layout)
│   └── ytd_layout.py          # Layout del dashboard YTD (create_ytd_layout)
├── callbacks/
│   ├── callbacks.py           # Callbacks del dashboard de ventas
│   └── ytd_callbacks.py       # Callbacks del dashboard YTD
├── data/
│   ├── queries.py             # Queries SQL del dashboard de ventas
│   └── ytd_queries.py         # Queries SQL del dashboard YTD
├── utils/
│   └── visualization.py       # Funciones de visualización (grillas, zonas convex hull)
├── components/                # (reservado para componentes reutilizables)
└── docs/
    └── EVALUACION_TECNICA_DASHBOARD.md  # Evaluación y propuestas de mejora
```

## Base de Datos

### Conexión
- PostgreSQL configurado via `.env` en la raíz del proyecto
- Variables requeridas: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `database.py` usa `pydantic-settings` para cargar el `.env`

### Esquema de Datos (Gold Layer)

**`gold.fact_ventas`** - Hechos de ventas
- `id_cliente`, `id_articulo`, `fecha_comprobante`, `nro_doc`
- `cantidades_total` (bultos), `subtotal_final` (facturación)
- `anulado` (boolean) - NO filtrar por anulado, incluir todas las ventas en los cálculos

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

**`gold.fact_stock`** - Stock actual (usado en dashboard YTD para días de inventario)

### Consideraciones Importantes de Datos

1. **Clientes sin coordenadas**: Algunos clientes no tienen `latitud`/`longitud`. Para mapas, filtrar coordenadas válidas solo en visualización, NO en queries de datos.

2. **Clientes no en dim_cliente**: Hay ventas en `fact_ventas` para clientes que no existen en `dim_cliente` (clientes anulados). Las queries DEBEN partir de `fact_ventas` con `LEFT JOIN` a `dim_cliente` para incluir todas las ventas.

3. **COALESCE en filtros**: Cuando se filtran campos de `dim_cliente` en SQL, usar siempre `COALESCE()` para manejar NULLs de clientes sin dim_cliente. Ejemplo: `COALESCE(c.des_canal_mkt, 'Sin canal') IN (...)`. Esto aplica tanto a queries directas como a `cargar_ventas_por_fecha()`.

4. **Fuerzas de Venta (FV)**:
   - FV1 y FV4 son fuerzas de venta independientes
   - Cada una tiene sus propias rutas (`id_ruta_fv1`, `id_ruta_fv4`) y preventistas (`des_personal_fv1`, `des_personal_fv4`)
   - Los filtros de ruta/preventista deben considerar la FV seleccionada

5. **Claves compuestas de rutas**: Los códigos de ruta NO son globalmente únicos — se repiten entre sucursales. La clave única es `(id_sucursal, id_ruta)`. En filtros SQL usar tuplas: `(c.id_sucursal, c.id_ruta_fvX) IN ((suc1, ruta1), ...)`. Los valores del MultiSelect de rutas son strings compuestos `"id_sucursal|id_ruta"`.

6. **Clientes (`id_cliente`)**: Son globalmente únicos, NO necesitan clave compuesta.

## Sistema de Navegación

El proyecto usa routing basado en URL:
- `/` → Página de inicio (cards de tableros)
- `/ventas` → Dashboard de ventas (mapas + tablero comparativo)
- `/ytd` → Dashboard YTD (indicadores acumulados anuales)
- `/nuevo` → Placeholder para nuevos tableros

Para agregar un nuevo tablero:
1. Crear layout en `layouts/nuevo_layout.py`
2. Crear callbacks en `callbacks/nuevo_callbacks.py`
3. Agregar ruta en `app.py` dentro de `display_page()`
4. Agregar card en `layouts/home_layout.py`

## Dashboard de Ventas (`/ventas`)

### Pestañas
- **Mapas**: Mapa de Burbujas, Mapa de Calor, Mapa Compró/No Compró
- **Tablero de Ventas**: Gráfico de comparación anual + tabla comparativa

### Filtros compartidos
- Rango de fechas, Canal, Subcanal, Localidad
- Lista de Precio, Tipo Sucursal, Sucursal
- Genérico, Marca (cascada)
- Fuerza de Venta, Ruta, Preventista
- Métrica (Bultos / Facturación / Documentos)

### Callbacks (callbacks/callbacks.py)
- `actualizar_mapa()`: Mapa de burbujas + KPIs
- `actualizar_mapa_calor()`: Mapa de calor (difuso/grilla)
- `actualizar_mapa_compro()`: Mapa compró vs no compró
- `actualizar_grafico_comparacion_anual()`: Gráfico de líneas por año
- `actualizar_tabla_comparativa()`: Tabla mensual con % crecimiento
- `actualizar_sucursal_por_tipo()`: Auto-filtro tipo sucursal

### Funciones de datos (data/queries.py)
- `cargar_ventas_por_cliente()`: Ventas agregadas por cliente (mapas y KPIs)
- `cargar_ventas_por_fecha()`: Ventas por fecha (gráficos temporales). Filtros de cliente usan COALESCE.
- `cargar_ventas_animacion()`: Ventas por cliente y período (animaciones)
- `obtener_*()`: Funciones para poblar dropdowns

## Dashboard YTD (`/ytd`)

### Indicadores (KPIs)
- Ventas (Bultos), Interanual (YoY %)
- Objetivo de Ventas (año anterior + 10%)
- Cumplimiento Objetivo (%)
- Ventas Año Anterior
- Ganancia Bruta (placeholder)
- Margen de Ganancia (placeholder)

### Gráficos
- Ventas por Genérico (barras apiladas con target)
- Ventas Reales vs Objetivo (mensual, colores semáforo)
- Ventas por Sucursal (barras horizontales real vs objetivo)
- Ventas por Canal (dona)
- Crecimiento de Ventas (barras +/-)
- Días de Inventario (gauge)
- Días de Cuentas por Cobrar (placeholder)

### Filtros
- Año, Mes (hasta), Tipo Sucursal

### Target automático
- `incremento_pct=10` hardcodeado en callbacks (año anterior + 10%)
- Se aplica a: total, por mes, por genérico, por sucursal

### Etiquetas
- Todas las etiquetas del dashboard YTD están en **español**

### Funciones de datos (data/ytd_queries.py)
- `obtener_ventas_ytd()`: Ventas acumuladas YTD
- `obtener_ventas_por_mes()`: Ventas desglosadas por mes
- `obtener_ventas_por_generico()`: Ventas por categoría
- `obtener_ventas_por_sucursal()`: Ventas por sucursal
- `obtener_ventas_por_canal()`: Ventas por canal
- `calcular_target_automatico()`: Target total y por mes
- `calcular_targets_por_generico()`: Targets por genérico
- `calcular_targets_por_sucursal()`: Targets por sucursal
- `calcular_crecimiento_mensual()`: Crecimiento % vs año anterior
- `obtener_dias_inventario()`: Días de inventario (stock / venta diaria)

## Convenciones de Código

### SQL
- NO filtrar por `anulado` en fact_ventas — incluir todas las ventas (anuladas y no anuladas)
- Siempre partir de `fact_ventas` con `LEFT JOIN` a dimensiones
- Usar `COALESCE()` para valores por defecto en campos nullable
- En filtros SQL de campos de dim_cliente, usar `COALESCE()` para consistencia con filtros Python
- Usar parámetros escapados para prevenir SQL injection

### Callbacks
- Usar `prevent_initial_call=True` cuando no se necesite ejecución inicial
- Manejar valores None/vacíos en filtros con `if filtro and len(filtro) > 0`
- Para filtros numéricos como rutas, convertir a lista de strings si es necesario

### Visualización
- Colores definidos en `config.py` (COLOR_SCALE_*, ZONE_COLORS)
- Métricas con labels en `METRICA_LABELS`
- Mapas usan `map_style='open-street-map'`
- Fuentes del YTD Dashboard aumentadas 25% sobre tamaño original

### Versionado
- Versionado semántico: `MAJOR.MINOR.PATCH`
- Solo una versión en producción (modelo milestones, no ramas paralelas)
- Bugs se corrigen como PATCH en la versión actual

## Ejecución

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
- dash, plotly
- pandas, numpy
- sqlalchemy, psycopg2-binary
- pydantic, pydantic-settings
- scipy (opcional, para zonas convex hull)
