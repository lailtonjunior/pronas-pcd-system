#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 2 - PARTE 1
# PRONAS/PCD System - Configuração Base do Backend
# Execute na raiz do projeto após aplicar o Lote 1

set -e

echo "🚀 LOTE 2 PARTE 1: Aplicando Configuração Base do Backend"
echo "======================================================="

# Verificar se Lote 1 foi aplicado
if [ ! -d "backend" ]; then
    echo "❌ Estrutura do Lote 1 não encontrada. Execute o Lote 1 primeiro."
    exit 1
fi

cd backend

echo "📝 Criando arquivos de configuração do Python..."

# requirements.txt
cat > requirements.txt << 'EOF'
# FastAPI and Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Redis & Caching
redis==5.0.1
hiredis==2.2.3

# Storage & Files
minio==7.2.0
python-magic==0.4.27

# Monitoring & Observability
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-sqlalchemy==0.42b0

# Data Validation & Serialization
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
structlog==23.2.0
rich==13.7.0

# HTTP Client
httpx==0.25.2
EOF

# requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
# Include production requirements
-r requirements.txt

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-xdist==3.5.0
httpx==0.25.2

# Code Quality
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0

# Development Tools
watchfiles==0.21.0
python-dotenv==1.0.0
ipython==8.17.2
EOF

# .python-version
echo "3.11.6" > .python-version

# pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_untyped_defs = true
warn_unused_ignores = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["tests"]
asyncio_mode = "auto"
EOF

echo "📝 Criando Dockerfiles..."

# Dockerfile para produção
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
EOF

# Dockerfile para desenvolvimento
cat > Dockerfile.dev << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

echo "📝 Criando estrutura inicial da aplicação..."

mkdir -p app/api/v1/endpoints app/core app/domain/entities app/adapters/database
touch app/__init__.py
find app -type d -exec touch {}/__init__.py \;

cd ..

echo ""
echo "🎉 LOTE 2 - PARTE 1 APLICADO COM SUCESSO!"
echo "=========================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Arquivos de configuração Python (requirements.txt, pyproject.toml)"
echo "• Dockerfiles para produção e desenvolvimento"
echo "• Estrutura básica da aplicação FastAPI"
echo ""
echo "⚠️  PRÓXIMOS PASSOS: Execute os próximos scripts do Lote 2."
