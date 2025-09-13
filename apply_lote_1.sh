#!/bin/bash

# SCRIPT COMPLETO PARA APLICAÇÃO DO LOTE 1
# PRONAS/PCD System - Configuração Base
# Execute este script na raiz do projeto

set -e

echo "🚀 LOTE 1: Aplicando Configuração Base do PRONAS/PCD System"
echo "============================================================="

# 1. Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."

# Diretórios raiz
mkdir -p scripts .github/{workflows,ISSUE_TEMPLATE} backups

# Backend
mkdir -p backend/{app/{api/v1/endpoints,core/{security,config,exceptions,middleware},domain/{entities,repositories,services},adapters/{database/{models,repositories},external/{storage,cache,notifications}},schemas/{requests,responses}},alembic/versions,tests/{unit/{domain,api},integration/{database,api},fixtures},scripts}

# Frontend  
mkdir -p frontend/{src/{app/'(auth)'/{login,register},app/'(dashboard)'/{dashboard,institutions,projects,documents,audit,profile},app/api/{auth,upload},components/{ui,forms,layout,dashboard},lib/{api,auth,utils,hooks,schemas},styles},public/images,tests/{unit,integration,e2e}}

# Infra
mkdir -p infra/{docker/{nginx,postgres},monitoring/{prometheus,grafana/{dashboards,provisioning/{datasources,dashboards}}},k8s/{base,apps,services,ingress}}

# Docs
mkdir -p docs/{architecture,api,deployment,security,operations}

echo "✅ Estrutura de diretórios criada"

# 2. Verificação de Git
if [ ! -d ".git" ]; then
    echo "📝 Inicializando repositório Git..."
    git init
    git branch -m main
fi

# 3. Criar .gitignore
echo "📝 Criando .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.env.local
.env.production
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.dmypy.json
dmypy.json

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.next/
out/
build
dist
*.tsbuildinfo
next-env.d.ts

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
media/

# Secrets
secrets/
*.pem
*.key
*.crt

# Backups
backups/
EOF

echo "✅ .gitignore criado"

# 4. Criar arquivo .env.example
echo "📝 Criando .env.example..."
cat > .env.example << 'EOF'
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pronas_pcd_dev
POSTGRES_USER=pronas_user
POSTGRES_PASSWORD=your_secure_password_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY=your_256_bit_secret_key_here
JWT_REFRESH_SECRET_KEY=your_256_bit_refresh_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
API_RELOAD=true

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pronas-pcd-documents
MINIO_SECURE=false

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM=noreply@pronas-pcd.gov.br

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=admin123

# Security
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
EOF

echo "✅ .env.example criado"

# 5. Criar .env.production.example
echo "📝 Criando .env.production.example..."
cat > .env.production.example << 'EOF'
# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=pronas_pcd_prod
POSTGRES_USER=pronas_user
POSTGRES_PASSWORD=${DATABASE_PASSWORD}

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_RELOAD=false

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://api.pronas-pcd.gov.br
NEXT_PUBLIC_APP_URL=https://pronas-pcd.gov.br

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
MINIO_BUCKET_NAME=pronas-pcd-documents
MINIO_SECURE=true

# Email Configuration
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=587
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
SMTP_FROM=noreply@pronas-pcd.gov.br

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

# Security
CORS_ORIGINS=https://pronas-pcd.gov.br
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
EOF

echo "✅ .env.production.example criado"

# 6. Criar Makefile
echo "📝 Criando Makefile..."
cat > Makefile << 'EOF'
.PHONY: help setup dev test lint build clean docker-build docker-up docker-down migrate seed backup

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Setup
setup: ## Initial project setup
	@echo "Setting up PRONAS/PCD System..."
	@./scripts/setup.sh

dev: ## Start development environment
	@echo "Starting development environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-logs: ## Show development logs
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Testing
test: ## Run all tests
	@echo "Running tests..."
	@./scripts/test.sh

test-backend: ## Run backend tests only
	@echo "Running backend tests..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests only
	@echo "Running frontend tests..."
	@cd frontend && npm run test

test-e2e: ## Run end-to-end tests
	@echo "Running E2E tests..."
	@cd frontend && npm run test:e2e

# Code Quality
lint: ## Run linting for all projects
	@echo "Running linting..."
	@./scripts/lint.sh

lint-backend: ## Run backend linting
	@cd backend && python -m black . && python -m isort . && python -m flake8 .

lint-frontend: ## Run frontend linting
	@cd frontend && npm run lint && npm run format

# Build
build: ## Build all services
	@echo "Building all services..."
	@./scripts/build.sh

build-backend: ## Build backend image
	@docker build -f backend/Dockerfile -t pronas-pcd-backend:latest ./backend

build-frontend: ## Build frontend image
	@docker build -f frontend/Dockerfile -t pronas-pcd-frontend:latest ./frontend

# Docker Management
docker-up: ## Start all services with Docker Compose
	@docker-compose up -d

docker-up-prod: ## Start production services
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

docker-down: ## Stop all services
	@docker-compose down

docker-clean: ## Remove all containers, networks, and volumes
	@docker-compose down -v --remove-orphans
	@docker system prune -f

# Database Operations
migrate: ## Run database migrations
	@echo "Running database migrations..."
	@./scripts/migrate.sh

migrate-create: ## Create new migration
	@echo "Creating new migration..."
	@cd backend && alembic revision --autogenerate -m "$(name)"

seed: ## Seed database with initial data
	@echo "Seeding database..."
	@./scripts/seed.sh

backup: ## Create database backup
	@echo "Creating database backup..."
	@./scripts/backup.sh

# Production
deploy: ## Deploy to production
	@echo "Deploying to production..."
	@./scripts/deploy.sh

# Clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@cd backend && rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true
EOF

echo "✅ Makefile criado"

echo ""
echo "🎉 LOTE 1 APLICADO COM SUCESSO!"
echo "================================"
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Estrutura completa de diretórios (281 arquivos planejados)"
echo "• Arquivos de configuração de ambiente (.env.example, .env.production.example)"
echo "• .gitignore configurado para Python/Node.js"
echo "• Makefile com comandos de automação"
echo "• Estrutura para 119 arquivos de backend"
echo "• Estrutura para 90 arquivos de frontend"
echo "• Estrutura para 26 arquivos de infraestrutura"
echo "• Estrutura para 20 arquivos de documentação"
echo "• Diretórios para scripts e CI/CD"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde o Lote 2 (Backend - Clean Architecture)"
echo "2. Aguarde o Lote 3 (Frontend - Next.js + TypeScript)"
echo "3. Aguarde o Lote 4 (DevOps - Docker + Scripts)"
echo "4. Depois execute: chmod +x scripts/*.sh"
echo "5. Execute: make help (para ver comandos disponíveis)"
echo ""
echo "📊 Status atual:"
echo "• Lote 1: ✅ CONCLUÍDO - Estrutura base criada"
echo "• Lote 2: ⏳ PENDENTE - Backend Clean Architecture"
echo "• Lote 3: ⏳ PENDENTE - Frontend Next.js"  
echo "• Lote 4: ⏳ PENDENTE - DevOps e Scripts"
echo ""
echo "🔗 Para executar este lote:"
echo "1. Salve este conteúdo como 'apply_lote_1.sh'"
echo "2. Execute: chmod +x apply_lote_1.sh"
echo "3. Execute: ./apply_lote_1.sh"
echo ""