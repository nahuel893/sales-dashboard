# Spec: Descripciones de Ruta en Filtro de Rutas

> **Estado:** DRAFT
> **Fecha:** 2026-03-02
> **Autor:** nahuel

## 1. Objetivo

Mostrar la descripcion de la ruta (nombre del preventista + dias de visita) junto al ID en el dropdown de filtro de rutas, cambiando el formato de label de `"5 (Sucursal Centro)"` a `"5 - CACHAGUA EZEQUIEL MA-VI (Sucursal Centro)"`.

## 2. Contexto

El dropdown `filtro-ruta` en `/ventas` y `/tablero` actualmente muestra solo el ID numerico de la ruta y el nombre de la sucursal. Esto es insuficiente para que los usuarios identifiquen una ruta de forma rapida sin conocer los codigos de memoria. La descripcion de la ruta (ej: `"CACHAGUA EZEQUIEL MA-VI"`) representa al preventista y sus dias de visita, que es exactamente la informacion que los usuarios necesitan para filtrar.

El campo `des_ruta` existe en `silver.routes`, pero el usuario de base de datos del dashboard (`reporting_user`) solo tiene acceso al schema `gold`. No existe una tabla o vista `gold.dim_ruta`. La solucion mas practica, dado que el ETL es un proyecto separado, es otorgar acceso de lectura a `silver.routes` al `reporting_user` y hacer el JOIN directamente en `obtener_rutas()`.

## 3. Requisitos Funcionales

- **RF-001**: Cuando el sistema carga las opciones del filtro de rutas (al inicio de la app o al cambiar la Fuerza de Venta), el sistema debe incluir `des_ruta` de `silver.routes` en el label de cada opcion, usando el formato `"{id_ruta} - {des_ruta} ({sucursal})"`.

- **RF-002**: Cuando una ruta no tiene descripcion en `silver.routes` (sin match en el JOIN), el sistema debe usar el formato anterior como fallback: `"{id_ruta} ({sucursal})"`, sin mostrar un guion ni campo vacio.

- **RF-003**: Cuando el usuario filtra por Fuerza de Venta (FV1, FV4 o TODOS), el sistema debe mostrar la descripcion correcta para cada ruta, considerando que `silver.routes` tiene la columna `id_fuerza_ventas` que permite distinguir rutas con el mismo `id_ruta` e `id_sucursal` entre fuerzas de venta distintas.

- **RF-004**: Mientras el usuario escribe en el campo de busqueda del MultiSelect de rutas, el sistema debe permitir buscar tanto por ID de ruta como por descripcion (`des_ruta`), ya que el componente `dmc.MultiSelect` con `searchable=True` busca sobre el campo `label`.

- **RF-005**: Si `reporting_user` no tiene acceso a `silver.routes`, el sistema debe fallar con un error de base de datos explicito al cargar la app, en lugar de mostrar rutas sin descripcion silenciosamente.

- **RF-006**: El `value` del MultiSelect (campo `"id_sucursal|id_ruta"`) no debe cambiar. Todos los callbacks que leen `filtro-ruta` y usan el valor para filtrar queries SQL no requieren ninguna modificacion.

## 4. Requisitos No Funcionales

- **RNF-001**: El JOIN a `silver.routes` no debe incrementar el tiempo de carga de `obtener_rutas()` en mas de 200ms respecto al tiempo actual (la tabla tiene ~210 rutas vigentes, el impacto debe ser despreciable).

- **RNF-002**: El label de ruta no debe superar aproximadamente 60 caracteres para no truncarse visiblemente en el dropdown. Si `des_ruta` puede ser larga, el campo se muestra tal cual (no se trunca en backend; dmc maneja el overflow visualmente).

- **RNF-003**: El GRANT sobre `silver.routes` debe quedar documentado en un archivo SQL en el repositorio para que sea reproducible en nuevos entornos o tras recrear el rol `reporting_user`.

## 5. Diseno Tecnico

### 5.1 Modelo de Datos

No hay cambios de DDL. Se accede a una tabla existente en silver:

```sql
-- silver.routes (solo columnas relevantes)
-- id_ruta          INTEGER
-- des_ruta         VARCHAR   -- ej: "CACHAGUA EZEQUIEL MA-VI"
-- id_sucursal      INTEGER
-- id_fuerza_ventas INTEGER   -- 1=FV1, 4=FV4
-- fecha_hasta      DATE      -- '9999-12-31' = vigente
-- anulado          BOOLEAN
-- UNIQUE(id_ruta, id_sucursal, id_fuerza_ventas)
```

Se requiere este GRANT ejecutado una vez en la base de datos:

```sql
GRANT SELECT ON silver.routes TO reporting_user;
```

Este GRANT debe guardarse en `auth/grants.sql` (archivo nuevo) para documentacion y reproducibilidad.

### 5.2 Arquitectura

El cambio es contenido en una sola funcion: `obtener_rutas()` en `data/queries.py` (lineas 45-82). Ningun callback ni layout necesita cambios porque:

- El `value` del MultiSelect (`"id_sucursal|id_ruta"`) no cambia.
- La funcion ya retorna `[{"label": ..., "value": ...}]` y los consumidores usan ese formato directamente.
- `dmc.MultiSelect` con `searchable=True` busca sobre `label`, por lo que la busqueda por descripcion queda habilitada automaticamente (RF-004).

Consumidores actuales de `obtener_rutas()`:

| Archivo | Linea | Uso |
|---|---|---|
| `app.py` | 42 | Carga inicial al arrancar la app (`lista_rutas = obtener_rutas()`) |
| `callbacks/callbacks.py` | 51 | Callback `actualizar_rutas_preventistas` en `/ventas` |

### 5.3 API / Interfaz

**Funcion modificada:** `obtener_rutas(fuerza_venta=None)` en `data/queries.py`

**Input:** `fuerza_venta` — string `'FV1'`, `'FV4'` o `None` (para TODOS)

**Output (sin cambios en estructura):**
```python
[
    {"label": "5 - CACHAGUA EZEQUIEL MA-VI (Sucursal Centro)", "value": "1|5"},
    {"label": "12 - ROBLES ORLANDO MISA (Sucursal Norte)", "value": "2|12"},
    # Si sin match en silver.routes (fallback):
    {"label": "99 (Sucursal Sur)", "value": "3|99"},
]
```

**Logica del JOIN para FV1 (ejemplo):**

```sql
SELECT DISTINCT
    c.id_sucursal,
    c.id_ruta_fv1                              AS id_ruta,
    COALESCE(c.des_sucursal, 'Sin sucursal')   AS sucursal,
    r.des_ruta
FROM gold.dim_cliente c
LEFT JOIN silver.routes r
    ON  r.id_ruta      = c.id_ruta_fv1
    AND r.id_sucursal  = c.id_sucursal
    AND r.id_fuerza_ventas = 1
    AND r.fecha_hasta  = '9999-12-31'
    AND r.anulado      = FALSE
WHERE c.id_ruta_fv1 IS NOT NULL
ORDER BY sucursal, id_ruta
```

Para FV4: igual pero con `id_fuerza_ventas = 4` y `c.id_ruta_fv4`.

Para TODOS: UNION de ambas queries (igual al patron actual).

**Construccion del label en Python:**

```python
# Dentro del list comprehension de retorno
label = (
    f"{row['id_ruta']} - {row['des_ruta']} ({row['sucursal']})"
    if pd.notna(row['des_ruta']) and row['des_ruta'].strip()
    else f"{row['id_ruta']} ({row['sucursal']})"
)
```

## 6. Edge Cases y Constraints

| Caso | Comportamiento esperado |
|---|---|
| Ruta sin match en `silver.routes` (LEFT JOIN retorna NULL) | Label fallback: `"{id_ruta} ({sucursal})"` sin guion ni texto vacio |
| `des_ruta` es string vacio o solo espacios | Mismo fallback — tratar como NULL |
| UNION de FV1 y FV4 con misma `(id_sucursal, id_ruta)` en ambas fuerzas | Pueden aparecer dos entradas distintas con diferente `des_ruta`; el DISTINCT de la UNION opera sobre la tupla `(id_sucursal, id_ruta, sucursal, des_ruta)`. Si en la practica las descripciones coinciden, el DISTINCT colapsa la duplicacion. Si difieren, aparecen ambas (caso raro segun el constraint UNIQUE del schema). |
| `reporting_user` sin GRANT a `silver.routes` | La query falla con `PermissionError` de PostgreSQL al arrancar la app. El error es explicito y detectable (RF-005). |
| Rutas con `fecha_hasta != '9999-12-31'` (rutas inactivas) | El JOIN filtra solo rutas vigentes. Si un cliente en `dim_cliente` tiene una ruta inactiva sin match vigente, aplica el fallback de RF-002. |

## 7. Plan de Testing

- [ ] Test: Ejecutar `obtener_rutas()` sin argumentos y verificar que todos los items del resultado tienen `"label"` con formato `"{id} - {desc} ({suc})"` o `"{id} ({suc})"` (nunca ` -  ` ni guion con descripcion vacia) — valida RF-001, RF-002.
- [ ] Test: Ejecutar `obtener_rutas('FV1')` y `obtener_rutas('FV4')` por separado, verificar que cada ruta aparece con la descripcion correcta para su fuerza de venta — valida RF-003.
- [ ] Test: Verificar que todos los `value` en el resultado de `obtener_rutas()` tienen formato `"{int}|{int}"` (sin cambios) — valida RF-006.
- [ ] Test manual: Abrir `/ventas`, escribir parte del nombre del preventista en el filtro de rutas y verificar que el MultiSelect filtra correctamente — valida RF-004.
- [ ] Test manual: Revocar GRANT a `silver.routes` y verificar que la app falla con error explicito al arrancar — valida RF-005.

## 8. Tareas de Implementacion

1. **Crear `auth/grants.sql`** con el GRANT documentado.
   - Archivos: `auth/grants.sql` (nuevo)
   - Ejecutar en la base de datos: `GRANT SELECT ON silver.routes TO reporting_user;`

2. **Modificar `obtener_rutas()` en `data/queries.py`** para agregar LEFT JOIN a `silver.routes` en las tres ramas (FV1, FV4, TODOS) y actualizar la construccion del label con logica de fallback.
   - Archivos: `data/queries.py` (lineas 45-82)
   - Depende de: Tarea 1 (el GRANT debe existir antes de que la app pueda ejecutar la query)

## 9. Boundaries (Lo que NO hacer)

- NO modificar ningun callback que consuma `filtro-ruta` — el `value` no cambia.
- NO modificar los layouts (`main_layout.py`, `tablero_layout.py`) — el MultiSelect ya tiene `searchable=True`.
- NO agregar `des_ruta` como columna a `gold.dim_cliente` — eso es responsabilidad del ETL (proyecto separado).
- NO crear una vista materializada `gold.dim_ruta` — fuera de scope de este proyecto.
- NO modificar la logica de filtrado SQL en `cargar_ventas_por_cliente()` u otras queries — los filtros de ruta siguen usando `"id_sucursal|id_ruta"` sin cambios.

## 10. Decisiones Abiertas

- [ ] Confirmar que `reporting_user` es el rol correcto (y unico rol) usado por el dashboard para conectarse a PostgreSQL. Si hay multiples roles, el GRANT debe aplicarse a todos los que necesiten acceso al filtro de rutas.
