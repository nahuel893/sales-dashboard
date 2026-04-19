"""
Cache module — flask-caching with Redis or SimpleCache backend.
Backend selected by REDIS_URL env var: set = Redis, empty = SimpleCache.
"""
from functools import wraps
from flask_caching import Cache

# Cache TTL (seconds)
CACHE_TTL_DIM = 28800       # 8 hours — static dimension data
CACHE_TTL_QUERY = 21600     # 6 hours — parametric sales queries

cache = Cache()


def init_app(server):
    """Initialize cache with the Flask server. Uses Redis if REDIS_URL is set."""
    from database import settings
    config = {'CACHE_DEFAULT_TIMEOUT': CACHE_TTL_QUERY}

    if settings.REDIS_URL:
        config['CACHE_TYPE'] = 'RedisCache'
        config['CACHE_REDIS_URL'] = settings.REDIS_URL
        config['CACHE_KEY_PREFIX'] = 'sd_cache:'
        # Fail-fast: verify Redis connection
        import redis as redis_lib
        redis_lib.from_url(settings.REDIS_URL).ping()
        print("  - Cache: Redis conectado")
    else:
        config['CACHE_TYPE'] = 'SimpleCache'
        config['CACHE_THRESHOLD'] = 500
        print("  - Cache: SimpleCache (in-memory)")

    cache.init_app(server, config=config)


def hashable_args(func):
    """Decorator: converts list->tuple, dict->frozenset(items) for hashable cache keys."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = tuple(
            tuple(a) if isinstance(a, list)
            else frozenset(a.items()) if isinstance(a, dict)
            else a
            for a in args
        )
        new_kwargs = {
            k: tuple(v) if isinstance(v, list)
            else frozenset(v.items()) if isinstance(v, dict)
            else v
            for k, v in kwargs.items()
        }
        return func(*new_args, **new_kwargs)
    return wrapper


def filtrar_sucursales(df, sucursales_permitidas):
    """Post-query RBAC filter. Returns df unchanged if sucursales is None.
    Filters df[df['id_sucursal'].isin(sucursales)] otherwise.
    Returns empty df if sucursales is empty list."""
    if sucursales_permitidas is None:
        return df
    if len(sucursales_permitidas) == 0:
        return df.iloc[0:0].copy()
    if 'id_sucursal' in df.columns:
        return df[df['id_sucursal'].isin(sucursales_permitidas)].copy()
    return df


def warmup_cache():
    """Pre-fire dimension queries + current-month cargar_ventas_por_cliente."""
    from datetime import date
    from data.queries import (
        obtener_genericos, obtener_marcas, obtener_rutas, obtener_preventistas,
        obtener_rango_fechas, cargar_ventas_por_cliente
    )

    print("Calentando cache...")
    # Dimension queries
    obtener_genericos()
    obtener_marcas()
    obtener_rutas()
    obtener_preventistas()
    obtener_rango_fechas()

    # Current month sales (most common query)
    hoy = date.today()
    cargar_ventas_por_cliente(hoy.replace(day=1), hoy)
    print("  - Cache calentado")
