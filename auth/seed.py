#!/usr/bin/env python3
"""
Script CLI para inicializar el schema de autenticación.
Crea tablas, roles y usuario admin inicial. Idempotente.

Uso:
    python auth/seed.py
"""
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database import engine
from auth.utils import hash_password


def seed():
    """Crea schema, tablas, roles y admin inicial."""
    print("Inicializando schema de autenticación...")

    # Leer y ejecutar schema.sql
    schema_path = Path(__file__).parent / 'schema.sql'
    schema_sql = schema_path.read_text()

    with engine.begin() as conn:
        # Ejecutar cada statement del schema
        for statement in schema_sql.split(';'):
            # Quitar líneas de comentario y espacios vacíos
            lines = [l for l in statement.splitlines() if l.strip() and not l.strip().startswith('--')]
            sql = '\n'.join(lines).strip()
            if sql:
                conn.execute(text(sql))
        print("  - Schema y tablas creados")

        # Insertar roles (idempotente via ON CONFLICT)
        roles = [
            ('admin', 'Acceso total + gestión de usuarios'),
            ('gerente', 'Ve todos los datos de todas las sucursales'),
            ('supervisor', 'Ve solo datos de sus sucursales asignadas'),
        ]
        for name, description in roles:
            conn.execute(text("""
                INSERT INTO app.roles (name, description)
                VALUES (:name, :description)
                ON CONFLICT (name) DO NOTHING
            """), {'name': name, 'description': description})
        print("  - Roles creados: admin, gerente, supervisor")

        # Crear admin inicial (idempotente)
        existing = conn.execute(
            text("SELECT id FROM app.users WHERE username = 'admin'")
        ).fetchone()

        if not existing:
            admin_role = conn.execute(
                text("SELECT id FROM app.roles WHERE name = 'admin'")
            ).fetchone()
            conn.execute(text("""
                INSERT INTO app.users (username, password_hash, full_name, role_id)
                VALUES (:username, :password_hash, :full_name, :role_id)
            """), {
                'username': 'admin',
                'password_hash': hash_password('admin'),
                'full_name': 'Administrador',
                'role_id': admin_role[0],
            })
            print("  - Usuario admin creado (password: admin) — CAMBIAR EN PRODUCCIÓN")
        else:
            print("  - Usuario admin ya existe, omitido")

    print("Inicialización completada.")


if __name__ == '__main__':
    seed()
