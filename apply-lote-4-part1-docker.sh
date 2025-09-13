#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 4 - PARTE 1
# PRONAS/PCD System - Docker Production + Nginx
# Execute na raiz do projeto após concluir os Lotes 1, 2 e 3

set -e

echo "🚀 LOTE 4 PARTE 1: Docker Production + Nginx"
echo "============================================="

# Verificar se estrutura existe
if [ ! -d "infra" ]; then
    echo "❌ Estrutura de infraestrutura não encontrada. Execute Lotes anteriores primeiro."
    exit 1
fi

echo "📝 Configurando Docker Production Setup..."

# Nginx Configuration
mkdir -p infra/docker/nginx
cat > infra/docker/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.pronas-pcd.gov.br;" always;

    # Backend upstream
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    # Frontend upstream
    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # Main server configuration
    server {
        listen 443 ssl http2 default_server;
        server_name pronas-pcd.gov.br;

        # SSL Certificate paths (to be mounted)
        ssl_certificate /etc/ssl/certs/pronas-pcd.crt;
        ssl_certificate_key /etc/ssl/private/pronas-pcd.key;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;

            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API Backend
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings for API
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 300s;

            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 128k;
            proxy_buffers 4 256k;
            proxy_busy_buffers_size 256k;
        }

        # Login endpoint with stricter rate limiting
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;

            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # Metrics (restricted access)
        location /metrics {
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;

            proxy_pass http://backend/metrics;
            access_log off;
        }

        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary Accept-Encoding;
        }

        # Security txt
        location /.well-known/security.txt {
            return 200 "Contact: security@pronas-pcd.gov.br\nExpires: 2025-12-31T23:59:59.000Z\nPreferred-Languages: pt-BR, en\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Nginx Dockerfile
cat > infra/docker/nginx/Dockerfile << 'EOF'
FROM nginx:1.25-alpine

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache \
    openssl \
    curl \
    && rm -rf /var/cache/apk/*

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directory
RUN mkdir -p /var/log/nginx

# Create SSL directory
RUN mkdir -p /etc/ssl/certs /etc/ssl/private

# Generate self-signed certificate for development
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/pronas-pcd.key \
    -out /etc/ssl/certs/pronas-pcd.crt \
    -subj "/C=BR/ST=DF/L=Brasilia/O=Ministerio da Saude/CN=pronas-pcd.gov.br"

# Set proper permissions
RUN chmod 600 /etc/ssl/private/pronas-pcd.key
RUN chmod 644 /etc/ssl/certs/pronas-pcd.crt

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
EOF

echo "✅ Nginx configurado!"

echo "📝 Criando Docker Compose para produção..."

# Production Docker Compose
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    build:
      context: ./infra/docker/nginx
      dockerfile: Dockerfile
    container_name: pronas_pcd_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - nginx_logs:/var/log/nginx
      - ssl_certs:/etc/ssl/certs:ro
      - ssl_private:/etc/ssl/private:ro
    depends_on:
      - backend
      - frontend
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.2'
          memory: 128M

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pronas_pcd_backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY}
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - API_DEBUG=false
      - API_RELOAD=false
    volumes:
      - app_logs:/app/logs
      - app_uploads:/app/uploads
    depends_on:
      - db
      - redis
      - minio
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Frontend Next.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pronas_pcd_frontend
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://pronas-pcd.gov.br
      - NEXT_PUBLIC_APP_URL=https://pronas-pcd.gov.br
    depends_on:
      - backend
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: pronas_pcd_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - postgres_backups:/backups
      - ./infra/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "127.0.0.1:5432:5432"  # Only localhost access
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.7
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c log_min_duration_statement=1000
      -c log_line_prefix='%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: pronas_pcd_redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data:/data
      - redis_conf:/usr/local/etc/redis
    ports:
      - "127.0.0.1:6379:6379"  # Only localhost access
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.2'
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    container_name: pronas_pcd_minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
      - MINIO_REGION_NAME=us-east-1
    volumes:
      - minio_data:/data
    ports:
      - "127.0.0.1:9000:9000"  # Only localhost access
      - "127.0.0.1:9001:9001"  # Console access
    networks:
      - pronas_network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  postgres_data:
    driver: local
  postgres_backups:
    driver: local
  redis_data:
    driver: local
  redis_conf:
    driver: local
  minio_data:
    driver: local
  nginx_logs:
    driver: local
  app_logs:
    driver: local
  app_uploads:
    driver: local
  ssl_certs:
    driver: local
  ssl_private:
    driver: local

networks:
  pronas_network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
EOF

echo "✅ Docker Compose Production criado!"

echo "📝 Configurando PostgreSQL inicialização..."

# PostgreSQL init script
mkdir -p infra/docker/postgres
cat > infra/docker/postgres/init.sql << 'EOF'
-- PostgreSQL initialization script for PRONAS/PCD
-- Create additional databases and configure security

-- Create read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'monitoring_password_change_me';
GRANT CONNECT ON DATABASE pronas_pcd_prod TO monitoring;
GRANT USAGE ON SCHEMA public TO monitoring;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;

-- Create backup user
CREATE USER backup_user WITH PASSWORD 'backup_password_change_me';
GRANT CONNECT ON DATABASE pronas_pcd_prod TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

-- Configure connection limits
ALTER USER pronas_user CONNECTION LIMIT 50;
ALTER USER monitoring CONNECTION LIMIT 10;
ALTER USER backup_user CONNECTION LIMIT 5;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Configure logging
ALTER SYSTEM SET log_destination TO 'stderr';
ALTER SYSTEM SET log_statement TO 'mod';
ALTER SYSTEM SET log_min_duration_statement TO 1000;

SELECT pg_reload_conf();
EOF

echo "✅ PostgreSQL configurado!"

echo "📝 Criando scripts de produção..."

# Production environment file
cat > .env.production << 'EOF'
# Production Environment Variables
# DO NOT COMMIT TO VERSION CONTROL

# Database
POSTGRES_DB=pronas_pcd_prod
POSTGRES_USER=pronas_user
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# Redis
REDIS_PASSWORD=CHANGE_ME_REDIS_PASSWORD

# JWT Secrets (generate with: openssl rand -base64 32)
JWT_SECRET_KEY=CHANGE_ME_JWT_SECRET
JWT_REFRESH_SECRET_KEY=CHANGE_ME_JWT_REFRESH_SECRET

# MinIO
MINIO_ACCESS_KEY=CHANGE_ME_MINIO_ACCESS
MINIO_SECRET_KEY=CHANGE_ME_MINIO_SECRET

# Optional: External monitoring
SENTRY_DSN=
PROMETHEUS_EXTERNAL_URL=

# Backup configuration
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=pronas-pcd-backups
BACKUP_S3_REGION=us-east-1
EOF

# Production deployment script
cat > scripts/deploy-production.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Deploying PRONAS/PCD to Production"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_status "❌ Do not run this script as root" $RED
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_status "❌ .env.production file not found" $RED
    print_status "Please create .env.production from .env.production template" $YELLOW
    exit 1
fi

# Check if all required environment variables are set
print_status "🔍 Checking environment variables..." $YELLOW
if grep -q "CHANGE_ME" .env.production; then
    print_status "❌ Please update all CHANGE_ME values in .env.production" $RED
    exit 1
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

print_status "✅ Environment variables validated" $GREEN

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_status "❌ Docker is not installed" $RED
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_status "❌ Docker Compose is not installed" $RED
    exit 1
fi

print_status "✅ Docker dependencies verified" $GREEN

# Create backup of current deployment
if [ -d "backups" ]; then
    BACKUP_DIR="backups/deployment_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    print_status "📦 Creating deployment backup..." $YELLOW
    
    # Backup database
    if docker-compose -f docker-compose.prod.yml ps | grep -q pronas_pcd_db; then
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_DIR/database_backup.sql
        print_status "✅ Database backed up" $GREEN
    fi
fi

# Pull latest images
print_status "📥 Pulling latest images..." $YELLOW
docker-compose -f docker-compose.prod.yml pull

# Build custom images
print_status "🔨 Building application images..." $YELLOW
docker-compose -f docker-compose.prod.yml build --no-cache

# Run database migrations
print_status "🗄️ Running database migrations..." $YELLOW
if docker-compose -f docker-compose.prod.yml ps | grep -q pronas_pcd_backend; then
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
else
    print_status "⚠️ Backend not running, will migrate on startup" $YELLOW
fi

# Start services
print_status "🚀 Starting production services..." $YELLOW
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "⏳ Waiting for services to be healthy..." $YELLOW
sleep 30

# Health checks
print_status "🏥 Performing health checks..." $YELLOW

# Check backend health
if curl -f -s http://localhost/health > /dev/null; then
    print_status "✅ Backend is healthy" $GREEN
else
    print_status "❌ Backend health check failed" $RED
    exit 1
fi

# Check if frontend is accessible
if curl -f -s http://localhost/ > /dev/null; then
    print_status "✅ Frontend is accessible" $GREEN
else
    print_status "❌ Frontend accessibility check failed" $RED
    exit 1
fi

# Display service status
print_status "📊 Service Status:" $YELLOW
docker-compose -f docker-compose.prod.yml ps

print_status "🎉 Production deployment completed successfully!" $GREEN
print_status "🌐 Application is available at: https://pronas-pcd.gov.br" $GREEN
print_status "📊 Monitoring dashboard: https://pronas-pcd.gov.br/metrics" $GREEN

echo ""
print_status "📋 Post-deployment checklist:" $YELLOW
echo "- [ ] Verify SSL certificate is valid"
echo "- [ ] Test user authentication"
echo "- [ ] Check application logs"
echo "- [ ] Verify backup schedule"
echo "- [ ] Update DNS records if needed"
echo "- [ ] Notify stakeholders"
EOF

chmod +x scripts/deploy-production.sh

echo "✅ Scripts de produção criados!"

echo "📝 Criando scripts de monitoramento..."

# Health check script
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

# PRONAS/PCD Health Check Script
# Monitors all services and sends alerts if needed

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if services are running
check_service_health() {
    local service_name=$1
    local health_url=$2
    
    if curl -f -s --max-time 10 "$health_url" > /dev/null; then
        print_status "✅ $service_name is healthy" $GREEN
        return 0
    else
        print_status "❌ $service_name is unhealthy" $RED
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 80 ]; then
        print_status "⚠️ Disk usage is ${usage}% - consider cleanup" $YELLOW
    else
        print_status "✅ Disk usage is ${usage}%" $GREEN
    fi
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    if [ $mem_usage -gt 80 ]; then
        print_status "⚠️ Memory usage is ${mem_usage}%" $YELLOW
    else
        print_status "✅ Memory usage is ${mem_usage}%" $GREEN
    fi
}

# Main health check
echo "🏥 PRONAS/PCD Health Check - $(date)"
echo "=================================="

# Service health checks
check_service_health "Frontend" "http://localhost/"
check_service_health "Backend API" "http://localhost/health"
check_service_health "Backend Ready" "http://localhost/ready"

# System health checks
check_disk_space
check_memory

# Docker container status
print_status "🐳 Docker Container Status:" $YELLOW
docker-compose -f docker-compose.prod.yml ps

# Database connection test
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    print_status "✅ Database is accessible" $GREEN
else
    print_status "❌ Database connection failed" $RED
fi

# Redis connection test
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_status "✅ Redis is accessible" $GREEN
else
    print_status "❌ Redis connection failed" $RED
fi

echo ""
print_status "Health check completed at $(date)" $GREEN
EOF

chmod +x scripts/health-check.sh

echo "✅ Scripts de monitoramento criados!"

cd ..

echo ""
echo "🎉 LOTE 4 PARTE 1 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Nginx reverse proxy com SSL e security headers"
echo "• Docker Compose para produção com otimizações"
echo "• PostgreSQL configurado para produção"
echo "• Scripts de deploy e health check automatizados"
echo "• Configuração de segurança e monitoramento"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 4 Parte 2 (Kubernetes Manifests)"
echo "2. Configure .env.production com valores reais"
echo "3. Execute: ./scripts/deploy-production.sh"
echo ""
echo "📊 Status:"
echo "• Lote 4.1: ✅ Docker Production + Nginx"
echo "• Lote 4.2: ⏳ Kubernetes (próximo)"
echo "• Lote 4.3: ⏳ CI/CD"
echo "• Lote 4.4: ⏳ Monitoring"
echo "• Lote 4.5: ⏳ Final Scripts"
echo ""