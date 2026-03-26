#!/bin/bash
# Setup Redis for Sales Dashboard
# Usage: sudo bash scripts/setup-redis.sh
#
# Installs Redis, configures for production, and enables on boot.
# Safe to run multiple times (idempotent).

set -e

echo "=== Sales Dashboard — Redis Setup ==="

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Error: ejecutar con sudo"
    exit 1
fi

# Install Redis
echo "Instalando Redis..."
apt-get update -qq
apt-get install -y redis-server

# Configure for production
echo "Configurando Redis..."
REDIS_CONF="/etc/redis/redis.conf"

# Backup original config
if [ ! -f "${REDIS_CONF}.bak" ]; then
    cp "$REDIS_CONF" "${REDIS_CONF}.bak"
fi

# Bind only to localhost (security)
sed -i 's/^bind .*/bind 127.0.0.1 ::1/' "$REDIS_CONF"

# Set max memory (256MB — sufficient for dashboard cache)
if grep -q "^maxmemory " "$REDIS_CONF"; then
    sed -i 's/^maxmemory .*/maxmemory 256mb/' "$REDIS_CONF"
else
    echo "maxmemory 256mb" >> "$REDIS_CONF"
fi

# Eviction policy: remove least recently used keys when memory is full
if grep -q "^maxmemory-policy " "$REDIS_CONF"; then
    sed -i 's/^maxmemory-policy .*/maxmemory-policy allkeys-lru/' "$REDIS_CONF"
else
    echo "maxmemory-policy allkeys-lru" >> "$REDIS_CONF"
fi

# Disable persistence (cache is ephemeral — rebuilt on app startup)
sed -i 's/^save /#save /' "$REDIS_CONF"
if grep -q "^appendonly " "$REDIS_CONF"; then
    sed -i 's/^appendonly .*/appendonly no/' "$REDIS_CONF"
fi

# Enable and start
echo "Iniciando Redis..."
systemctl enable redis-server
systemctl restart redis-server

# Verify
if redis-cli ping | grep -q "PONG"; then
    echo ""
    echo "=== Redis configurado ==="
    echo "  - Bind: 127.0.0.1"
    echo "  - Max memory: 256MB"
    echo "  - Eviction: allkeys-lru"
    echo "  - Persistence: deshabilitada"
    echo "  - Status: activo"
    echo ""
    echo "Agregar a .env:"
    echo "  REDIS_URL=redis://localhost:6379/0"
else
    echo "ERROR: Redis no responde"
    exit 1
fi
