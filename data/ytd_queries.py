"""
Queries específicas para el YTD Dashboard.
Incluye cálculos de targets automáticos, comparación año anterior, y métricas de inventario.
"""
import pandas as pd
from datetime import date
from database import engine


def obtener_ventas_ytd(anio, mes_hasta, tipo_sucursal='TODAS'):
    """
    Obtiene ventas acumuladas Year-To-Date hasta el mes indicado.

    Args:
        anio: Año a consultar
        mes_hasta: Mes hasta el cual acumular (1-12)
        tipo_sucursal: 'TODAS', 'SUCURSALES', 'CASA_CENTRAL'

    Returns:
        DataFrame con ventas totales YTD
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    query = f"""
        SELECT
            SUM(f.cantidades_total) as bultos,
            SUM(f.subtotal_final) as facturacion,
            COUNT(DISTINCT f.nro_doc) as documentos,
            COUNT(DISTINCT f.id_cliente) as clientes
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        WHEREEXTRACT(YEAR FROM f.fecha_comprobante) = {anio}
          AND EXTRACT(MONTH FROM f.fecha_comprobante) <= {mes_hasta}
          {filtro_sucursal}
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def obtener_ventas_por_mes(anio, mes_hasta, tipo_sucursal='TODAS'):
    """
    Obtiene ventas desglosadas por mes para el año indicado.
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    query = f"""
        SELECT
            EXTRACT(MONTH FROM f.fecha_comprobante)::int as mes,
            SUM(f.cantidades_total) as bultos,
            SUM(f.subtotal_final) as facturacion
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        WHEREEXTRACT(YEAR FROM f.fecha_comprobante) = {anio}
          AND EXTRACT(MONTH FROM f.fecha_comprobante) <= {mes_hasta}
          {filtro_sucursal}
        GROUP BY EXTRACT(MONTH FROM f.fecha_comprobante)
        ORDER BY mes
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def obtener_ventas_por_generico(anio, mes_hasta, top_n=5, tipo_sucursal='TODAS'):
    """
    Obtiene ventas por genérico (categoría de producto).
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    query = f"""
        SELECT
            COALESCE(a.generico, 'Sin categoría') as generico,
            SUM(f.cantidades_total) as bultos,
            SUM(f.subtotal_final) as facturacion
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo
        WHEREEXTRACT(YEAR FROM f.fecha_comprobante) = {anio}
          AND EXTRACT(MONTH FROM f.fecha_comprobante) <= {mes_hasta}
          {filtro_sucursal}
        GROUP BY a.generico
        ORDER BY bultos DESC
        LIMIT {top_n}
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def obtener_ventas_por_sucursal(anio, mes_hasta, tipo_sucursal='TODAS'):
    """
    Obtiene ventas por sucursal (región).
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    query = f"""
        SELECT
            COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal,
            SUM(f.cantidades_total) as bultos,
            SUM(f.subtotal_final) as facturacion
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        WHEREEXTRACT(YEAR FROM f.fecha_comprobante) = {anio}
          AND EXTRACT(MONTH FROM f.fecha_comprobante) <= {mes_hasta}
          {filtro_sucursal}
        GROUP BY c.des_sucursal
        ORDER BY bultos DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def obtener_ventas_por_canal(anio, mes_hasta, tipo_sucursal='TODAS'):
    """
    Obtiene ventas por canal.
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    query = f"""
        SELECT
            COALESCE(c.des_canal_mkt, 'Sin canal') as canal,
            SUM(f.cantidades_total) as bultos,
            SUM(f.subtotal_final) as facturacion
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        WHEREEXTRACT(YEAR FROM f.fecha_comprobante) = {anio}
          AND EXTRACT(MONTH FROM f.fecha_comprobante) <= {mes_hasta}
          {filtro_sucursal}
        GROUP BY c.des_canal_mkt
        ORDER BY bultos DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def calcular_target_automatico(anio, mes_hasta, incremento_pct=10, tipo_sucursal='TODAS'):
    """
    Calcula target automático basado en el año anterior + incremento porcentual.

    Args:
        anio: Año actual
        mes_hasta: Mes hasta el cual calcular
        incremento_pct: Porcentaje de incremento sobre año anterior (default 10%)
        tipo_sucursal: Filtro de tipo de sucursal

    Returns:
        dict con target total y por mes
    """
    anio_anterior = anio - 1

    # Ventas del año anterior
    df_anterior = obtener_ventas_ytd(anio_anterior, mes_hasta, tipo_sucursal)
    ventas_anterior = df_anterior['bultos'].iloc[0] if len(df_anterior) > 0 else 0

    # Target = año anterior * (1 + incremento)
    target_total = ventas_anterior * (1 + incremento_pct / 100) if ventas_anterior else 0

    # Ventas por mes del año anterior para targets mensuales
    df_meses_anterior = obtener_ventas_por_mes(anio_anterior, mes_hasta, tipo_sucursal)

    targets_por_mes = {}
    for _, row in df_meses_anterior.iterrows():
        targets_por_mes[int(row['mes'])] = row['bultos'] * (1 + incremento_pct / 100)

    return {
        'target_total': target_total,
        'ventas_anio_anterior': ventas_anterior,
        'targets_por_mes': targets_por_mes
    }


def calcular_targets_por_generico(anio, mes_hasta, incremento_pct=10, top_n=5, tipo_sucursal='TODAS'):
    """
    Calcula targets por genérico basado en año anterior.
    """
    anio_anterior = anio - 1
    df_anterior = obtener_ventas_por_generico(anio_anterior, mes_hasta, top_n, tipo_sucursal)

    targets = {}
    for _, row in df_anterior.iterrows():
        targets[row['generico']] = row['bultos'] * (1 + incremento_pct / 100)

    return targets


def calcular_targets_por_sucursal(anio, mes_hasta, incremento_pct=10, tipo_sucursal='TODAS'):
    """
    Calcula targets por sucursal basado en año anterior.
    """
    anio_anterior = anio - 1
    df_anterior = obtener_ventas_por_sucursal(anio_anterior, mes_hasta, tipo_sucursal)

    targets = {}
    for _, row in df_anterior.iterrows():
        targets[row['sucursal']] = row['bultos'] * (1 + incremento_pct / 100)

    return targets


def calcular_crecimiento_mensual(anio, mes_hasta, tipo_sucursal='TODAS'):
    """
    Calcula el crecimiento porcentual mes a mes vs año anterior.
    """
    anio_anterior = anio - 1

    df_actual = obtener_ventas_por_mes(anio, mes_hasta, tipo_sucursal)
    df_anterior = obtener_ventas_por_mes(anio_anterior, mes_hasta, tipo_sucursal)

    # Crear diccionario del año anterior
    ventas_anterior = {int(row['mes']): row['bultos'] for _, row in df_anterior.iterrows()}

    # Calcular crecimiento
    crecimiento = []
    for _, row in df_actual.iterrows():
        mes = int(row['mes'])
        actual = row['bultos']
        anterior = ventas_anterior.get(mes, 0)

        if anterior > 0:
            pct = ((actual - anterior) / anterior) * 100
        else:
            pct = 100 if actual > 0 else 0

        crecimiento.append({
            'mes': mes,
            'bultos_actual': actual,
            'bultos_anterior': anterior,
            'crecimiento_pct': pct
        })

    return pd.DataFrame(crecimiento)


def obtener_dias_inventario(tipo_sucursal='TODAS'):
    """
    Calcula los días de inventario basado en stock actual y promedio de ventas diarias.

    Fórmula: días_inventario = stock_actual / promedio_venta_diaria
    """
    filtro_sucursal = ""
    if tipo_sucursal == 'SUCURSALES':
        filtro_sucursal = "AND c.des_sucursal != 'CASA CENTRAL' AND c.des_sucursal LIKE 'SUCURSAL%'"
    elif tipo_sucursal == 'CASA_CENTRAL':
        filtro_sucursal = "AND c.des_sucursal = 'CASA CENTRAL'"

    # Obtener stock actual (asumiendo que fact_stock tiene el stock más reciente)
    query_stock = f"""
        SELECT COALESCE(SUM(stock), 0) as stock_total
        FROM gold.fact_stock
    """

    # Obtener promedio de ventas diarias de los últimos 30 días
    query_ventas = f"""
        SELECT
            COALESCE(SUM(f.cantidades_total), 0) as ventas_total,
            COUNT(DISTINCT f.fecha_comprobante) as dias_con_ventas
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        WHEREf.fecha_comprobante >= CURRENT_DATE - INTERVAL '30 days'
          {filtro_sucursal}
    """

    try:
        with engine.connect() as conn:
            df_stock = pd.read_sql(query_stock, conn)
            df_ventas = pd.read_sql(query_ventas, conn)

        stock_total = df_stock['stock_total'].iloc[0] if len(df_stock) > 0 else 0
        ventas_total = df_ventas['ventas_total'].iloc[0] if len(df_ventas) > 0 else 0
        dias_con_ventas = df_ventas['dias_con_ventas'].iloc[0] if len(df_ventas) > 0 else 30

        # Promedio diario
        promedio_diario = ventas_total / dias_con_ventas if dias_con_ventas > 0 else 0

        # Días de inventario
        dias_inventario = stock_total / promedio_diario if promedio_diario > 0 else 0

        return {
            'dias_inventario': round(dias_inventario, 0),
            'stock_total': stock_total,
            'promedio_diario': promedio_diario
        }
    except Exception as e:
        # Si hay error, devolver valores placeholder
        return {
            'dias_inventario': 0,
            'stock_total': 0,
            'promedio_diario': 0,
            'error': str(e)
        }


def obtener_anios_disponibles_ytd():
    """
    Obtiene los años disponibles en fact_ventas para el selector YTD.
    """
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM fecha_comprobante)::int as anio
        FROM gold.fact_ventas
        ORDER BY anio DESC
    """

    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df['anio'].tolist()
    except Exception:
        # Si hay error, devolver años por defecto
        current_year = date.today().year
        return [current_year, current_year - 1]


def obtener_mes_actual():
    """Retorna el mes actual."""
    return date.today().month


def obtener_anio_actual():
    """Retorna el año actual."""
    return date.today().year
