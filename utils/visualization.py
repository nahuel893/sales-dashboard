"""
Utilidades de visualización.
Funciones para crear elementos visuales del mapa (grillas, zonas, etc).
"""
import numpy as np
from config import SCIPY_AVAILABLE

if SCIPY_AVAILABLE:
    from scipy.spatial import ConvexHull


# Colores predefinidos para los 8 grupos (frío a calor)
COLORES_CALOR = [
    'rgba(0, 50, 150, 0.6)',      # Azul oscuro
    'rgba(0, 100, 255, 0.6)',     # Azul
    'rgba(0, 200, 255, 0.6)',     # Celeste
    'rgba(0, 255, 150, 0.6)',     # Verde claro
    'rgba(200, 255, 0, 0.6)',     # Amarillo-verde
    'rgba(255, 200, 0, 0.6)',     # Amarillo-naranja
    'rgba(255, 100, 0, 0.6)',     # Naranja
    'rgba(200, 0, 0, 0.7)',       # Rojo
]

# Colores para zonas (12 colores base)
COLORES_ZONAS = [
    ('rgba(255, 0, 0, 0.2)', 'rgba(255, 0, 0, 0.8)'),
    ('rgba(0, 255, 0, 0.2)', 'rgba(0, 255, 0, 0.8)'),
    ('rgba(0, 0, 255, 0.2)', 'rgba(0, 0, 255, 0.8)'),
    ('rgba(255, 255, 0, 0.2)', 'rgba(255, 255, 0, 0.8)'),
    ('rgba(255, 0, 255, 0.2)', 'rgba(255, 0, 255, 0.8)'),
    ('rgba(0, 255, 255, 0.2)', 'rgba(0, 255, 255, 0.8)'),
    ('rgba(255, 128, 0, 0.2)', 'rgba(255, 128, 0, 0.8)'),
    ('rgba(128, 0, 255, 0.2)', 'rgba(128, 0, 255, 0.8)'),
    ('rgba(0, 128, 255, 0.2)', 'rgba(0, 128, 255, 0.8)'),
    ('rgba(255, 0, 128, 0.2)', 'rgba(255, 0, 128, 0.8)'),
    ('rgba(128, 255, 0, 0.2)', 'rgba(128, 255, 0, 0.8)'),
    ('rgba(0, 255, 128, 0.2)', 'rgba(0, 255, 128, 0.8)'),
]


def _filtrar_outliers_iqr(puntos):
    """
    Filtra outliers usando el metodo IQR (rango intercuartilico).
    Calcula la distancia de cada punto al centroide y elimina
    los que estan fuera de 1.5*IQR.

    Args:
        puntos: numpy array de shape (n, 2) con [longitud, latitud]

    Returns:
        numpy array con los puntos sin outliers
    """
    if len(puntos) < 4:
        return puntos

    # Calcular centroide
    centroide = puntos.mean(axis=0)

    # Calcular distancias al centroide
    distancias = np.sqrt(np.sum((puntos - centroide) ** 2, axis=1))

    # Calcular IQR
    q1 = np.percentile(distancias, 25)
    q3 = np.percentile(distancias, 75)
    iqr = q3 - q1

    # Definir limites (1.5 * IQR es el estandar)
    limite_superior = q3 + 1.5 * iqr

    # Filtrar puntos dentro del limite
    mascara = distancias <= limite_superior
    puntos_filtrados = puntos[mascara]

    # Si quedaron muy pocos puntos, devolver los originales
    if len(puntos_filtrados) < 3:
        return puntos

    return puntos_filtrados


def _calcular_hull_seguro(puntos):
    """
    Calcula el convex hull de forma segura.
    Retorna None si no es posible calcular.
    """
    if len(puntos) < 3:
        return None

    try:
        hull = ConvexHull(puntos)
        hull_puntos = puntos[hull.vertices]
        # Cerrar el poligono
        hull_puntos = np.vstack([hull_puntos, hull_puntos[0]])
        return hull_puntos
    except Exception:
        return None


def crear_grilla_calor_optimizada(df, metrica, precision=2, usar_log=True, n_grupos=8):
    """
    Crea una grilla de cuadrados agrupados por color para mejor rendimiento.
    Retorna grupos de celdas (un trace por grupo de color).
    """
    if len(df) == 0:
        return {}

    # Redondear coordenadas para crear celdas (vectorizado)
    factor = 10 ** precision
    df = df.copy()
    df['lat_grid'] = (df['latitud'] * factor).round() / factor
    df['lon_grid'] = (df['longitud'] * factor).round() / factor

    # Agregar por celda
    df_grid = df.groupby(['lat_grid', 'lon_grid']).agg({
        metrica: 'sum',
        'id_cliente': 'count'
    }).reset_index()
    df_grid.columns = ['lat', 'lon', 'valor', 'n_clientes']

    # Aplicar escala logarítmica si corresponde
    if usar_log:
        df_grid['valor_color'] = np.log1p(df_grid['valor'])
    else:
        df_grid['valor_color'] = df_grid['valor']

    # Normalizar valores para color (0-1)
    val_min = df_grid['valor_color'].min()
    val_max = df_grid['valor_color'].max()
    if val_max > val_min:
        df_grid['valor_norm'] = (df_grid['valor_color'] - val_min) / (val_max - val_min)
    else:
        df_grid['valor_norm'] = 0.5

    # Asignar grupo de color (0 a n_grupos-1)
    df_grid['grupo'] = (df_grid['valor_norm'] * (n_grupos - 0.001)).astype(int)

    # Tamaño de celda en grados
    cell_size = 10 ** -precision
    half = cell_size / 2

    # Agrupar celdas por color - cada grupo será un solo trace
    grupos = {}
    for grupo_id in range(n_grupos):
        grupo_df = df_grid[df_grid['grupo'] == grupo_id]
        if len(grupo_df) == 0:
            continue

        # Combinar todos los polígonos del grupo en arrays con None como separador
        all_lats = []
        all_lons = []
        total_valor = 0
        total_clientes = 0

        for _, row in grupo_df.iterrows():
            lat, lon = row['lat'], row['lon']
            # Coordenadas del cuadrado + None para separar
            all_lats.extend([lat - half, lat - half, lat + half, lat + half, lat - half, None])
            all_lons.extend([lon - half, lon + half, lon + half, lon - half, lon - half, None])
            total_valor += row['valor']
            total_clientes += row['n_clientes']

        grupos[grupo_id] = {
            'lats': all_lats,
            'lons': all_lons,
            'n_celdas': len(grupo_df),
            'total_valor': total_valor,
            'total_clientes': total_clientes
        }

    return grupos


def calcular_zonas(df, columna_grupo):
    """
    Calcula poligonos (convex hull) para cada grupo, filtrando outliers.

    - Para 'ruta': Calcula una zona por cada ruta, filtrando outliers
    - Para 'preventista': Calcula zonas separadas para cada ruta del preventista

    Args:
        df: DataFrame con columnas 'latitud', 'longitud', 'ruta', 'preventista'
        columna_grupo: 'ruta' o 'preventista'

    Returns:
        Lista de diccionarios con: nombre, color, color_borde, lats, lons, n_clientes
    """
    if not SCIPY_AVAILABLE:
        return []

    zonas = []
    color_idx = 0

    if columna_grupo == 'preventista':
        # Para preventistas: mostrar cada ruta del preventista como zona separada
        zonas = _calcular_zonas_preventista(df)
    else:
        # Para rutas: una zona por ruta, filtrando outliers
        zonas = _calcular_zonas_ruta(df)

    return zonas


def _calcular_zonas_ruta(df):
    """
    Calcula zonas agrupando por ruta, filtrando outliers.

    Jerarquia: Sucursal -> Preventista -> Ruta -> Cliente

    Crea identificador unico: sucursal + ruta
    para evitar mezclar rutas con mismo numero de diferentes sucursales.
    """
    zonas = []
    color_idx = 0

    # Filtrar rutas validas
    df_valido = df[~df['ruta'].isin(['Sin ruta', ''])].copy()
    if len(df_valido) == 0:
        return zonas

    # Crear identificador unico: sucursal|ruta
    df_valido['ruta_unica'] = df_valido['sucursal'].fillna('') + '|' + df_valido['ruta'].fillna('')

    # Agrupar por identificador unico
    grupos = df_valido.groupby('ruta_unica')

    for ruta_unica, grupo in grupos:
        puntos = grupo[['longitud', 'latitud']].values

        if len(puntos) < 3:
            continue

        # Filtrar outliers
        puntos_filtrados = _filtrar_outliers_iqr(puntos)

        # Calcular convex hull
        hull_puntos = _calcular_hull_seguro(puntos_filtrados)
        if hull_puntos is None:
            continue

        # Obtener nombre de ruta y sucursal del grupo
        ruta = grupo['ruta'].iloc[0]
        sucursal = grupo['sucursal'].iloc[0]

        # Nombre descriptivo
        nombre = f"{ruta} ({sucursal})" if sucursal and sucursal != 'Sin sucursal' else str(ruta)

        color, color_borde = COLORES_ZONAS[color_idx % len(COLORES_ZONAS)]
        zonas.append({
            'nombre': nombre,
            'color': color,
            'color_borde': color_borde,
            'lons': hull_puntos[:, 0].tolist(),
            'lats': hull_puntos[:, 1].tolist(),
            'n_clientes': len(grupo),
            'n_clientes_zona': len(puntos_filtrados),
            'clientes': grupo['id_cliente'].tolist(),
        })
        color_idx += 1

    return zonas


def _calcular_zonas_preventista(df):
    """
    Calcula zonas para preventistas mostrando cada ruta como zona independiente.

    Jerarquia: Sucursal -> Preventista -> Ruta -> Cliente

    Crea identificador unico de ruta: sucursal + ruta
    para evitar mezclar rutas con mismo numero de diferentes sucursales.
    """
    zonas = []
    color_idx = 0

    # Filtrar preventistas validos
    df_valido = df[~df['preventista'].isin(['Sin preventista', ''])].copy()
    if len(df_valido) == 0:
        return zonas

    # Crear identificador unico de ruta (sucursal + ruta)
    df_valido['ruta_unica'] = df_valido['sucursal'].fillna('') + '|' + df_valido['ruta'].fillna('')

    # Filtrar rutas validas
    df_valido = df_valido[~df_valido['ruta'].isin(['Sin ruta', ''])]
    if len(df_valido) == 0:
        return zonas

    # Agrupar por preventista Y sucursal (un preventista es unico por sucursal)
    preventistas = df_valido.groupby(['preventista', 'sucursal'])

    for (preventista_nombre, sucursal_prev), grupo_preventista in preventistas:
        # Agrupar por ruta_unica (garantiza que no se mezclen rutas de otras sucursales)
        rutas = grupo_preventista.groupby('ruta_unica')

        # Color base para este preventista
        color_base, color_borde_base = COLORES_ZONAS[color_idx % len(COLORES_ZONAS)]

        ruta_num = 0
        for ruta_unica, grupo_ruta in rutas:
            puntos = grupo_ruta[['longitud', 'latitud']].values

            if len(puntos) < 3:
                continue

            # Filtrar outliers
            puntos_filtrados = _filtrar_outliers_iqr(puntos)

            # Calcular convex hull
            hull_puntos = _calcular_hull_seguro(puntos_filtrados)
            if hull_puntos is None:
                continue

            # Variar la opacidad para distinguir rutas del mismo preventista
            opacidad_fill = 0.15 + (ruta_num * 0.05)
            opacidad_borde = 0.7 + (ruta_num * 0.1)
            opacidad_fill = min(opacidad_fill, 0.4)
            opacidad_borde = min(opacidad_borde, 1.0)

            # Modificar colores con nueva opacidad
            color = color_base.replace('0.2', str(opacidad_fill))
            color_borde = color_borde_base.replace('0.8', str(opacidad_borde))

            # Obtener nombre de ruta (sin el prefijo de sucursal)
            ruta_nombre = grupo_ruta['ruta'].iloc[0]

            # Nombre descriptivo: Preventista (Sucursal) - Ruta
            if sucursal_prev and sucursal_prev != 'Sin sucursal':
                nombre_zona = f"{preventista_nombre} ({sucursal_prev}) - {ruta_nombre}"
            else:
                nombre_zona = f"{preventista_nombre} - {ruta_nombre}"

            zonas.append({
                'nombre': nombre_zona,
                'color': color,
                'color_borde': color_borde,
                'lons': hull_puntos[:, 0].tolist(),
                'lats': hull_puntos[:, 1].tolist(),
                'n_clientes': len(grupo_ruta),
                'n_clientes_zona': len(puntos_filtrados),
                'clientes': grupo_ruta['id_cliente'].tolist(),
            })
            ruta_num += 1

        color_idx += 1

    return zonas
