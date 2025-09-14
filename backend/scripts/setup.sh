
# Setup das migrações do banco
if [ -f "backend/alembic.ini" ]; then
    echo "🗄️  Configurando banco de dados..."
    cd backend
    source venv/bin/activate
    
    # Verificar se há migrações
    if [ ! -f "alembic/versions/*.py" ]; then
        echo "Criando migração inicial..."
        alembic revision --autogenerate -m "Initial migration"
    fi
    
    echo "✅ Banco de dados configurado"
    cd ..
fi
