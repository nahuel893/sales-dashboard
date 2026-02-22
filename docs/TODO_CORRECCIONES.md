# Correcciones y Optimizaciones del Dashboard

## Estado general

| Tipo | Total | Hechas | Pendientes |
|------|-------|--------|------------|
| Correcciones | 10 | 5 | 5 |
| Optimizaciones | 14 | 1 | 13 |

---

## Correcciones Aplicadas

### C1 — Clave compuesta en JOINs con `dim_cliente` (CRITICO) — HECHO

**Problema:** Todos los JOINs con `dim_cliente` usaban solo `id_cliente` como clave:
```sql
-- ANTES (incorrecto)
LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente
```

**Fundamento:** Según `CONTEXT_IA.md`, los IDs de cliente, vendedor y ruta **no son globalmente unicos** — son unicos por sucursal. Si dos sucursales tuvieran un cliente con el mismo `id_cliente`, el JOIN sin clave compuesta produciria un producto cartesiano parcial: cada venta matchearia con ambos clientes, duplicando filas y mezclando datos (localidad, canal, ruta, etc.) entre sucursales.

**Solucion aplicada:** Se agrego `AND f.id_sucursal = c.id_sucursal` en los 9 JOINs:
```sql
-- DESPUES (correcto)
LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
```

**Nota:** En la practica actual los `id_cliente` son unicos globalmente, por lo que el cambio no altera resultados. Es una correccion preventiva que protege contra datos futuros.

**Archivos modificados:** `data/queries.py` (3 JOINs), `data/ytd_queries.py` (6 JOINs)

---

### C2 — Eliminacion del filtro `anulado = FALSE` (CRITICO) — HECHO

**Problema:** Todas las queries filtraban `f.anulado = FALSE`, excluyendo ventas anuladas:
```sql
-- ANTES (incorrecto)
WHERE f.anulado = FALSE AND ...
```

**Fundamento:** `CONTEXT_IA.md` (linea 231) establece explicitamente: *"No filtrar por anulado: Las ventas anuladas deben incluirse en los calculos"*. El campo `anulado` existe en `fact_ventas` pero el ETL ya maneja la logica de anulacion en la capa de transformacion. Filtrar por `anulado = FALSE` en la capa de presentacion excluia ventas que el negocio necesita ver reflejadas en los totales (por ejemplo, notas de credito que anulan facturas — ambas deben computar para que el neto sea correcto).

**Solucion aplicada:** Se elimino `anulado = FALSE` de las 12 queries donde aparecia. En las funciones que construyen WHERE dinamico (`cargar_ventas_por_cliente`, `cargar_ventas_animacion`, `cargar_ventas_por_fecha`), se agrego fallback `"TRUE"` para cuando no hay filtros activos:
```python
# ANTES
where_clauses = ["f.anulado = FALSE"]
where_sql = " AND ".join(where_clauses)

# DESPUES
where_clauses = []
where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
```

**Decision del usuario:** Confirmado que no se filtra `anulado`. Ventas anuladas se incluyen en todos los calculos.

**Archivos modificados:** `data/queries.py` (5 eliminaciones), `data/ytd_queries.py` (7 eliminaciones), `CLAUDE.md` (directiva actualizada)

---

### C4 — NULL safety en `obtener_ventas_ytd` (MEDIO) — HECHO

**Problema:** Cuando `SUM()` no tiene filas que sumar, PostgreSQL devuelve una fila con valores NULL.

**Solucion aplicada:** Se agregaron checks `len(df) > 0` y fallback a 0 antes de acceder a `.iloc[0]`. Valores None se manejan con condicionales antes de operaciones aritmeticas.

**Archivo:** `data/ytd_queries.py`

---

### C5 — Rutas string vs int en SQL (BAJO) — HECHO

**Problema:** Tras la migracion a dmc, las rutas se manejaban como strings sin tipado correcto en SQL.

**Solucion aplicada:** Se implemento `_parse_rutas_compuestas()` que parsea valores compuestos `"id_sucursal|id_ruta"` a tuplas de enteros, y `_build_ruta_where()` que construye SQL con tuplas tipadas: `(c.id_sucursal, c.id_ruta_fvX) IN ((suc1, ruta1), ...)`.

**Archivo:** `data/queries.py`

---

### C6 — `WHEREf` sin espacio en `obtener_dias_inventario` (CRITICO) — HECHO

**Problema:** Faltaba un espacio entre `WHERE` y `f` en la query de ventas diarias.

**Solucion aplicada:** Corregido a `WHERE f.fecha_comprobante >= ...`.

**Archivo:** `data/ytd_queries.py`

---

## Correcciones Pendientes

### C3/C10 — Stock query no aplica filtro de sucursal (MEDIO)

**Problema:** En `obtener_dias_inventario()`, se construye `filtro_sucursal` segun el tipo de sucursal seleccionado, pero la query de stock no lo usa:
```python
# Se construye el filtro...
filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

# ...pero la query de stock lo ignora
query_stock = "SELECT COALESCE(SUM(stock), 0) as stock_total FROM gold.fact_stock"
```

**Impacto:** El gauge de "Dias de Inventario" siempre muestra el stock global, sin importar si el usuario filtro por sucursal o casa central. El denominador (ventas diarias) si filtra por sucursal, creando una metrica inconsistente.

**Nota:** `fact_stock` no tiene `id_sucursal` en su esquema actual. Requiere cambio en BD.

**Archivo:** `data/ytd_queries.py:280-293`

---

### C7 — `/cliente/<id>` no incluye `id_sucursal` en toda la pipeline (CRITICO)

**Problema:** La ruta de detalle de cliente usa solo `id_cliente`, pero segun la regla de clave compuesta, `id_cliente` no es globalmente unico — es unico por sucursal. Toda la pipeline esta afectada:

1. **URL:** `/cliente/<id_cliente>` — deberia ser `/cliente/<id_sucursal>/<id_cliente>`
2. **clientside_callback:** Solo extrae `id_cliente` de `customdata[5]` — falta `id_sucursal`
3. **`dcc.Store`:** Solo almacena `{'id_cliente': id}` — falta `id_sucursal`
4. **`cargar_info_cliente()`:** `WHERE c.id_cliente = {id}` sin `id_sucursal` — puede retornar multiples filas
5. **`cargar_ventas_cliente_detalle()`:** `WHERE f.id_cliente = {id}` sin `id_sucursal` — mezcla datos de sucursales

**Impacto:** Si un `id_cliente` existe en mas de una sucursal, la pagina muestra datos mezclados/incorrectos. En la practica actual los `id_cliente` son unicos globalmente, pero es una vulnerabilidad ante datos futuros.

**Solucion:** Agregar `id_sucursal` a: customdata del mapa, URL, store, queries, y routing en `app.py`.

**Archivos:** `callbacks/callbacks.py`, `app.py`, `layouts/cliente_layout.py`, `callbacks/cliente_callbacks.py`, `data/queries.py`

---

### C8 — ROW_NUMBER en hover siempre ordena por bultos (MEDIO)

**Problema:** La funcion `cargar_ventas_por_cliente_generico()` usa `ROW_NUMBER()` con `ORDER BY SUM(f.cantidades_total) DESC` hardcodeado. El top 5 de genericos en el hover siempre se rankea por bultos, sin importar la metrica seleccionada.

```sql
ROW_NUMBER() OVER (PARTITION BY f.id_cliente ORDER BY SUM(f.cantidades_total) DESC) as rn
```

**Impacto:** Cuando el usuario selecciona metrica "Documentos", el ranking (que genericos aparecen en el top 5) sigue correspondiendo a bultos. Los genericos fijos (`GENERICOS_HOVER_FIJOS`) siempre aparecen independientemente del ranking.

**Solucion:** Pasar `metrica` como parametro a la funcion y usar la columna correspondiente en el `ORDER BY` del `ROW_NUMBER()`.

**Archivo:** `data/queries.py`

---

### C9 — Mapa compro/no compro calcula centro con coordenadas invalidas (MEDIO)

**Problema:** `actualizar_mapa_compro` calcula el centro del mapa con `df['latitud'].mean()` sin filtrar coordenadas nulas o cero. A diferencia de `actualizar_mapa` que si filtra.

```python
if len(df) > 0:
    center_lat = df['latitud'].mean()   # incluye NaN y 0
    center_lon = df['longitud'].mean()
```

**Impacto:** Si hay clientes con `latitud=NaN`, el centro del mapa es `NaN` y el mapa no renderiza. Si hay muchos clientes con `(0, 0)`, el centro se desplaza hacia el Golfo de Guinea.

**Solucion:** Filtrar `df[df['latitud'].notna() & (df['latitud'] != 0)]` antes de calcular el centro.

**Archivo:** `callbacks/callbacks.py`

---

## Optimizaciones Pendientes

### Impacto ALTO

#### O1 — ~~`EXTRACT()` en WHERE impide uso de indices~~ ✅ HECHO

**Problema:** Las queries YTD usaban `EXTRACT(YEAR FROM fecha_comprobante) = 2025` en el WHERE. Esto aplicaba una funcion sobre la columna, forzando un full table scan porque el indice en `fecha_comprobante` no se puede usar.

**Solucion aplicada:** Reemplazado por rango de fechas con `make_date()`:
```sql
-- ANTES (full scan)
WHERE EXTRACT(YEAR FROM f.fecha_comprobante) = 2025
  AND EXTRACT(MONTH FROM f.fecha_comprobante) <= 7

-- DESPUES (index scan)
WHERE f.fecha_comprobante >= make_date(2025, 1, 1)
  AND f.fecha_comprobante < (make_date(2025, 7, 1) + INTERVAL '1 month')
```

**Impacto estimado:** 50-90% mas rapido en queries YTD.

**Archivo:** `data/ytd_queries.py` — 5 funciones corregidas: `obtener_ventas_ytd`, `obtener_ventas_por_mes`, `obtener_ventas_por_generico`, `obtener_ventas_por_sucursal`, `obtener_ventas_por_canal`

---

#### O2 — Queries redundantes N+1 en YTD

**Problema:** Un cambio de filtro en YTD dispara ~4 callbacks que ejecutan ~12-15 queries. Muchas son duplicadas: `obtener_ventas_ytd` se llama 2+ veces con los mismos parametros (una para el anio actual, otra internamente desde `calcular_target_automatico` para el anio anterior).

**Solucion propuesta:** Consolidar en 2-3 queries maestras que traigan todo lo necesario, o usar `dcc.Store` para cachear resultados compartidos.

**Archivos:** `callbacks/ytd_callbacks.py`, `data/ytd_queries.py`

---

#### O3 — 3 callbacks de mapa cargan datos identicos

**Problema:** `actualizar_mapa`, `actualizar_mapa_calor` y `actualizar_mapa_compro` ejecutan la misma query (`cargar_ventas_por_cliente`) independientemente. Cada cambio de filtro genera 3 queries identicas al DB.

**Solucion propuesta:** Usar `dcc.Store` para compartir el dataset entre los 3 callbacks, o un callback maestro que cargue datos una vez.

**Archivo:** `callbacks/callbacks.py`

---

#### O4 — Filtros aplicados en Python en vez de SQL

**Problema:** Los filtros de canal, subcanal, localidad, lista_precio y sucursal se aplican con `df.isin()` en Python despues de cargar el 100% de los datos:
```python
df = cargar_ventas_por_cliente(...)  # Trae TODOS los datos
if canales: df = df[df['canal'].isin(canales)]  # Filtra en memoria
```

**Nota:** Esto es parcialmente intencional — el mapa necesita TODOS los clientes activos (para mostrar los sin venta). Pero los filtros de canal/subcanal/localidad podrian pasarse a SQL.

**Solucion propuesta:** Pasar estos filtros como parametros a la query SQL para que el DB haga el filtrado.

**Archivo:** `callbacks/callbacks.py`

---

#### O5 — Sin cache entre callbacks

**Problema:** No hay mecanismo para compartir datos entre callbacks con los mismos inputs. Cada callback recalcula todo desde cero.

**Solucion propuesta:** Implementar `dcc.Store` o `lru_cache` para evitar queries duplicadas.

**Archivo:** `callbacks/callbacks.py` (global)

---

### Impacto MEDIO

#### O6 — ConvexHull se recalcula en cada render

`calcular_zonas()` ejecuta O(n log n) por zona sin cache. ~200 zonas = 200 calculos costosos por cambio de filtro.

**Archivo:** `utils/visualization.py`, `callbacks/callbacks.py`

---

#### O7 — `df.apply(axis=1)` en vez de vectorizacion

Las columnas `ruta` y `preventista` se calculan con `df.apply(lambda r: ..., axis=1)` (iteracion fila por fila). Deberia usarse `np.where()` vectorizado.

**Nota:** En v1.2.0 se agregaron mas `df.apply()` para pre-formatear hover lines (`_build_hover_lines`). Estas tambien se beneficiarian de vectorizacion.

**Archivo:** `data/queries.py`, `callbacks/callbacks.py`

---

#### O8 — Copias multiples de DataFrame

`_process_ventas_df` aplica 7+ `.astype()` que crean copias. Con 50K filas = 7+ DataFrames en memoria simultaneamente.

**Archivo:** `data/queries.py:168-194`

---

#### O9 — Animacion sin limite de periodos

Rango 1 anio + granularidad diaria = 365 periodos x 5K clientes = 1.8M filas. Puede crashear el navegador.

**Archivo:** `callbacks/callbacks.py`

---

#### O10 — Dataset completo para extraer valores unicos

`actualizar_filtros()` carga todo el dataset solo para hacer `df['canal'].unique()`. Deberia ser `SELECT DISTINCT` en SQL.

**Archivo:** `callbacks/callbacks.py`

---

### Impacto BAJO

#### O11 — `filtro_sucursal` duplicado 6 veces

El bloque que construye `filtro_sucursal` se repite identico en 6 funciones. Extraer a `_build_filtro_sucursal(tipo_sucursal)`.

**Archivo:** `data/ytd_queries.py`

---

#### O12 — `incremento_pct=10` hardcodeado

El 10% de incremento para targets esta hardcodeado en 4 lugares. Mover a `config.py`.

**Archivo:** `callbacks/ytd_callbacks.py`

---

#### O13 — Sin error handling en callbacks de ventas

Si falla una query, Dash muestra un error generico. Deberia haber try/except con mensajes claros.

**Archivo:** `callbacks/callbacks.py`

---

#### O14 — Sin logging en el proyecto

Errores silenciosos, imposible debuggear en produccion. Agregar logging basico.

**Archivos:** Todos

---

## Impacto estimado si se corrige todo

| Area | Estado actual | Despues de correcciones |
|------|--------------|------------------------|
| Queries por cambio de filtro (YTD) | ~12-15 | ~2-3 |
| Queries por cambio de filtro (Ventas) | ~3-4 duplicadas | ~1 compartida |
| Tiempo de query YTD (EXTRACT -> date range) | ✅ Index scan | ✅ Resuelto |
| Memoria (eliminar copias + filtrar en SQL) | Multiples copias completas | 50-70% menos uso |
| Correccion de datos (clave compuesta) | ✅ Preventivo aplicado | ✅ Resuelto |

---

## Orden sugerido de implementacion

1. ~~**C2** — Filtro `anulado`~~ ✅ HECHO
2. ~~**C1** — Clave compuesta en JOINs~~ ✅ HECHO
3. ~~**C6** — `WHEREf` sin espacio~~ ✅ HECHO
4. ~~**C4** — NULL safety~~ ✅ HECHO
5. ~~**C5** — Rutas string vs int~~ ✅ HECHO
6. ~~**O1** — EXTRACT -> date range~~ ✅ HECHO
7. **C9** — Centro de mapa compro con coordenadas validas (fix rapido)
8. **C8** — ROW_NUMBER por metrica seleccionada
9. **C7** — `id_sucursal` en pipeline `/cliente/` (preventivo, multiples archivos)
10. **C3/C10** — Stock query con filtro sucursal (requiere cambio en BD)
11. **O11** — Helper `filtro_sucursal` (simplifica el resto)
12. **O2** — Consolidar queries YTD (alto impacto)
13. **O4** — Filtros en SQL en vez de Python
14. **O3 + O5** — Cache/Store compartido entre callbacks
15. **O7 + O8** — Vectorizar `_process_ventas_df` + hover lines
16. **O10** — DISTINCT en SQL para filtros
17. Resto (O6, O9, O12, O13, O14)

---

*Generado: 2026-02-09*
*Ultima actualizacion: 2026-02-22*
*Referencia: CONTEXT_IA.md, CLAUDE.md*
