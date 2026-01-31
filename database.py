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


settings = Settings()

SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generador de sesion de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
