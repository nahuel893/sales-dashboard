# Autenticacion y Control de Acceso (RBAC)

Sistema de autenticacion con control de acceso basado en roles (RBAC) por sucursal.

## Activacion

La autenticacion es **condicional**: se activa solo si `SECRET_KEY` esta definida en `.env`.

```env
# .env
SECRET_KEY=una-clave-secreta-larga-y-aleatoria
```

Sin `SECRET_KEY` (o con valor vacio), la app funciona igual que antes — sin login, sin restricciones.

## Roles

| Rol | Acceso a datos | Admin usuarios | Descripcion |
|-----|---------------|----------------|-------------|
| **admin** | Todas las sucursales | Si (`/admin/usuarios`) | Acceso total al sistema |
| **gerente** | Todas las sucursales | No | Ve todos los datos sin restriccion |
| **supervisor** | Solo sucursales asignadas | No | Ve unicamente datos de sus sucursales |

## Setup inicial

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Se agregaron `flask-login` y `flask-session`.

### 2. Configurar SECRET_KEY

```bash
# Generar una clave aleatoria
python -c "import secrets; print(secrets.token_hex(32))"

# Agregar al .env
echo 'SECRET_KEY=<clave-generada>' >> .env
```

### 3. Crear tablas y usuario admin

```bash
python auth/seed.py
```

Esto crea:
- Schema `app` en PostgreSQL
- Tablas: `roles`, `users`, `user_sucursales`, `sessions`
- Roles: admin, gerente, supervisor
- Usuario inicial: `admin` / `admin`

El script es idempotente — se puede ejecutar multiples veces sin duplicar datos.

**Cambiar la contraseña del admin desde `/admin/usuarios` despues del primer login.**

### 4. Iniciar la app

```bash
python app.py
```

Con `SECRET_KEY` configurada, la app redirige a `/login` automaticamente.

## Arquitectura

### Archivos

```
auth/
├── __init__.py          # Package init
├── models.py            # Modelos ORM: Role, User, UserSucursal
├── utils.py             # hash_password(), check_password(), get_user_sucursales()
├── middleware.py         # init_auth(), protect_all_routes()
├── schema.sql           # DDL de tablas (schema app)
└── seed.py              # Script CLI para inicializar BD

layouts/
├── login_layout.py      # Pagina de login
└── admin_layout.py      # Pagina de gestion de usuarios

callbacks/
├── auth_callbacks.py    # Login (validacion de credenciales)
└── admin_callbacks.py   # CRUD de usuarios
```

### Flujo de autenticacion

1. `app.py` verifica si `SECRET_KEY` esta en `.env`
2. Si esta, llama a `init_auth()` (configura Flask-Login + Flask-Session con PostgreSQL)
3. `protect_all_routes()` registra un `before_request` que:
   - Permite paths publicos (`/login`, `/assets/`, `/_dash-layout`, etc.)
   - Redirige a `/login` si no hay sesion
   - Retorna 401 en callbacks Dash (`/_dash-update-component`) sin sesion
4. Login exitoso → `login_user()` → redirect a `/`
5. Logout → `/logout` → `logout_user()` → redirect a `/login`

### Deployment con gunicorn

SQLite no soporta escrituras concurrentes desde multiples procesos. Al deployar con gunicorn, usar **un unico worker con threads**:

```bash
gunicorn app:server --workers 1 --threads 4 --bind 0.0.0.0:8050
```

Multiples workers (`--workers N` con N > 1) pueden generar errores de "database is locked" bajo carga.

### Filtrado RBAC por sucursal

La funcion central es `get_user_sucursales()` en `auth/utils.py`:

| Situacion | Retorna | Efecto |
|-----------|---------|--------|
| Auth desactivada | `None` | Sin filtro (ve todo) |
| Admin o Gerente | `None` | Sin filtro (ve todo) |
| Supervisor con sucursales | `[1, 3, 5]` | Solo esas sucursales |
| Supervisor sin sucursales | `[]` | No ve nada |

Cada callback obtiene `suc_perm = get_user_sucursales()` y lo pasa como `sucursales_permitidas` a las funciones de queries. Las queries agregan `AND c.id_sucursal IN (...)` cuando la lista no es `None`.

**Archivos de callbacks que aplican RBAC:**
- `callbacks/callbacks.py` — Dashboard de ventas (mapas, KPIs)
- `callbacks/tablero_callbacks.py` — Tablero de comparacion anual
- `callbacks/ytd_callbacks.py` — Dashboard YTD
- `callbacks/cliente_callbacks.py` — Detalle de cliente

**Funciones de queries con `sucursales_permitidas`:**
- `data/queries.py`: `cargar_ventas_por_cliente`, `cargar_ventas_animacion`, `cargar_ventas_por_fecha`, `cargar_ventas_por_cliente_generico`, `cargar_info_cliente`
- `data/ytd_queries.py`: todas las funciones (`obtener_ventas_ytd`, `obtener_ventas_por_mes`, `obtener_ventas_por_generico`, `obtener_ventas_por_sucursal`, `obtener_ventas_por_canal`, `calcular_target_automatico`, `calcular_targets_por_generico`, `calcular_targets_por_sucursal`, `calcular_crecimiento_mensual`, `obtener_dias_inventario`)

## Gestion de usuarios (`/admin/usuarios`)

Accesible solo para usuarios con rol **admin**. Permite:

- **Crear** usuarios con nombre, usuario, contraseña, rol
- **Editar** usuarios existentes (contraseña opcional al editar)
- **Activar/Desactivar** usuarios (no se eliminan, se marcan como inactivos)
- **Asignar sucursales** a supervisores (MultiSelect con sucursales de `dim_cliente`)

La card "Gestion de Usuarios" aparece en la pagina de inicio solo para admins.

## Base de datos

### Storage: SQLite local (`auth/auth.db`)

Los datos de autenticacion (usuarios, roles, sesiones) se almacenan en un archivo SQLite separado de PostgreSQL.

- **Ubicacion**: `auth/auth.db` en la raiz del proyecto
- **Excluido de git**: listado en `.gitignore` — debe incluirse en el backup del servidor por separado
- **Creacion automatica**: `python auth/seed.py` crea el archivo si no existe

```
auth/auth.db
├── roles         (id, name, description)
├── users         (id, username, password_hash, full_name, role_id, is_active)
├── user_sucursales (id, user_id, id_sucursal)  -- UNIQUE(user_id, id_sucursal)
└── sessions      (sesiones server-side de flask-session)
```

### Seguridad

- Passwords hasheados con bcrypt
- Hashes SHA-256 legacy (`salt:hex`) son re-hasheados a bcrypt transparentemente en el proximo login
- Sesiones server-side en SQLite (no cookies con datos sensibles)
- Duracion de sesion: 24 horas
- Usuarios inactivos (`is_active = false`) no pueden hacer login

### Nota de migracion

Los usuarios existentes en `app.*` (PostgreSQL) se pierden al migrar a SQLite.
Ejecutar `python auth/seed.py` para crear el usuario admin inicial y distribuir nuevas credenciales.

## Retrocompatibilidad

El sistema es 100% retrocompatible:

- Sin `SECRET_KEY` → no se importan modulos de auth, no se crean tablas, la app funciona identica
- `get_user_sucursales()` retorna `None` si auth no esta activa → queries sin filtro
- Los archivos de auth (`auth/`, `layouts/login_layout.py`, `layouts/admin_layout.py`, `callbacks/auth_callbacks.py`, `callbacks/admin_callbacks.py`) solo se importan condicionalmente
