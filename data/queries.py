"""
Funciones de consulta a la base de datos.
Todas las queries SQL y carga de datos del dashboard.
"""
import pandas as pd
from database import engine


def obtener_genericos():
    """Obtiene lista de genericos disponibles."""
    query = """
        SELECT DISTINCT generico
        FROM gold.dim_articulo
        WHERE generico IS NOT NULL
        ORDER BY generico
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['generico'].tolist()


def obtener_marcas(genericos=None):
    """Obtiene lista de marcas disponibles, opcionalmente filtradas por genéricos."""
    if genericos and len(genericos) > 0:
        genericos_escaped = [g.replace("'", "''") for g in genericos]
        filtro_genericos = f"AND generico IN ('" + "','".join(genericos_escaped) + "')"
    else:
        filtro_genericos = ""

    query = f"""
        SELECT DISTINCT marca
        FROM gold.dim_articulo
        WHERE marca IS NOT NULL
        {filtro_genericos}
        ORDER BY marca
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['marca'].tolist()


def obtener_rutas(fuerza_venta=None):
    """Obtiene lista de rutas con clave compuesta (id_sucursal, id_ruta).
    Retorna lista de dicts con label y value para dmc.MultiSelect.
    Value es 'id_sucursal|id_ruta', label es 'id_ruta (sucursal)'."""
    if fuerza_venta == 'FV1':
        query = """
            SELECT DISTINCT c.id_sucursal, c.id_ruta_fv1 as id_ruta,
                   COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
            FROM gold.dim_cliente c
            WHERE c.id_ruta_fv1 IS NOT NULL
            ORDER BY sucursal, id_ruta
        """
    elif fuerza_venta == 'FV4':
        query = """
            SELECT DISTINCT c.id_sucursal, c.id_ruta_fv4 as id_ruta,
                   COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
            FROM gold.dim_cliente c
            WHERE c.id_ruta_fv4 IS NOT NULL
            ORDER BY sucursal, id_ruta
        """
    else:
        query = """
            SELECT DISTINCT c.id_sucursal, c.id_ruta_fv1 as id_ruta,
                   COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
            FROM gold.dim_cliente c WHERE c.id_ruta_fv1 IS NOT NULL
            UNION
            SELECT DISTINCT c.id_sucursal, c.id_ruta_fv4 as id_ruta,
                   COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
            FROM gold.dim_cliente c WHERE c.id_ruta_fv4 IS NOT NULL
            ORDER BY sucursal, id_ruta
        """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return [
        {"label": f"{row['id_ruta']} ({row['sucursal']})",
         "value": f"{row['id_sucursal']}|{row['id_ruta']}"}
        for _, row in df.iterrows()
    ]


def obtener_preventistas(fuerza_venta=None):
    """Obtiene lista de preventistas disponibles según la fuerza de venta seleccionada."""
    if fuerza_venta == 'FV1':
        query = """
            SELECT DISTINCT des_personal_fv1 as preventista
            FROM gold.dim_cliente
            WHERE des_personal_fv1 IS NOT NULL
            ORDER BY preventista
        """
    elif fuerza_venta == 'FV4':
        query = """
            SELECT DISTINCT des_personal_fv4 as preventista
            FROM gold.dim_cliente
            WHERE des_personal_fv4 IS NOT NULL
            ORDER BY preventista
        """
    else:
        query = """
            SELECT DISTINCT des_personal_fv1 as preventista FROM gold.dim_cliente WHERE des_personal_fv1 IS NOT NULL
            UNION
            SELECT DISTINCT des_personal_fv4 as preventista FROM gold.dim_cliente WHERE des_personal_fv4 IS NOT NULL
            ORDER BY preventista
        """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['preventista'].tolist()


def obtener_anios_disponibles():
    """Obtiene la lista de años disponibles en fact_ventas."""
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM fecha_comprobante)::INTEGER as anio
        FROM gold.fact_ventas
        ORDER BY anio
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['anio'].tolist()


def obtener_rango_fechas():
    """Obtiene el rango de fechas disponible en fact_ventas."""
    query = """
        SELECT MIN(fecha_comprobante) as min_fecha, MAX(fecha_comprobante) as max_fecha
        FROM gold.fact_ventas
    """
    with engine.connect() as conn:
        result = pd.read_sql(query, conn)
    return result['min_fecha'].iloc[0], result['max_fecha'].iloc[0]


def _build_articulo_filters(genericos, marcas):
    """Construye join y where para filtros de artículo."""
    join_articulo = ""
    where_articulo = []

    if genericos and len(genericos) > 0:
        join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        genericos_escaped = [g.replace("'", "''") for g in genericos]
        where_articulo.append(f"a.generico IN ('" + "','".join(genericos_escaped) + "')")

    if marcas and len(marcas) > 0:
        if not join_articulo:
            join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        marcas_escaped = [m.replace("'", "''") for m in marcas]
        where_articulo.append(f"a.marca IN ('" + "','".join(marcas_escaped) + "')")

    return join_articulo, where_articulo


def _parse_rutas_compuestas(rutas):
    """Parsea valores compuestos 'id_sucursal|id_ruta' a tuplas SQL."""
    parsed = []
    for r in rutas:
        parts = str(r).split('|')
        if len(parts) == 2:
            parsed.append((int(parts[0]), int(parts[1])))
    return parsed


def _build_ruta_where(rutas, fuerza_venta):
    """Construye WHERE para rutas con clave compuesta (id_sucursal, id_ruta)."""
    parsed = _parse_rutas_compuestas(rutas)
    if not parsed:
        return None
    tuples_sql = ", ".join([f"({suc}, {rta})" for suc, rta in parsed])
    if fuerza_venta == 'FV1':
        return f"(c.id_sucursal, c.id_ruta_fv1) IN ({tuples_sql})"
    elif fuerza_venta == 'FV4':
        return f"(c.id_sucursal, c.id_ruta_fv4) IN ({tuples_sql})"
    else:
        return f"((c.id_sucursal, c.id_ruta_fv1) IN ({tuples_sql}) OR (c.id_sucursal, c.id_ruta_fv4) IN ({tuples_sql}))"


def _build_cliente_filters(rutas, preventistas, fuerza_venta):
    """Construye where para filtros de cliente (ruta/preventista)."""
    where_cliente = []

    if rutas and len(rutas) > 0:
        ruta_where = _build_ruta_where(rutas, fuerza_venta)
        if ruta_where:
            where_cliente.append(ruta_where)

    if preventistas and len(preventistas) > 0:
        prev_escaped = [p.replace("'", "''") for p in preventistas]
        prev_list = "'" + "','".join(prev_escaped) + "'"
        if fuerza_venta == 'FV1':
            where_cliente.append(f"c.des_personal_fv1 IN ({prev_list})")
        elif fuerza_venta == 'FV4':
            where_cliente.append(f"c.des_personal_fv4 IN ({prev_list})")
        else:
            where_cliente.append(f"(c.des_personal_fv1 IN ({prev_list}) OR c.des_personal_fv4 IN ({prev_list}))")

    return where_cliente


def _process_ventas_df(df):
    """Procesa DataFrame de ventas: tipos y columnas derivadas."""
    df['latitud'] = df['latitud'].astype(float)
    df['longitud'] = df['longitud'].astype(float)
    df['cantidad_total'] = df['cantidad_total'].astype(float)
    df['facturacion'] = df['facturacion'].astype(float)

    df = df.fillna({
        'canal': 'Sin canal', 'segmento': 'Sin segmento',
        'subcanal': 'Sin subcanal', 'ramo': 'Sin ramo',
        'lista_precio': 'Sin lista', 'sucursal': 'Sin sucursal',
        'preventista_fv1': '', 'preventista_fv4': ''
    })

    df['ruta'] = df.apply(
        lambda r: f"FV1-{int(r['id_ruta_fv1'])}" if pd.notna(r['id_ruta_fv1'])
                  else (f"FV4-{int(r['id_ruta_fv4'])}" if pd.notna(r['id_ruta_fv4']) else 'Sin ruta'),
        axis=1
    )

    df['preventista'] = df.apply(
        lambda r: r['preventista_fv1'] if r['preventista_fv1']
                  else (r['preventista_fv4'] if r['preventista_fv4'] else 'Sin preventista'),
        axis=1
    )

    return df


def cargar_ventas_por_cliente(fecha_desde=None, fecha_hasta=None, genericos=None, marcas=None, rutas=None, preventistas=None, fuerza_venta=None):
    """Carga ventas agregadas por cliente partiendo de fact_ventas para incluir TODAS las ventas."""

    where_clauses = []

    if fecha_desde and fecha_hasta:
        where_clauses.append(f"f.fecha_comprobante BETWEEN '{fecha_desde}' AND '{fecha_hasta}'")

    join_articulo, where_articulo = _build_articulo_filters(genericos, marcas)
    where_cliente = _build_cliente_filters(rutas, preventistas, fuerza_venta)

    if where_articulo:
        where_clauses.extend(where_articulo)
    if where_cliente:
        where_clauses.extend(where_cliente)

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = f"""
        SELECT
            f.id_cliente,
            COALESCE(c.razon_social, 'Cliente ' || f.id_cliente::text) as razon_social,
            COALESCE(c.fantasia, '') as fantasia,
            c.latitud,
            c.longitud,
            COALESCE(c.des_localidad, 'Sin localidad') as localidad,
            COALESCE(c.des_provincia, 'Sin provincia') as provincia,
            COALESCE(c.des_ramo, 'Sin ramo') as ramo,
            COALESCE(c.des_canal_mkt, 'Sin canal') as canal,
            COALESCE(c.des_segmento_mkt, 'Sin segmento') as segmento,
            COALESCE(c.des_subcanal_mkt, 'Sin subcanal') as subcanal,
            COALESCE(c.des_lista_precio, 'Sin lista') as lista_precio,
            SUM(f.cantidades_total) as cantidad_total,
            SUM(f.subtotal_final) as facturacion,
            COUNT(DISTINCT f.nro_doc) as cantidad_documentos,
            c.id_ruta_fv1,
            c.id_ruta_fv4,
            c.des_personal_fv1 as preventista_fv1,
            c.des_personal_fv4 as preventista_fv4,
            COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        {join_articulo}
        WHERE {where_sql}
        GROUP BY f.id_cliente, c.razon_social, c.fantasia, c.latitud, c.longitud,
                 c.des_localidad, c.des_provincia, c.des_ramo,
                 c.des_canal_mkt, c.des_segmento_mkt, c.des_subcanal_mkt, c.des_lista_precio,
                 c.id_ruta_fv1, c.id_ruta_fv4, c.des_personal_fv1, c.des_personal_fv4, c.des_sucursal
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return _process_ventas_df(df)


def cargar_ventas_animacion(fecha_desde=None, fecha_hasta=None, genericos=None, marcas=None, rutas=None, preventistas=None, fuerza_venta=None, granularidad='semana'):
    """Carga ventas agregadas por cliente y período partiendo de fact_ventas para incluir TODAS las ventas."""

    trunc_map = {
        'dia': ('day', '%Y-%m-%d'),
        'semana': ('week', '%Y-%m-%d'),
        'mes': ('month', '%Y-%m')
    }
    trunc_sql, date_format = trunc_map.get(granularidad, ('week', '%Y-%m-%d'))

    where_clauses = []

    if fecha_desde and fecha_hasta:
        where_clauses.append(f"f.fecha_comprobante BETWEEN '{fecha_desde}' AND '{fecha_hasta}'")

    join_articulo, where_articulo = _build_articulo_filters(genericos, marcas)
    where_cliente = _build_cliente_filters(rutas, preventistas, fuerza_venta)

    if where_articulo:
        where_clauses.extend(where_articulo)
    if where_cliente:
        where_clauses.extend(where_cliente)

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = f"""
        SELECT
            f.id_cliente,
            COALESCE(c.razon_social, 'Cliente ' || f.id_cliente::text) as razon_social,
            COALESCE(c.fantasia, '') as fantasia,
            c.latitud,
            c.longitud,
            COALESCE(c.des_localidad, 'Sin localidad') as localidad,
            COALESCE(c.des_provincia, 'Sin provincia') as provincia,
            COALESCE(c.des_ramo, 'Sin ramo') as ramo,
            COALESCE(c.des_canal_mkt, 'Sin canal') as canal,
            COALESCE(c.des_segmento_mkt, 'Sin segmento') as segmento,
            COALESCE(c.des_subcanal_mkt, 'Sin subcanal') as subcanal,
            COALESCE(c.des_lista_precio, 'Sin lista') as lista_precio,
            DATE_TRUNC('{trunc_sql}', f.fecha_comprobante)::date as periodo,
            SUM(f.cantidades_total) as cantidad_total,
            SUM(f.subtotal_final) as facturacion,
            COUNT(DISTINCT f.nro_doc) as cantidad_documentos,
            c.id_ruta_fv1,
            c.id_ruta_fv4,
            c.des_personal_fv1 as preventista_fv1,
            c.des_personal_fv4 as preventista_fv4,
            COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal
        FROM gold.fact_ventas f
        LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal
        {join_articulo}
        WHERE {where_sql}
        GROUP BY f.id_cliente, c.razon_social, c.fantasia, c.latitud, c.longitud,
                 c.des_localidad, c.des_provincia, c.des_ramo,
                 c.des_canal_mkt, c.des_segmento_mkt, c.des_subcanal_mkt, c.des_lista_precio,
                 c.id_ruta_fv1, c.id_ruta_fv4, c.des_personal_fv1, c.des_personal_fv4, c.des_sucursal,
                 DATE_TRUNC('{trunc_sql}', f.fecha_comprobante)
        ORDER BY periodo
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if len(df) == 0:
        return df

    df = _process_ventas_df(df)
    df['periodo'] = pd.to_datetime(df['periodo']).dt.strftime(date_format)

    return df


def cargar_ventas_por_fecha(fecha_desde=None, fecha_hasta=None, canales=None, subcanales=None, localidades=None, listas_precio=None, sucursales=None, genericos=None, marcas=None, rutas=None, preventistas=None, fuerza_venta=None):
    """Carga ventas agregadas por fecha para el gráfico de evolución."""

    where_clauses = []

    if fecha_desde and fecha_hasta:
        where_clauses.append(f"f.fecha_comprobante BETWEEN '{fecha_desde}' AND '{fecha_hasta}'")

    # Filtros de cliente (usando gold.dim_cliente)
    join_cliente = "LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal"

    if canales and len(canales) > 0:
        canales_escaped = [c.replace("'", "''") for c in canales]
        where_clauses.append(f"COALESCE(c.des_canal_mkt, 'Sin canal') IN ('" + "','".join(canales_escaped) + "')")

    if subcanales and len(subcanales) > 0:
        subcanales_escaped = [s.replace("'", "''") for s in subcanales]
        where_clauses.append(f"COALESCE(c.des_subcanal_mkt, 'Sin subcanal') IN ('" + "','".join(subcanales_escaped) + "')")

    if localidades and len(localidades) > 0:
        localidades_escaped = [l.replace("'", "''") for l in localidades]
        where_clauses.append(f"COALESCE(c.des_localidad, 'Sin localidad') IN ('" + "','".join(localidades_escaped) + "')")

    if listas_precio and len(listas_precio) > 0:
        listas_escaped = [l.replace("'", "''") for l in listas_precio]
        where_clauses.append(f"COALESCE(c.des_lista_precio, 'Sin lista') IN ('" + "','".join(listas_escaped) + "')")

    if sucursales and len(sucursales) > 0:
        sucursales_escaped = [s.replace("'", "''") for s in sucursales]
        where_clauses.append(f"COALESCE(c.des_sucursal, 'Sin sucursal') IN ('" + "','".join(sucursales_escaped) + "')")

    # Filtros de ruta (clave compuesta id_sucursal|id_ruta)
    if rutas and len(rutas) > 0:
        ruta_where = _build_ruta_where(rutas, fuerza_venta)
        if ruta_where:
            where_clauses.append(ruta_where)

    if preventistas and len(preventistas) > 0:
        prev_escaped = [p.replace("'", "''") for p in preventistas]
        prev_list = "'" + "','".join(prev_escaped) + "'"
        if fuerza_venta == 'FV1':
            where_clauses.append(f"c.des_personal_fv1 IN ({prev_list})")
        elif fuerza_venta == 'FV4':
            where_clauses.append(f"c.des_personal_fv4 IN ({prev_list})")
        else:
            where_clauses.append(f"(c.des_personal_fv1 IN ({prev_list}) OR c.des_personal_fv4 IN ({prev_list}))")

    # Filtros de articulo
    join_articulo = ""
    if genericos and len(genericos) > 0:
        join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        genericos_escaped = [g.replace("'", "''") for g in genericos]
        where_clauses.append(f"a.generico IN ('" + "','".join(genericos_escaped) + "')")
    if marcas and len(marcas) > 0:
        if not join_articulo:
            join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        marcas_escaped = [m.replace("'", "''") for m in marcas]
        where_clauses.append(f"a.marca IN ('" + "','".join(marcas_escaped) + "')")

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = f"""
        SELECT
            f.fecha_comprobante as fecha,
            SUM(f.cantidades_total) as cantidad_total,
            SUM(f.subtotal_final) as facturacion,
            COUNT(DISTINCT f.nro_doc) as cantidad_documentos,
            COUNT(DISTINCT f.id_cliente) as clientes
        FROM gold.fact_ventas f
        {join_cliente}
        {join_articulo}
        WHERE {where_sql}
        GROUP BY f.fecha_comprobante
        ORDER BY f.fecha_comprobante
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df['cantidad_total'] = df['cantidad_total'].astype(float)
    df['facturacion'] = df['facturacion'].astype(float)

    return df


def cargar_ventas_por_cliente_generico(fecha_desde=None, fecha_hasta=None, genericos=None, marcas=None, rutas=None, preventistas=None, fuerza_venta=None, top_n=5):
    """Obtiene top N genéricos por cliente para el hover del mapa."""

    where_clauses = []

    if fecha_desde and fecha_hasta:
        where_clauses.append(f"f.fecha_comprobante BETWEEN '{fecha_desde}' AND '{fecha_hasta}'")

    join_articulo, where_articulo = _build_articulo_filters(genericos, marcas)
    where_cliente = _build_cliente_filters(rutas, preventistas, fuerza_venta)

    if where_articulo:
        where_clauses.extend(where_articulo)
    if where_cliente:
        where_clauses.extend(where_cliente)

    # Siempre necesitamos dim_articulo para el genérico
    join_articulo = join_articulo or "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"

    # JOIN con dim_cliente solo si hay filtros de cliente
    join_cliente = ""
    if where_cliente:
        join_cliente = "LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal"

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = f"""
        WITH ventas_generico AS (
            SELECT
                f.id_cliente,
                COALESCE(a.generico, 'Sin categoria') as generico,
                SUM(f.cantidades_total) as cantidad_total,
                SUM(f.subtotal_final) as facturacion,
                COUNT(DISTINCT f.nro_doc) as cantidad_documentos,
                ROW_NUMBER() OVER (PARTITION BY f.id_cliente ORDER BY SUM(f.cantidades_total) DESC) as rn
            FROM gold.fact_ventas f
            {join_cliente}
            {join_articulo}
            WHERE {where_sql}
            GROUP BY f.id_cliente, a.generico
        )
        SELECT id_cliente, generico, cantidad_total, facturacion, cantidad_documentos
        FROM ventas_generico
        WHERE rn <= {top_n}
        ORDER BY id_cliente, cantidad_total DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


def _build_all_filters(fecha_desde, fecha_hasta, canales, subcanales, localidades,
                       listas_precio, sucursales, genericos, marcas, rutas,
                       preventistas, fuerza_venta):
    """Construye join y where para todos los filtros (reutilizable)."""
    where_clauses = []
    need_cliente = False

    if fecha_desde and fecha_hasta:
        where_clauses.append(f"f.fecha_comprobante BETWEEN '{fecha_desde}' AND '{fecha_hasta}'")

    # Filtros dim_cliente
    if canales and len(canales) > 0:
        need_cliente = True
        canales_escaped = [c.replace("'", "''") for c in canales]
        where_clauses.append(f"COALESCE(c.des_canal_mkt, 'Sin canal') IN ('" + "','".join(canales_escaped) + "')")
    if subcanales and len(subcanales) > 0:
        need_cliente = True
        subcanales_escaped = [s.replace("'", "''") for s in subcanales]
        where_clauses.append(f"COALESCE(c.des_subcanal_mkt, 'Sin subcanal') IN ('" + "','".join(subcanales_escaped) + "')")
    if localidades and len(localidades) > 0:
        need_cliente = True
        localidades_escaped = [l.replace("'", "''") for l in localidades]
        where_clauses.append(f"COALESCE(c.des_localidad, 'Sin localidad') IN ('" + "','".join(localidades_escaped) + "')")
    if listas_precio and len(listas_precio) > 0:
        need_cliente = True
        listas_escaped = [l.replace("'", "''") for l in listas_precio]
        where_clauses.append(f"COALESCE(c.des_lista_precio, 'Sin lista') IN ('" + "','".join(listas_escaped) + "')")
    if sucursales and len(sucursales) > 0:
        need_cliente = True
        sucursales_escaped = [s.replace("'", "''") for s in sucursales]
        where_clauses.append(f"COALESCE(c.des_sucursal, 'Sin sucursal') IN ('" + "','".join(sucursales_escaped) + "')")

    # Rutas y preventistas
    if rutas and len(rutas) > 0:
        need_cliente = True
        ruta_where = _build_ruta_where(rutas, fuerza_venta)
        if ruta_where:
            where_clauses.append(ruta_where)
    if preventistas and len(preventistas) > 0:
        need_cliente = True
        prev_escaped = [p.replace("'", "''") for p in preventistas]
        prev_list = "'" + "','".join(prev_escaped) + "'"
        if fuerza_venta == 'FV1':
            where_clauses.append(f"c.des_personal_fv1 IN ({prev_list})")
        elif fuerza_venta == 'FV4':
            where_clauses.append(f"c.des_personal_fv4 IN ({prev_list})")
        else:
            where_clauses.append(f"(c.des_personal_fv1 IN ({prev_list}) OR c.des_personal_fv4 IN ({prev_list}))")

    join_cliente = "LEFT JOIN gold.dim_cliente c ON f.id_cliente = c.id_cliente AND f.id_sucursal = c.id_sucursal" if need_cliente else ""

    # Filtros dim_articulo
    join_articulo = ""
    if genericos and len(genericos) > 0:
        join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        genericos_escaped = [g.replace("'", "''") for g in genericos]
        where_clauses.append(f"a.generico IN ('" + "','".join(genericos_escaped) + "')")
    if marcas and len(marcas) > 0:
        if not join_articulo:
            join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"
        marcas_escaped = [m.replace("'", "''") for m in marcas]
        where_clauses.append(f"a.marca IN ('" + "','".join(marcas_escaped) + "')")

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
    return join_cliente, join_articulo, where_sql


def cargar_ventas_por_generico_top(fecha_desde=None, fecha_hasta=None, canales=None,
                                    subcanales=None, localidades=None, listas_precio=None,
                                    sucursales=None, genericos=None, marcas=None, rutas=None,
                                    preventistas=None, fuerza_venta=None, metrica='cantidad_total',
                                    top_n=10):
    """Top N genéricos por métrica seleccionada, respetando todos los filtros."""
    join_cliente, join_articulo, where_sql = _build_all_filters(
        fecha_desde, fecha_hasta, canales, subcanales, localidades,
        listas_precio, sucursales, genericos, marcas, rutas,
        preventistas, fuerza_venta
    )
    # Siempre necesitamos dim_articulo para el genérico
    if not join_articulo:
        join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"

    metrica_sql = {
        'cantidad_total': 'SUM(f.cantidades_total)',
        'facturacion': 'SUM(f.subtotal_final)',
        'cantidad_documentos': 'COUNT(DISTINCT f.nro_doc)',
    }
    agg = metrica_sql.get(metrica, 'SUM(f.cantidades_total)')

    query = f"""
        SELECT
            COALESCE(a.generico, 'Sin categoria') as generico,
            {agg} as valor
        FROM gold.fact_ventas f
        {join_cliente}
        {join_articulo}
        WHERE {where_sql}
        GROUP BY a.generico
        ORDER BY valor DESC
        LIMIT {int(top_n)}
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df['valor'] = df['valor'].astype(float)
    return df


def cargar_ventas_por_marca_top(fecha_desde=None, fecha_hasta=None, canales=None,
                                 subcanales=None, localidades=None, listas_precio=None,
                                 sucursales=None, genericos=None, marcas=None, rutas=None,
                                 preventistas=None, fuerza_venta=None, metrica='cantidad_total',
                                 top_n=10):
    """Top N marcas por métrica seleccionada, respetando todos los filtros."""
    join_cliente, join_articulo, where_sql = _build_all_filters(
        fecha_desde, fecha_hasta, canales, subcanales, localidades,
        listas_precio, sucursales, genericos, marcas, rutas,
        preventistas, fuerza_venta
    )
    if not join_articulo:
        join_articulo = "LEFT JOIN gold.dim_articulo a ON f.id_articulo = a.id_articulo"

    metrica_sql = {
        'cantidad_total': 'SUM(f.cantidades_total)',
        'facturacion': 'SUM(f.subtotal_final)',
        'cantidad_documentos': 'COUNT(DISTINCT f.nro_doc)',
    }
    agg = metrica_sql.get(metrica, 'SUM(f.cantidades_total)')

    query = f"""
        SELECT
            COALESCE(a.marca, 'Sin marca') as marca,
            {agg} as valor
        FROM gold.fact_ventas f
        {join_cliente}
        {join_articulo}
        WHERE {where_sql}
        GROUP BY a.marca
        ORDER BY valor DESC
        LIMIT {int(top_n)}
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df['valor'] = df['valor'].astype(float)
    return df


def buscar_clientes(texto_busqueda, limite=50):
    """Busca clientes por razon social, fantasia o ID."""
    texto = texto_busqueda.strip().replace("'", "''")

    # Si es numérico, buscar también por ID
    try:
        id_num = int(texto)
        filtro_id = f"OR c.id_cliente = {id_num}"
    except ValueError:
        filtro_id = ""

    query = f"""
        SELECT DISTINCT
            c.id_cliente,
            c.razon_social,
            COALESCE(c.fantasia, '') as fantasia,
            COALESCE(c.des_localidad, 'Sin localidad') as localidad,
            COALESCE(c.des_provincia, 'Sin provincia') as provincia,
            COALESCE(c.des_canal_mkt, 'Sin canal') as canal,
            COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal,
            COALESCE(c.des_ramo, 'Sin ramo') as ramo
        FROM gold.dim_cliente c
        WHERE (
            c.razon_social ILIKE '%%{texto}%%'
            OR c.fantasia ILIKE '%%{texto}%%'
            {filtro_id}
        )
        ORDER BY c.razon_social
        LIMIT {int(limite)}
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def cargar_info_cliente(id_cliente):
    """Obtiene datos maestros de un cliente desde dim_cliente."""
    query = f"""
        SELECT
            c.id_cliente,
            c.razon_social,
            COALESCE(c.fantasia, '') as fantasia,
            COALESCE(c.des_localidad, 'Sin localidad') as localidad,
            COALESCE(c.des_provincia, 'Sin provincia') as provincia,
            COALESCE(c.des_canal_mkt, 'Sin canal') as canal,
            COALESCE(c.des_segmento_mkt, 'Sin segmento') as segmento,
            COALESCE(c.des_subcanal_mkt, 'Sin subcanal') as subcanal,
            COALESCE(c.des_lista_precio, 'Sin lista') as lista_precio,
            COALESCE(c.des_sucursal, 'Sin sucursal') as sucursal,
            COALESCE(c.des_ramo, 'Sin ramo') as ramo,
            c.id_ruta_fv1,
            c.id_ruta_fv4,
            c.des_personal_fv1 as preventista_fv1,
            c.des_personal_fv4 as preventista_fv4
        FROM gold.dim_cliente c
        WHERE c.id_cliente = {int(id_cliente)}
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df


def cargar_ventas_cliente_detalle(id_cliente):
    """
    Obtiene todos los articulos con ventas desglosadas por mes,
    mas los articulos sin venta (bultos=NULL, anio=NULL, mes=NULL).
    Una sola query reemplaza las 2 anteriores.
    """
    query = f"""
        WITH ventas AS (
            SELECT
                f.id_articulo,
                EXTRACT(YEAR FROM f.fecha_comprobante)::int as anio,
                EXTRACT(MONTH FROM f.fecha_comprobante)::int as mes,
                SUM(f.cantidades_total) as bultos
            FROM gold.fact_ventas f
            WHERE f.id_cliente = {int(id_cliente)}
            GROUP BY f.id_articulo, anio, mes
        )
        SELECT
            a.id_articulo,
            COALESCE(a.generico, 'Sin categoria') as generico,
            COALESCE(a.marca, 'Sin marca') as marca,
            COALESCE(a.des_articulo, 'Articulo ' || a.id_articulo::text) as articulo,
            v.anio,
            v.mes,
            v.bultos
        FROM gold.dim_articulo a
        LEFT JOIN ventas v ON a.id_articulo = v.id_articulo
        WHERE a.generico IN ('CERVEZAS', 'VINOS CCU', 'AGUAS DANONE', 'FRATELLI B', 'VINOS', 'VINOS FINOS')
        ORDER BY a.generico, a.marca, a.des_articulo, v.anio, v.mes
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df
