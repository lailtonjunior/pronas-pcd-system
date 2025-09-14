#!/bin/bash

set -e

echo "🗄️  Executando migrações do banco de dados..."

# Verificar se o ambiente backend está configurado
if [ ! -d "backend/venv" ]; then
    echo "❌ Ambiente Python não encontrado. Execute 'make setup' primeiro."
    exit 1
fi

cd backend
source venv/bin/activate

# Verificar se Alembic está configurado
if [ -f "alembic.ini" ]; then
    echo "Executando migrações..."
    alembic upgrade head
    echo "✅ Migrações executadas com sucesso"
else
    echo "❌ Alembic não configurado"
    exit 1
fi

cd ..
