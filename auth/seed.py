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

from database import auth_engine, AuthSessionLocal
from auth.models import Base, Role, User
from auth.utils import hash_password


def seed():
    """Crea tablas, roles y admin inicial."""
    print("Inicializando schema de autenticación...")

    # Crear tablas via ORM
    Base.metadata.create_all(auth_engine)
    print("  - Schema y tablas creados")

    db = AuthSessionLocal()
    try:
        # Insertar roles (idempotente)
        roles = [
            ('admin', 'Acceso total + gestión de usuarios'),
            ('gerente', 'Ve todos los datos de todas las sucursales'),
            ('supervisor', 'Ve solo datos de sus sucursales asignadas'),
        ]
        for name, description in roles:
            existing_role = db.query(Role).filter_by(name=name).first()
            if not existing_role:
                db.add(Role(name=name, description=description))
        db.commit()
        print("  - Roles creados: admin, gerente, supervisor")

        # Crear admin inicial (idempotente)
        existing = db.query(User).filter_by(username='admin').first()
        if not existing:
            admin_role = db.query(Role).filter_by(name='admin').first()
            db.add(User(
                username='admin',
                password_hash=hash_password('admin'),
                full_name='Administrador',
                role_id=admin_role.id,
                is_active=True,
            ))
            db.commit()
            print("  - Usuario admin creado (password: admin) — CAMBIAR EN PRODUCCIÓN")
        else:
            print("  - Usuario admin ya existe, omitido")
    finally:
        db.close()

    print("Inicialización completada.")


if __name__ == '__main__':
    seed()
