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

# Paleta de tema oscuro
DARK = {
    'bg': '#0f1117',
    'card': '#1a1a2e',
    'card_alt': '#16213e',
    'surface': '#252540',
    'border': '#2d2d44',
    'text': '#ffffff',
    'text_secondary': '#a0a0b0',
    'text_muted': '#6c6c7e',
    'header': '#1a1a2e',
    'accent_blue': '#3498db',
    'accent_green': '#27ae60',
    'accent_red': '#e74c3c',
    'accent_purple': '#9b59b6',
    'accent_orange': '#e67e22',
    'accent_yellow': '#f1c40f',
    'grid': '#2d2d44',
    'plot_bg': '#1a1a2e',
    'paper_bg': '#1a1a2e',
}

# Genéricos excluidos de filtros y hover
GENERICOS_EXCLUIDOS = [
    'ENVACES CCU', 'AGUAS Y SODAS', 'APERITIVOS', 'DISPENSER',
    'ENVASES PALAU', 'GASEOSA', 'MARKETING BRANCA', 'MARKETING',
]

# Genéricos que siempre aparecen en el hover del mapa (aunque tengan 0 ventas)
GENERICOS_HOVER_FIJOS = [
    'CERVEZAS', 'AGUAS DANONE', 'SIDRAS Y LICORES', 'VINOS CCU',
    'FRATELLI B', 'VINOS', 'VINOS FINOS',
]

# Estilos comunes
STYLES = {
    'filter_section': {
        'padding': '8px 20px 15px 20px',
        'backgroundColor': DARK['card']
    },
    'filter_label': {
        'fontWeight': 'bold',
        'marginBottom': '5px',
        'fontSize': '13px',
        'color': DARK['text_secondary']
    },
    'map_height': '87vh'
}
