# Roadmap - Sales Dashboard

Plan de desarrollo por versiones.

---

## Vista General

```
v1.0 ──► v1.1 ──► v1.2 ──► v2.0 ──► v2.1 ──► v3.0
 │        │        │        │        │        │
 │        │        │        │        │        └─ Market Intelligence
 │        │        │        │        └─ Optimización de Rutas
 │        │        │        └─ Tablero Inteligencia Territorial
 │        │        └─ Analytics (Clustering, Anomalías)
 │        └─ Quick Wins (Oportunidades, Eficiencia)
 └─ Base (Actual)
```

---

## v1.0.0 - Base ✅ COMPLETADA

**Estado:** En producción
**Fecha:** Enero 2026

### Features incluidas:
- [x] Dashboard de Ventas con 3 mapas
- [x] Dashboard YTD con KPIs y gráficos
- [x] Sistema de navegación multi-tablero
- [x] Filtros completos (fecha, cliente, producto, territorio)
- [x] Zonas por ruta/preventista (convex hull)
- [x] Animación temporal
- [x] Comparación anual (gráfico + tabla)

---

## v1.1.0 - Quick Wins 🎯 PRÓXIMA

**Estado:** Planificada
**Esfuerzo estimado:** 1-2 semanas
**Impacto:** Alto

### Features planificadas:

#### 1. Mapa de Oportunidades Perdidas
```
Descripción: Identificar clientes que NO compraron pero están
             rodeados de clientes que SÍ compraron.

Algoritmo:
- Para cada cliente sin compra, buscar K vecinos más cercanos
- Si >70% de vecinos compraron → es "oportunidad perdida"
- Mostrar con marcador especial (rojo pulsante)

Archivos a crear/modificar:
- analytics/opportunities.py (nuevo)
- callbacks/callbacks.py (agregar trace)
- layouts/main_layout.py (toggle para activar)
```

#### 2. Métricas de Eficiencia en Zonas
```
Descripción: Enriquecer tooltips de zonas con métricas de rendimiento.

Métricas a mostrar:
- Venta total de la zona
- Venta promedio por cliente
- % cobertura (activos/total)
- Comparación vs promedio empresa
- Tendencia vs período anterior

Archivos a modificar:
- utils/visualization.py (calcular métricas)
- callbacks/callbacks.py (enriquecer hover)
```

#### 3. Mejoras Visuales Menores
```
- Leyenda más clara en mapas
- Colores más intuitivos (verde=bueno, rojo=atención)
- Loading states mejorados
```

---

## v1.2.0 - Analytics

**Estado:** Planificada
**Esfuerzo estimado:** 3-4 semanas
**Impacto:** Alto

### Features planificadas:

#### 1. Clustering de Puntos (DBSCAN)
```
Descripción: Agrupar clientes cercanos para evitar superposición
             y revelar patrones de concentración.

Dependencias:
- scikit-learn

Archivos a crear:
- analytics/clustering.py

Visualización:
- Círculos agregados: "N clientes, X bultos"
- Click para expandir cluster
```

#### 2. Detección de Anomalías Espaciales
```
Descripción: Identificar clientes con rendimiento inusual
             comparado con sus vecinos geográficos.

Tipos de anomalías:
- Super performers (venta >> vecinos)
- Bajo rendimiento (venta << vecinos)

Archivos a crear:
- analytics/anomalies.py

Visualización:
- Borde dorado: super performer
- Borde negro: alerta bajo rendimiento
```

#### 3. Panel de Alertas Básico
```
Descripción: Sección que muestra alertas automáticas.

Alertas iniciales:
- Clientes sin compra en zona caliente
- Zonas con caída >20% vs período anterior
- Rutas con baja cobertura

Archivos a crear:
- components/alerts_panel.py
```

---

## v2.0.0 - Inteligencia Territorial

**Estado:** Planificada
**Esfuerzo estimado:** 4-6 semanas
**Impacto:** Muy Alto

### Features planificadas:

#### 1. Nuevo Tablero Completo
```
Ruta: /territorial

Componentes:
┌─────────────────────────────────────────────────────┐
│  INTELIGENCIA TERRITORIAL                           │
├─────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌─────────────────────────────┐ │
│  │ MAPA PRINCIPAL│  │ RANKING DE TERRITORIOS      │ │
│  │               │  │ 1. Ruta 15: 98% efic. ↑     │ │
│  │               │  │ 2. Ruta 23: 94% efic. →     │ │
│  └───────────────┘  └─────────────────────────────┘ │
│  ┌───────────────┐  ┌─────────────────────────────┐ │
│  │    ALERTAS    │  │    RECOMENDACIONES          │ │
│  └───────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

#### 2. Ranking de Territorios
```
Tabla ordenable con:
- Nombre de ruta/preventista
- Venta total
- % cumplimiento objetivo
- Eficiencia (venta/cliente)
- Tendencia (↑↓→)
- Cobertura (%)
```

#### 3. Sistema de Alertas Avanzado
```
Categorías:
- Oportunidades (verde)
- Atención (amarillo)
- Crítico (rojo)

Acciones:
- Click → ver en mapa
- Exportar lista
- Marcar como atendida
```

---

## v2.1.0 - Optimización

**Estado:** Planificada
**Esfuerzo estimado:** 4-6 semanas
**Impacto:** Alto

### Features planificadas:

#### 1. Optimización de Rutas (TSP)
```
Descripción: Calcular ruta óptima para cada preventista.

Dependencias:
- ortools (Google OR-Tools)

Visualización:
- Línea conectando clientes en orden óptimo
- Comparación km actuales vs óptimos
- Ahorro estimado

Archivos a crear:
- analytics/route_optimizer.py
```

#### 2. Análisis de Canibalización
```
Descripción: Detectar clientes muy cercanos del mismo canal
             que podrían estar compitiendo entre sí.

Visualización:
- Líneas rojas conectando pares
- Métrica de "densidad competitiva"
```

#### 3. Métricas de Eficiencia de Rutas
```
KPIs por ruta:
- Km totales recorridos (estimado)
- Km óptimos
- % ineficiencia
- Clientes por km
- Tiempo estimado de recorrido
```

---

## v3.0.0 - Market Intelligence

**Estado:** Planificada
**Esfuerzo estimado:** 2-3 meses
**Impacto:** Muy Alto

### Features planificadas:

#### 1. Integración de Datos Externos
```
Fuentes:
- Datos censales INDEC (población por radio censal)
- OpenStreetMap (puntos de interés)
- Catastro comercial (opcional)

Archivos a crear:
- data/external/census_data.py
- data/external/osm_data.py
```

#### 2. Análisis de Potencial de Mercado
```
Descripción: Comparar venta real vs potencial estimado.

Índice de Penetración:
= (Venta_zona / Población_zona) / (Venta_total / Población_total)

Visualización:
- Mapa de calor de potencial
- Zonas subatendidas destacadas
```

#### 3. Recomendaciones con ML
```
Modelos:
- Predicción de venta por zona
- Segmentación de clientes
- Propensión a compra

Dependencias:
- scikit-learn
- (opcional) tensorflow/pytorch
```

---

## Backlog (Sin versión asignada)

Ideas para evaluar en el futuro:

- [ ] Dashboard móvil (responsive)
- [ ] Exportación de reportes PDF
- [ ] Integración con sistema de pedidos
- [ ] Notificaciones push a preventistas
- [ ] API REST para integraciones
- [ ] Multi-idioma
- [ ] Temas claro/oscuro
- [ ] Modo offline (PWA)

---

## Gestión de Bugs

Los bugs se corrigen en la versión actual y se publican como PATCH:

```
v1.0.0 → v1.0.1 (bugfix)
v2.0.0 → v2.0.1 (bugfix)
```

No se mantienen múltiples versiones en paralelo.
Solo existe una versión en producción a la vez.

---

## Contribución

Para proponer nuevas features:
1. Documentar en este archivo (sección Backlog)
2. Evaluar esfuerzo e impacto
3. Asignar a versión según prioridad

---

*Última actualización: Enero 2026*
