"""
Configuración central del dashboard.
Constantes, estilos y configuración de la aplicación.
"""
from database import engine

# Verificar disponibilidad de scipy para zonas
try:
    from scipy.spatial import ConvexHull
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("scipy no instalado - zonas deshabilitadas")

# Configuración del servidor
SERVER_CONFIG = {
    'host': '127.0.0.1',
    'port': 8050,
    'debug': False
}

# Labels para métricas
METRICA_LABELS = {
    'cantidad_total': 'Cantidad (bultos)',
    'facturacion': 'Facturación ($)',
    'cantidad_documentos': 'Documentos'
}

# Escala de colores para mapas
COLOR_SCALE_BURBUJAS = [
    [0, 'rgb(70, 130, 180)'],
    [0.5, 'rgb(255, 165, 0)'],
    [1, 'rgb(220, 20, 20)']
]

COLOR_SCALE_CALOR = [
    [0.0, 'rgb(0, 0, 150)'],
    [0.15, 'rgb(0, 100, 255)'],
    [0.3, 'rgb(0, 200, 255)'],
    [0.45, 'rgb(0, 255, 150)'],
    [0.55, 'rgb(200, 255, 0)'],
    [0.7, 'rgb(255, 200, 0)'],
    [0.85, 'rgb(255, 100, 0)'],
    [1.0, 'rgb(200, 0, 0)']
]

# Colores para zonas
ZONE_COLORS = [
    'rgba(255, 99, 132, 0.3)',
    'rgba(54, 162, 235, 0.3)',
    'rgba(255, 206, 86, 0.3)',
    'rgba(75, 192, 192, 0.3)',
    'rgba(153, 102, 255, 0.3)',
    'rgba(255, 159, 64, 0.3)',
    'rgba(199, 199, 199, 0.3)',
    'rgba(83, 102, 255, 0.3)',
    'rgba(255, 99, 255, 0.3)',
    'rgba(99, 255, 132, 0.3)'
]

# Valores por defecto para filtros
DEFAULT_NULL_VALUES = {
    'canal': 'Sin canal',
    'segmento': 'Sin segmento',
    'subcanal': 'Sin subcanal',
    'ramo': 'Sin ramo',
    'lista_precio': 'Sin lista',
    'sucursal': 'Sin sucursal',
    'preventista_fv1': '',
    'preventista_fv4': ''
}

# Configuración de granularidad temporal
GRANULARIDAD_CONFIG = {
    'dia': ('day', '%Y-%m-%d'),
    'semana': ('week', '%Y-%m-%d'),
    'mes': ('month', '%Y-%m')
}

# Estilos comunes
STYLES = {
    'filter_section': {
        'padding': '8px 20px 15px 20px',
        'backgroundColor': '#f8f9fa'
    },
    'filter_label': {
        'fontWeight': 'bold',
        'marginBottom': '5px',
        'fontSize': '13px'
    },
    'map_height': '87vh'
}
