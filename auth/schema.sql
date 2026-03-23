-- OBSOLETO: el schema se crea automáticamente via Base.metadata.create_all(auth_engine) en seed.py
-- Schema de autenticación y autorización para el dashboard.
-- Ejecutar con: psql -f auth/schema.sql o via auth/seed.py

CREATE SCHEMA IF NOT EXISTS app;

-- Roles del sistema
CREATE TABLE IF NOT EXISTS app.roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200)
);

-- Usuarios
CREATE TABLE IF NOT EXISTS app.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES app.roles(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Relación M2M: usuarios <-> sucursales
CREATE TABLE IF NOT EXISTS app.user_sucursales (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    id_sucursal INTEGER NOT NULL,
    CONSTRAINT uq_user_sucursal UNIQUE (user_id, id_sucursal)
);

-- Sesiones server-side (para flask-session)
CREATE TABLE IF NOT EXISTS app.sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    data BYTEA,
    expiry TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_expiry ON app.sessions(expiry);
