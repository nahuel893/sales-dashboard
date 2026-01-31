# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] - 2026-01-17

### Agregado

#### Sistema de Navegación
- Página de inicio con cards de navegación entre tableros
- Sistema de routing basado en URL (`/`, `/ventas`, `/ytd`)
- Botón "← Inicio" en cada tablero para volver

#### Dashboard de Ventas (`/ventas`)
- **Mapa de Burbujas**: Visualización de clientes con tamaño según métrica seleccionada
- **Mapa de Calor**: Dos modos (difuso y grilla) con escala logarítmica opcional
- **Mapa Compró/No Compró**: Verde (compraron) vs Rojo (no compraron)
- **Zonas Territoriales**: Convex hull por ruta y preventista con filtrado de outliers (IQR)
- **Animación Temporal**: Evolución de ventas por día/semana/mes
- **KPIs en tiempo real**: Clientes, Bultos, Facturación, Documentos
- **Tablero de Comparación Anual**: Gráfico de líneas y tabla comparativa por mes/año

#### Dashboard YTD (`/ytd`)
- KPIs: Ventas, Objetivo, Cumplimiento %, Año Anterior, Ganancia Bruta (placeholder)
- Gráfico de barras por Genérico con targets
- Gráfico mensual Real vs Objetivo con colores semáforo
- Gráfico horizontal por Sucursal
- Gráfico de dona por Canal
- Gráfico de Crecimiento interanual por mes
- Gauge de Días de Inventario
- Placeholder para Días de Cuentas por Cobrar

#### Filtros
- Rango de fechas
- Canal, Subcanal, Localidad
- Lista de Precio, Sucursal
- Tipo Sucursal (Todas / Solo Sucursales / Solo Casa Central)
- Genérico y Marca (filtro en cascada)
- Fuerza de Venta (FV1 / FV4 / Todos)
- Ruta y Preventista (dependientes de FV)
- Métrica (Bultos / Facturación / Documentos)

#### Opciones de Visualización
- Escala logarítmica para mapas de calor
- Tamaño de celda configurable (grilla)
- Radio difuso configurable
- Normalización: Normal / Percentil / Limitado (p95)

### Corregido
- Consistencia de datos entre KPIs y tablas (queries ahora parten de `fact_ventas` con LEFT JOIN)
- Clientes sin coordenadas se excluyen solo de visualización, no de cálculos

### Técnico
- Arquitectura: Dash/Plotly + PostgreSQL (medallion ETL)
- Esquema de datos: gold.fact_ventas, gold.dim_cliente, gold.dim_articulo
- Conexión via SQLAlchemy con variables de entorno

---

## [Unreleased]

### Por agregar en v1.1
- Mapa de oportunidades perdidas
- Métricas de eficiencia en zonas

---

## Convención de Versiones

```
v[MAJOR].[MINOR].[PATCH]

MAJOR = Cambio grande (nuevo tablero, reestructura)
MINOR = Nueva funcionalidad
PATCH = Bugfix
```

## Tipos de cambios

- **Agregado** para nuevas funcionalidades
- **Cambiado** para cambios en funcionalidades existentes
- **Obsoleto** para funcionalidades que serán removidas
- **Removido** para funcionalidades removidas
- **Corregido** para bugfixes
- **Seguridad** para vulnerabilidades
