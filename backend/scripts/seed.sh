#!/bin/bash

set -e

echo "🌱 Populando banco de dados com dados iniciais..."

# Verificar se o ambiente backend está configurado
if [ ! -d "backend/venv" ]; then
    echo "❌ Ambiente Python não encontrado. Execute 'make setup' primeiro."
    exit 1
fi

cd backend
source venv/bin/activate

# Executar script de seed
if [ -f "scripts/seed_data.py" ]; then
    echo "Executando seed..."
    python scripts/seed_data.py
    echo "✅ Dados iniciais inseridos com sucesso"
else
    echo "❌ Script de seed não encontrado"
    exit 1
fi

cd ..
