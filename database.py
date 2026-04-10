"""
Modulo de Base de Datos
Gestiona la conexion con la base de datos PostgreSQL.
"""
from pathlib import Path
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Ruta al .env del proyecto actual
PROJECT_ROOT = Path(__file__).parent


class Settings(BaseSettings):
    """Configuracion cargada desde variables de entorno o archivo .env"""
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )
    POSTGRES_USER: str = Field(..., description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str = Field(..., description="Contrasena de PostgreSQL")
    POSTGRES_DB: str = Field(..., description="Nombre de la base de datos")
    POSTGRES_HOST: str = Field(default="localhost", description="IP o hostname del servidor")
    POSTGRES_PORT: int = Field(default=5432, description="Puerto de PostgreSQL")
    SECRET_KEY: str = Field(default="", description="Secret key para sesiones (vacio = auth desactivada)")
    ALLOWED_ORIGINS: str = Field(default="", description="Comma-separated allowed origins for POST validation (empty = skip check)")
    REDIS_URL: str = Field(default="", description="Redis URL for cache and sessions (empty = in-memory/filesystem)")
    SESSION_TIMEOUT: int = Field(default=1800, description="Idle session timeout in seconds (default 30min)")


settings = Settings()

SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)

SQLALCHEMY_DATABASE_URL_STR = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Auth engine — SQLite local (usuarios y roles; sesiones via filesystem)
SQLITE_AUTH_PATH = PROJECT_ROOT / 'auth' / 'auth.db'
SQLITE_AUTH_URL = f"sqlite:///{SQLITE_AUTH_PATH}"
auth_engine = create_engine(SQLITE_AUTH_URL, connect_args={"check_same_thread": False})
AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)


def get_db():
    """Generador de sesion de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
