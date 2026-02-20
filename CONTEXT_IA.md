# Contexto del Data Warehouse - Medallion ETL

## Resumen del Proyecto

Este es un Data Warehouse construido con **arquitectura Medallion** (Bronze - Silver - Gold) que extrae datos de un ERP de distribucion comercial (Chess ERP) y los transforma para analisis.

## Arquitectura de Capas

```
Bronze (Raw)     ->     Silver (Clean)     ->     Gold (Analytics)
---------------------------------------------------------------------
Datos crudos JSON      Datos normalizados      Modelo dimensional
Sin transformacion     Tipados y limpios       Star Schema
```

## Ejecucion

```bash
# Carga diaria automatizada (crontab)
python3 daily_load.py              # Usa fecha de hoy
python3 daily_load.py 2025-06-15   # Fecha especifica

# Carga manual por capa/entidad
python3 orchestrator.py <capa> <entidad> [args...]
```

El `daily_load.py` ejecuta el pipeline completo Bronze -> Silver -> Gold en 10 fases.
Recarga el mes actual completo de ventas en cada ejecucion, y si es dia 1-3 tambien el mes anterior.

## Esquema Silver (Tablas normalizadas)

### Tablas de hechos
| Tabla | Descripcion |
|-------|-------------|
| `silver.fact_ventas` | Lineas de venta (con campo calculado `facturacion_neta`) |
| `silver.fact_stock` | Stock por deposito/articulo/fecha |

### Tablas de dimension/maestros
| Tabla | Descripcion |
|-------|-------------|
| `silver.branches` | Sucursales |
| `silver.sales_forces` | Fuerzas de venta |
| `silver.staff` | Personal (vendedores, supervisores, gerentes) |
| `silver.routes` | Rutas de venta (constraint: id_ruta, id_sucursal, id_fuerza_ventas) |
| `silver.clients` | Clientes (con segmentacion mkt y geolocalizacion) |
| `silver.client_forces` | Asignaciones cliente-ruta (constraint: id_cliente, id_ruta, fecha_inicio) |
| `silver.articles` | Articulos |
| `silver.article_groupings` | Agrupaciones de articulos (marca, generico, calibre, etc.) |
| `silver.marketing_segments` | Segmentos de marketing (nivel 1) |
| `silver.marketing_channels` | Canales de marketing (nivel 2, FK a segments) |
| `silver.marketing_subchannels` | Subcanales de marketing (nivel 3, FK a channels) |

## Esquema Gold (Usar para consultas)

La capa **Gold** es la recomendada para consultas analiticas. Contiene un modelo dimensional (star schema).

### Tablas de Dimensiones

| Tabla | Descripcion | Campos clave |
|-------|-------------|--------------|
| `gold.dim_tiempo` | Calendario | fecha, dia, dia_semana, nombre_dia, semana, mes, nombre_mes, trimestre, anio |
| `gold.dim_sucursal` | Sucursales | id_sucursal, descripcion |
| `gold.dim_vendedor` | Vendedores | id_vendedor, des_vendedor, id_fuerza_ventas, id_sucursal, des_sucursal |
| `gold.dim_articulo` | Articulos | id_articulo, des_articulo, marca, generico, calibre, proveedor, unidad_negocio |
| `gold.dim_cliente` | Clientes | id_cliente, razon_social, fantasia, id_sucursal, marketing (canal/segmento/subcanal), id_ruta_fv1, id_ruta_fv4, des_personal_fv1/fv4, ramo, localidad, provincia, lat/long, lista_precio |

### Tablas de Hechos

| Tabla | Descripcion | Granularidad |
|-------|-------------|--------------|
| `gold.fact_ventas` | Lineas de venta | Una fila por linea de comprobante |
| `gold.fact_stock` | Stock por deposito | Una fila por articulo/deposito/fecha (UNIQUE) |

### Tablas de Cobertura (Agregaciones mensuales)

| Tabla | Descripcion | Campos |
|-------|-------------|--------|
| `gold.cob_preventista_marca` | Cobertura por vendedor/ruta/marca | periodo, id_fuerza_ventas, id_vendedor, id_ruta, id_sucursal, marca, clientes_compradores, volumen_total |
| `gold.cob_sucursal_marca` | Cobertura por sucursal/marca | periodo, id_fuerza_ventas, id_sucursal, marca, clientes_compradores, volumen_total |
| `gold.cob_preventista_generico` | Cobertura por vendedor/ruta/generico | periodo, id_fuerza_ventas, id_vendedor, id_ruta, id_sucursal, generico, clientes_compradores, volumen_total |

## Campos Importantes

### fact_ventas (Silver - Tabla principal de ventas)
```sql
- fecha_comprobante     -- Fecha de la venta
- id_sucursal          -- Sucursal
- id_vendedor          -- Vendedor
- id_cliente           -- Cliente
- id_articulo          -- Articulo
- id_fuerza_ventas     -- Fuerza de venta
- cantidades_total     -- Cantidad vendida (unidades)
- facturacion_neta     -- cantidades_total * abs(precio_unitario_bruto) (campo calculado)
- subtotal_final       -- Monto total de la linea
- anulado              -- Boolean (incluir en consultas, no filtrar)
```

### fact_ventas (Gold - Metricas resumidas)
```sql
- fecha_comprobante     -- FK a dim_tiempo
- id_sucursal          -- FK a dim_sucursal
- id_vendedor          -- FK a dim_vendedor
- id_cliente           -- FK a dim_cliente
- id_articulo          -- FK a dim_articulo
- id_documento, letra, serie, nro_doc  -- Identificacion documento
- cantidades_con_cargo, cantidades_sin_cargo, cantidades_total
- subtotal_neto, subtotal_final, bonificacion
- anulado
```

### dim_vendedor
```sql
- id_vendedor          -- ID del vendedor (unico por sucursal)
- id_sucursal          -- Sucursal a la que pertenece
- des_vendedor         -- Nombre del vendedor
- id_fuerza_ventas     -- 1=FV1 (Preventa), 4=FV4 (Autoventa)
- des_sucursal         -- Descripcion de la sucursal
```

### dim_cliente
```sql
- id_cliente           -- ID del cliente
- razon_social         -- Nombre legal
- fantasia             -- Nombre de fantasia
- id_sucursal          -- Sucursal que lo atiende
- id_canal_mkt, id_segmento_mkt, id_subcanal_mkt  -- Segmentacion comercial
- id_ruta_fv1          -- Ruta asignada en Fuerza de Venta 1
- des_personal_fv1     -- Preventista FV1
- id_ruta_fv4          -- Ruta asignada en Fuerza de Venta 4
- des_personal_fv4     -- Preventista FV4
- id_ramo, des_ramo    -- Ramo comercial
- latitud, longitud    -- Geolocalizacion
- id_lista_precio      -- Lista de precios asignada
```

### dim_articulo
```sql
- id_articulo          -- ID del articulo
- des_articulo         -- Descripcion completa
- marca                -- Marca del producto
- generico             -- Categoria generica del producto
- calibre              -- Calibre
- proveedor            -- Proveedor
- unidad_negocio       -- Unidad de negocio
```

## Claves Compuestas (Importante)

### Vendedores y Rutas: requieren clave compuesta
Los IDs de vendedor y ruta **NO son unicos globalmente**. Son unicos **por sucursal**:

```sql
-- CORRECTO: JOIN vendedor con clave compuesta
JOIN gold.dim_vendedor dv
  ON fv.id_vendedor = dv.id_vendedor
  AND fv.id_sucursal = dv.id_sucursal

-- CORRECTO: Filtro de rutas con tuplas
WHERE (c.id_sucursal, c.id_ruta_fv1) IN ((1, 5), (2, 3), ...)
```

### Clientes: ID globalmente unico
`id_cliente` **ES unico globalmente** y NO necesita clave compuesta:

```sql
-- CORRECTO: JOIN cliente solo por id_cliente
LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente

-- INCORRECTO (innecesario): agregar id_sucursal
LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
```

## Fuerzas de Venta

Las fuerzas de venta son **grupos de preventistas que venden distintos articulos**:

| Fuerza | id_fuerza_ventas | Genericos que vende |
|--------|------------------|---------------------|
| FV1 | 1 | CERVEZAS, AGUAS DANONE, VINOS CCU, SIDRAS Y LICORES |
| FV4 | 4 | FRATELLI B, VINOS, JUGOS, VINOS FINOS |

- Un mismo cliente puede ser atendido por diferentes fuerzas de venta
- Cada FV tiene sus propias rutas asignadas
- Las rutas se cargan desde la API con `get_routes(fuerza_venta=N)`
- Solo se procesan rutas vigentes (`fecha_hasta = '9999-12-31'`)

## Constraints Silver

- `silver.routes`: `UNIQUE(id_ruta, id_sucursal, id_fuerza_ventas)` - Una ruta por sucursal y FV
- `silver.client_forces`: `UNIQUE(id_cliente, id_ruta, fecha_inicio)` - Asignacion unica por vigencia
- `silver.article_groupings`: `UNIQUE(id_articulo, id_forma_agrupar)` - Una agrupacion por tipo por articulo
- `silver.fact_stock`: `UNIQUE(date_stock, id_deposito, id_articulo)` - Un registro por dia/deposito/articulo
- Sin FKs entre tablas (por diseño medallion, la integridad la garantiza el ETL)

## Consultas de Ejemplo

### Ventas por Sucursal/Mes/Generico
```sql
SELECT
    fv.id_sucursal,
    ds.descripcion AS sucursal,
    EXTRACT(YEAR FROM fv.fecha_comprobante) AS anio,
    EXTRACT(MONTH FROM fv.fecha_comprobante) AS mes,
    da.generico,
    SUM(fv.cantidades_total) AS volumen_total,
    SUM(fv.facturacion_neta) AS facturacion_total
FROM gold.fact_ventas fv
LEFT JOIN gold.dim_articulo da ON fv.id_articulo = da.id_articulo
LEFT JOIN gold.dim_sucursal ds ON fv.id_sucursal = ds.id_sucursal
GROUP BY fv.id_sucursal, ds.descripcion, anio, mes, da.generico
ORDER BY fv.id_sucursal, anio, mes, volumen_total DESC;
```

### Ventas por Vendedor/Marca
```sql
SELECT
    fv.id_sucursal,
    ds.descripcion AS sucursal,
    fv.id_vendedor,
    dv.des_vendedor,
    EXTRACT(YEAR FROM fv.fecha_comprobante) AS anio,
    EXTRACT(MONTH FROM fv.fecha_comprobante) AS mes,
    da.marca,
    SUM(fv.cantidades_total) AS volumen_total
FROM gold.fact_ventas fv
LEFT JOIN gold.dim_articulo da ON fv.id_articulo = da.id_articulo
LEFT JOIN gold.dim_sucursal ds ON fv.id_sucursal = ds.id_sucursal
LEFT JOIN gold.dim_vendedor dv ON fv.id_vendedor = dv.id_vendedor
    AND fv.id_sucursal = dv.id_sucursal
GROUP BY fv.id_sucursal, ds.descripcion, fv.id_vendedor, dv.des_vendedor, anio, mes, da.marca
ORDER BY fv.id_sucursal, fv.id_vendedor, anio, mes, volumen_total DESC;
```

### Cobertura pre-calculada
```sql
SELECT * FROM gold.cob_preventista_marca
WHERE periodo = '2025-01-01'
ORDER BY id_sucursal, id_vendedor, volumen_total DESC;
```

## Notas Importantes

1. **No filtrar por anulado en fact_ventas**: Las ventas anuladas deben incluirse en los calculos
2. **Claves compuestas solo para vendedores y rutas**: Incluir `id_sucursal` en JOINs con dim_vendedor. Para dim_cliente, `id_cliente` es suficiente (es unico global)
3. **Rutas: clave compuesta `(id_sucursal, id_ruta)`**: Los codigos de ruta se repiten entre sucursales. Usar tuplas SQL para filtrar
4. **Mapas parten de dim_cliente**: Para mostrar todos los clientes activos (incluso sin ventas), partir de `dim_cliente WHERE anulado = FALSE` con LEFT JOIN a fact_ventas
5. **Queries de metricas parten de fact_ventas**: Para totales y series temporales, partir de `fact_ventas` con LEFT JOIN a dim_cliente (para aplicar filtros de cliente)
6. **COALESCE en filtros de dim_cliente**: Usar `COALESCE(c.campo, 'valor_default')` en filtros SQL porque el LEFT JOIN puede generar NULLs
7. **Cobertura no es sumable**: La cobertura de marca A + marca B no es la cobertura total (clientes pueden comprar ambas)
8. **Periodo en cobertura**: Es el primer dia del mes (ej: '2025-01-01' para enero 2025)
9. **facturacion_neta solo en Silver**: Gold fact_ventas no tiene este campo, usar `subtotal_final` directamente

## Arquitectura del Dashboard

```
Browser  <-->  Dash (Flask)  <-->  SQLAlchemy  <-->  PostgreSQL (gold layer)
```

- **Framework**: Dash/Plotly (Python) con Flask como servidor web
- **Componentes UI**: dash-mantine-components (dmc v2.5.1) para filtros y tooltips, Plotly para graficos y mapas
- **Conexion BD**: SQLAlchemy engine + pd.read_sql() (queries SQL directas, sin ORM)
- **Tema visual**: Paleta oscura completa centralizada en `config.py` (dict `DARK` con 16+ colores)
- **Paginas**:
  - Home (`/`) — Cards de navegacion
  - Ventas (`/ventas`) — Mapas interactivos (burbujas, calor, compro/no compro) + tablero comparativo
  - YTD (`/ytd`) — 7 KPIs + 6 graficos con targets automaticos
  - Buscar Clientes (`/clientes`) — Busqueda por nombre o codigo
  - Detalle Cliente (`/cliente/<id>`) — Tabla jerarquica generico->marca->articulo, export Excel
- **Filtros de ventas**: Panel lateral colapsable (dmc.Drawer) con tema oscuro
- **Mapa de burbujas**: Escala fija 0-15, hover MAct/MAnt, click abre detalle cliente, badges de zona con dmc.HoverCard
- **Sin cache**: Cada cambio de filtro ejecuta una query nueva a la BD
- **Sin autenticacion**: Acceso directo sin login
- **Deployment**: GitHub + servidor produccion via git remotes, branch unico `main`
