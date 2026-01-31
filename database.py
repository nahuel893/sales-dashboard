"""
Modulo de Base de Datos
Gestiona la conexion con la base de datos PostgreSQL del proyecto medallion-etl.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Ruta al .env del proyecto medallion-etl
MEDALLION_ETL_ROOT = Path.home() / 'Desktop' / 'medallion-etl'

class Settings(BaseSettings):
    """Configuracion cargada desde variables de entorno."""
    model_config = SettingsConfigDict(
        env_file=str(MEDALLION_ETL_ROOT / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )
    POSTGRES_USER: str = Field(..., description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str = Field(..., description="Contrasena de PostgreSQL")
    DATABASE: str = Field(..., description="Nombre de la base de datos")
    IP_SERVER: str = Field(..., description="Direccion IP del servidor")

settings = Settings()

SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host='192.168.1.132',
    port=5432,
    database=settings.DATABASE,
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
