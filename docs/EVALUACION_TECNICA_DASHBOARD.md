# EVALUACIÓN TÉCNICA DEL DASHBOARD DE VENTAS

**Fecha:** Enero 2026
**Autor:** Claude (Análisis como Científico de Datos)
**Proyecto:** Sales Dashboard - Medallion ETL

---

## 1. ANÁLISIS DE LO EXISTENTE

### Fortalezas actuales:
- Buena arquitectura de datos (medallion ETL: bronze → silver → gold)
- Separación correcta entre datos de visualización y cálculos
- Zonas con filtrado de outliers (IQR) - técnicamente sólido
- Escala logarítmica para métricas con alta varianza
- Animación temporal para ver evolución
- Sistema de filtros en cascada bien implementado

### Debilidades identificadas en los mapas:

| Problema | Impacto | Severidad |
|----------|---------|-----------|
| **Superposición de puntos** | En áreas densas no se distinguen clientes individuales | Alta |
| **Zonas solo muestran cobertura** | No indican rendimiento ni eficiencia del territorio | Media |
| **Sin análisis de oportunidades** | Clientes sin venta en zonas calientes pasan desapercibidos | Alta |
| **Sin métricas de densidad relativa** | No se compara venta real vs potencial de mercado | Alta |
| **Colores de mapa de calor** | El azul-rojo puede confundir (¿azul = frío = malo?) | Media |

---

## 2. PROPUESTAS DE MEJORA INMEDIATAS

### A) Mapa de Clustering Inteligente

Agrupar clientes cercanos automáticamente para evitar superposición:

```
Implementación: DBSCAN o clustering jerárquico espacial
Beneficio: Ver clusters naturales de clientes, identificar concentraciones
Visualización: Círculos agregados que muestran "N clientes, X bultos"
```

**Librerías sugeridas:**
- `sklearn.cluster.DBSCAN`
- `scipy.cluster.hierarchy`

### B) Mapa de "Oportunidades Perdidas"

Mostrar clientes que NO compraron pero están en zonas de alta actividad:

```
Lógica: Si vecinos compraron y este no → oportunidad
Visualización: Puntos rojos pulsantes en zonas verdes/calientes
Uso: Lista priorizada para que preventistas visiten
```

**Algoritmo sugerido:**
1. Para cada cliente sin compra, buscar K vecinos más cercanos
2. Calcular % de vecinos que SÍ compraron
3. Si % > 70% → cliente es "oportunidad perdida"
4. Ordenar por potencial (venta promedio de vecinos)

### C) Indicadores de Eficiencia Territorial

En las zonas de ruta/preventista, agregar métricas:

```
- Venta/cliente promedio vs empresa
- % de cobertura (clientes activos / clientes totales)
- Densidad: clientes por km²
- Tendencia: ↑↓ vs período anterior
```

**Visualización sugerida:**
- Tooltip enriquecido al pasar sobre zona
- Panel lateral con ranking de territorios
- Colores de zona según eficiencia (no solo identificación)

---

## 3. PROPUESTAS TÉCNICAS AVANZADAS

### D) Análisis de Canibalización

Detectar cuando clientes muy cercanos compiten entre sí:

```sql
-- Pseudocódigo
SELECT c1.id, c2.id, distancia(c1, c2)
FROM clientes c1, clientes c2
WHERE distancia < 500m AND mismo_canal
  AND ambos_compraron
-- Visualizar como líneas rojas conectando pares
```

**Uso:**
- Identificar si estamos saturando una zona
- Evaluar si podemos consolidar clientes
- Detectar posible canibalización de ventas

### E) Mapa de "Potencial de Mercado"

Cruzar con datos externos para evaluar penetración real:

```
Fuentes sugeridas:
- Datos censales (población por radio censal)
- Datos de INDEC de actividad comercial
- Catastro de comercios

Visualización: Overlay semitransparente mostrando:
  VERDE = zona con venta proporcional a población
  ROJO = zona subatendida (mucha población, poca venta)
  AZUL = zona sobre-atendida
```

**Fórmula de índice de penetración:**
```
Índice = (Venta_real / Población_zona) / (Venta_total / Población_total)
- Índice > 1.2 → Sobre-atendida
- Índice 0.8-1.2 → Equilibrada
- Índice < 0.8 → Subatendida (OPORTUNIDAD)
```

### F) Optimización de Rutas (TSP - Traveling Salesman Problem)

Calcular la ruta óptima para cada preventista:

```python
# Usando OR-Tools de Google
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def optimizar_ruta(coordenadas_clientes):
    """
    Input: lista de (lat, lon) de clientes de una ruta
    Output: orden óptimo de visitas minimizando distancia
    """
    # Crear matriz de distancias
    # Resolver TSP
    # Retornar orden óptimo
    pass
```

**Visualización:**
- Línea que conecta clientes en orden óptimo
- Comparación: distancia actual vs óptima
- Tiempo estimado de recorrido
- Ahorro potencial en km/combustible

**Métricas a mostrar:**
- Km actuales vs km óptimos
- % de ineficiencia
- Ahorro estimado mensual (combustible)

### G) Análisis de Difusión Temporal

Ver cómo se "propaga" la actividad comercial geográficamente:

```
Implementación:
1. Dividir período en frames temporales (semanas/meses)
2. Para cada frame, calcular centroide ponderado de ventas
3. Animar el movimiento del centroide
4. Calcular "radio de expansión" de la actividad

Preguntas que responde:
- ¿Las ventas se expanden desde centro hacia periferia?
- ¿Hay zonas que "despiertan" en ciertos meses?
- ¿Existe estacionalidad geográfica?
```

### H) Detección de Anomalías Espaciales

Identificar automáticamente outliers de rendimiento:

```python
from sklearn.neighbors import BallTree
import numpy as np

def detectar_anomalias_espaciales(df, k_vecinos=10):
    """
    Para cada cliente, comparar con sus K vecinos más cercanos.
    - Si venta >> promedio_vecinos → super performer
    - Si venta << promedio_vecinos → bajo rendimiento sospechoso
    """
    coords = df[['latitud', 'longitud']].values
    tree = BallTree(np.radians(coords), metric='haversine')

    for i, cliente in df.iterrows():
        # Buscar K vecinos
        dist, idx = tree.query([coords[i]], k=k_vecinos+1)
        vecinos = df.iloc[idx[0][1:]]  # Excluir el mismo cliente

        # Calcular z-score espacial
        promedio_vecinos = vecinos['cantidad_total'].mean()
        std_vecinos = vecinos['cantidad_total'].std()

        if std_vecinos > 0:
            z_score = (cliente['cantidad_total'] - promedio_vecinos) / std_vecinos
            # z_score > 2 → Super performer
            # z_score < -2 → Bajo rendimiento
```

**Visualización:**
- Círculos con borde dorado → super performers
- Círculos con borde negro → alertas de bajo rendimiento
- Lista exportable para seguimiento

---

## 4. DATOS ADICIONALES RECOMENDADOS

| Dato | Fuente | Uso |
|------|--------|-----|
| **Población por zona** | INDEC/Censo | Calcular penetración de mercado |
| **Comercios registrados** | AFIP/Catastro municipal | Cobertura real vs potencial |
| **Datos de competencia** | Market research / Nielsen | Participación de mercado |
| **Tiempos de visita** | App preventistas | Eficiencia de rutas |
| **Rechazos/sin stock** | Sistema de pedidos | Oportunidades perdidas por stockout |
| **Histórico de coordenadas GPS** | Tracking vehicular | Rutas reales vs asignadas |
| **Datos meteorológicos** | SMN | Correlación clima-ventas |
| **Calendario de eventos** | Manual/API | Impacto de eventos locales |

### Integración sugerida de datos externos:

```
1. INDEC - Censo Nacional
   - Radios censales con población
   - Nivel socioeconómico por zona
   - Densidad poblacional

2. OpenStreetMap
   - Puntos de interés (comercios)
   - Infraestructura vial
   - Límites de barrios/localidades

3. Google Places API (opcional)
   - Comercios por categoría
   - Horarios de apertura
   - Ratings/reviews
```

---

## 5. PROPUESTA DE NUEVO TABLERO: "INTELIGENCIA TERRITORIAL"

```
┌─────────────────────────────────────────────────────────────────┐
│  INTELIGENCIA TERRITORIAL                           [Filtros]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │   MAPA PRINCIPAL    │  │  RANKING DE TERRITORIOS         │  │
│  │   (Interactivo)     │  │  ┌───────────────────────────┐  │  │
│  │                     │  │  │ 1. Ruta 15: 98% efic. ↑   │  │  │
│  │   [Clusters]        │  │  │ 2. Ruta 23: 94% efic. →   │  │  │
│  │   [Oportunidades]   │  │  │ 3. Ruta 08: 87% efic. ↓   │  │  │
│  │   [Anomalías]       │  │  │ ...                       │  │  │
│  │                     │  │  └───────────────────────────┘  │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │ ALERTAS AUTOMÁTICAS │  │  RECOMENDACIONES IA             │  │
│  │ ⚠ 12 clientes sin   │  │  • Reasignar cliente X a ruta Y │  │
│  │   compra en zona    │  │  • Zona Norte subatendida       │  │
│  │   caliente          │  │  • Consolidar rutas 3 y 7       │  │
│  │ ⚠ Ruta 5 tiene 30%  │  │                                 │  │
│  │   más km que óptimo │  │                                 │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes del tablero:

1. **Mapa Principal Interactivo**
   - Toggle entre: Clusters / Oportunidades / Anomalías / Rutas
   - Click en zona → detalle en panel derecho
   - Filtros sincronizados con otros tableros

2. **Ranking de Territorios**
   - Ordenable por: eficiencia, venta, cobertura, tendencia
   - Código de colores: verde/amarillo/rojo
   - Click → zoom a territorio en mapa

3. **Alertas Automáticas**
   - Generadas por algoritmos de detección
   - Priorizadas por impacto potencial
   - Accionables (link a cliente/ruta)

4. **Recomendaciones IA**
   - Basadas en análisis de datos
   - Simulación de impacto
   - Histórico de recomendaciones aplicadas

---

## 6. PRIORIZACIÓN DE IMPLEMENTACIÓN

| Prioridad | Feature | Esfuerzo | Impacto | Dependencias |
|-----------|---------|----------|---------|--------------|
| 🔴 **Alta** | Mapa de oportunidades perdidas | Bajo | Alto | Ninguna |
| 🔴 **Alta** | Métricas de eficiencia en zonas | Bajo | Alto | Ninguna |
| 🟡 **Media** | Clustering de puntos | Medio | Medio | sklearn |
| 🟡 **Media** | Detección de anomalías | Medio | Alto | sklearn |
| 🟢 **Baja** | Optimización de rutas | Alto | Alto | ortools |
| 🟢 **Baja** | Análisis de potencial de mercado | Alto | Muy Alto | Datos externos |

### Roadmap sugerido:

```
Fase 1 (Inmediato - 1-2 semanas):
├── Mapa de oportunidades perdidas
├── Métricas de eficiencia en zonas
└── Mejora de tooltips con más info

Fase 2 (Corto plazo - 1 mes):
├── Clustering de puntos
├── Detección de anomalías espaciales
└── Panel de alertas automáticas

Fase 3 (Mediano plazo - 2-3 meses):
├── Optimización de rutas
├── Análisis de canibalización
└── Dashboard de Inteligencia Territorial

Fase 4 (Largo plazo - 3-6 meses):
├── Integración de datos externos (censo)
├── Análisis de potencial de mercado
└── Recomendaciones con IA/ML
```

---

## 7. CONSIDERACIONES TÉCNICAS

### Librerías adicionales necesarias:

```python
# Para clustering y anomalías
scikit-learn>=1.0.0

# Para optimización de rutas
ortools>=9.0

# Para cálculos geoespaciales avanzados
geopandas>=0.10.0
shapely>=2.0.0

# Para análisis de grafos (opcional)
networkx>=2.6
```

### Consideraciones de rendimiento:

1. **Clustering:** Pre-calcular en carga de datos, no en cada request
2. **Anomalías:** Calcular en batch, actualizar diariamente
3. **Rutas óptimas:** Cachear resultados, recalcular solo si cambian clientes
4. **Datos externos:** Cargar una vez, cruzar por código de zona

### Estructura de archivos sugerida:

```
sales-dashboard/
├── analytics/
│   ├── clustering.py      # Funciones de clustering espacial
│   ├── anomalies.py       # Detección de anomalías
│   ├── opportunities.py   # Análisis de oportunidades
│   └── route_optimizer.py # Optimización de rutas
├── data/
│   ├── external/          # Datos censales, etc.
│   └── cache/             # Resultados pre-calculados
└── layouts/
    └── territorial_layout.py  # Nuevo dashboard
```

---

## 8. MÉTRICAS DE ÉXITO

Para evaluar el impacto de las mejoras:

| Métrica | Baseline | Objetivo |
|---------|----------|----------|
| Clientes sin compra visitados | ? | +20% |
| Eficiencia de rutas (km/cliente) | ? | -15% |
| Tiempo de análisis territorial | Manual | Automático |
| Alertas accionadas | 0 | 80% |
| Precisión de recomendaciones | N/A | >70% |

---

*Documento generado como referencia para futuras implementaciones.*
