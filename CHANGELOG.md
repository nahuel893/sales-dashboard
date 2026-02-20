# Changelog

Todos los cambios notables de este proyecto seran documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Por agregar
- Mapa de oportunidades perdidas
- Metricas de eficiencia en zonas

---

## [1.1.0] - 2026-02-20

### Agregado

#### Detalle de Cliente (`/cliente/<id>`)
- Pagina de detalle accesible via click en mapa o busqueda
- Tabla plana con jerarquia generico -> marca -> articulo (ultimos 12 meses calendario)
- Subtotales por marca y generico
- KPIs del mes actual (bultos, facturacion, documentos) con texto explicativo
- Jump-to dropdowns para navegar a un generico o marca especifica (scroll)
- Export Excel con 3 hojas: Por Generico, Por Marca, Detalle Articulos
- Click en burbuja del mapa abre detalle en nueva pestana

#### Busqueda de Clientes (`/clientes`)
- Busqueda por razon_social, fantasia o id_cliente
- Resultados como links a `/cliente/<id>`
- Input con debounce para rendimiento

#### Mapa de Burbujas - Mejoras
- Escala fija 0-15 para color y tamano de burbujas
- Hover enriquecido: top 5 genericos por cliente con MAct/MAnt (mes actual vs anterior)
- Hover para clientes sin ventas: muestra desglose MAnt del mes anterior
- Circulos rojos (#ff0000) para clientes sin ventas con id_cliente visible
- Badges de ruta: overlay dmc.HoverCard sobre el mapa con info por zona
  - Ventas (bultos) MAct/MAnt por generico + total
  - Cantidad de compradores por generico con total de clientes
- Click en burbuja abre `/cliente/<id>` en nueva pestana

#### Zonas Geograficas
- Lista de clientes incluida en cada zona (para calculos de badges)
- Convex hull incluye clientes de la zona completa

#### UI / Tema Oscuro
- Migracion de filtros de `dcc` a `dash-mantine-components` (dmc v2.5.1)
- Panel lateral (dmc.Drawer) con tema oscuro completo
- Dark styles en todos los componentes: MultiSelect, DatePickerInput, SegmentedControl, Switch
- Labels blancos en secciones de filtros
- Aumento 25% fuentes generales + 50% valores numericos en YTD

### Cambiado
- Filtros de ventas: de accordion a layout plano
- KPIs de cliente: usan mes actual calendario (date.today()) en vez de ultimo mes con datos
- Tabla de cliente: ultimos 12 meses calendario (no ultimos 12 con datos)
- Escala de colores del mapa: de azul-naranja-rojo a azul-celeste-verde-amarillo
- Tamano de burbujas reducido y normalizado a escala fija

### Corregido
- C1: JOIN con clave compuesta preventiva en dim_cliente (id_sucursal + id_cliente)
- C2: Eliminacion del filtro `anulado = FALSE` en fact_ventas (ventas anuladas se incluyen)
- Colores de texto en filtros del drawer (dark theme)
- Ultimos 12 meses calendario en vez de ultimos 12 con datos
- Multiplicador IQR de 1.5 a 2.5 para zonas convex hull (menos clientes excluidos)
- Marcadores de sin ventas: de texto Unicode a circulos rojos nativos

### Tecnico
- Nuevo: `layouts/cliente_layout.py`, `layouts/clientes_layout.py`
- Nuevo: `callbacks/cliente_callbacks.py`, `callbacks/clientes_callbacks.py`
- Nuevo: funciones en `data/queries.py`: `cargar_info_cliente()`, `cargar_ventas_cliente_detalle()`, `buscar_clientes()`, `cargar_ventas_por_cliente_generico()`
- Dependencia agregada: `openpyxl` (export Excel)
- dmc.HoverCard para badges de zona (workaround: Plotly no soporta hover en polygons fill='toself')
- Documentacion actualizada: CLAUDE.md, README.md, CONTEXT_IA.md

---

## [1.0.0] - 2026-01-17

### Agregado

#### Sistema de Navegacion
- Pagina de inicio con cards de navegacion entre tableros
- Sistema de routing basado en URL (`/`, `/ventas`, `/ytd`)
- Boton "<- Inicio" en cada tablero para volver

#### Dashboard de Ventas (`/ventas`)
- **Mapa de Burbujas**: Visualizacion de clientes con tamano segun metrica seleccionada
- **Mapa de Calor**: Dos modos (difuso y grilla) con escala logaritmica opcional
- **Mapa Compro/No Compro**: Verde (compraron) vs Rojo (no compraron)
- **Zonas Territoriales**: Convex hull por ruta y preventista con filtrado de outliers (IQR)
- **Animacion Temporal**: Evolucion de ventas por dia/semana/mes
- **KPIs en tiempo real**: Clientes, Bultos, Facturacion, Documentos
- **Tablero de Comparacion Anual**: Grafico de lineas y tabla comparativa por mes/ano

#### Dashboard YTD (`/ytd`)
- KPIs: Ventas, Objetivo, Cumplimiento %, Ano Anterior, Ganancia Bruta (placeholder)
- Grafico de barras por Generico con targets
- Grafico mensual Real vs Objetivo con colores semaforo
- Grafico horizontal por Sucursal
- Grafico de dona por Canal
- Grafico de Crecimiento interanual por mes
- Gauge de Dias de Inventario

#### Filtros
- Rango de fechas
- Canal, Subcanal, Localidad
- Lista de Precio, Sucursal
- Tipo Sucursal (Todas / Solo Sucursales / Solo Casa Central)
- Generico y Marca (filtro en cascada)
- Fuerza de Venta (FV1 / FV4 / Todos)
- Ruta y Preventista (dependientes de FV)
- Metrica (Bultos / Facturacion / Documentos)

#### Opciones de Visualizacion
- Escala logaritmica para mapas de calor
- Tamano de celda configurable (grilla)
- Radio difuso configurable
- Normalizacion: Normal / Percentil / Limitado (p95)

### Corregido
- Consistencia de datos entre KPIs y tablas (queries parten de `fact_ventas` con LEFT JOIN)
- Clientes sin coordenadas se excluyen solo de visualizacion, no de calculos

### Tecnico
- Arquitectura: Dash/Plotly + PostgreSQL (medallion ETL)
- Esquema de datos: gold.fact_ventas, gold.dim_cliente, gold.dim_articulo
- Conexion via SQLAlchemy con variables de entorno
- Servidor Flask exportado para gunicorn

---

## Convencion de Versiones

```
v[MAJOR].[MINOR].[PATCH]

MAJOR = Cambio grande (nuevo tablero, reestructura)
MINOR = Nueva funcionalidad
PATCH = Bugfix
```

## Tipos de cambios

- **Agregado** para nuevas funcionalidades
- **Cambiado** para cambios en funcionalidades existentes
- **Obsoleto** para funcionalidades que seran removidas
- **Removido** para funcionalidades removidas
- **Corregido** para bugfixes
- **Seguridad** para vulnerabilidades
