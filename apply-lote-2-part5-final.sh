#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 2 - PARTE 5 FINAL
# PRONAS/PCD System - Database Setup (Alembic + Seeds + Testes)
# Execute na raiz do projeto após aplicar todas as partes anteriores

set -e

echo "🚀 LOTE 2 PARTE 5 FINAL: Database Setup + Testes"
echo "================================================="

# Verificar se backend existe
if [ ! -d "backend" ]; then
    echo "❌ Diretório backend não encontrado. Execute Lotes anteriores primeiro."
    exit 1
fi

cd backend

echo "📝 Configurando Alembic..."

# alembic.ini
cat > alembic.ini << 'EOF'
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format (uses % formatting)
# version_num = %(year)d%(month)02d%(day)02d_%(hour)02d%(minute)02d

# include symbol indicates how the migration
# includes another
# include_symbol = +

# placeholder string for revision id
# revision_id = ${revision}

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# alembic/env.py
cat > alembic/env.py << 'EOF'
"""
Alembic Environment Configuration
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Add the app directory to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config.settings import get_settings
from app.adapters.database.models.base import Base

# Import all models to ensure they're registered
from app.adapters.database.models.user import UserModel
from app.adapters.database.models.institution import InstitutionModel
from app.adapters.database.models.project import ProjectModel
from app.adapters.database.models.document import DocumentModel
from app.adapters.database.models.audit_log import AuditLogModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get database URL from settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
EOF

# alembic/script.py.mako
cat > alembic/script.py.mako << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
EOF

echo "✅ Alembic configurado!"

echo "📝 Criando Scripts de Seed..."

# scripts/seed_data.py
cat > scripts/seed_data.py << 'EOF'
"""
Seed Data Script
Popular banco com dados iniciais para desenvolvimento e testes
"""

import asyncio
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config.settings import get_settings
from app.adapters.database.session import get_async_session
from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.adapters.database.repositories.institution_repository import InstitutionRepositoryImpl
from app.adapters.database.repositories.project_repository import ProjectRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus
from app.domain.entities.institution import InstitutionType, InstitutionStatus
from app.domain.entities.project import ProjectType, ProjectStatus

settings = get_settings()


async def create_admin_user():
    """Criar usuário administrador padrão"""
    async with get_async_session() as session:
        user_repo = UserRepositoryImpl(session)
        
        # Verificar se já existe
        admin_email = "admin@pronas-pcd.gov.br"
        existing_admin = await user_repo.get_by_email(admin_email)
        
        if not existing_admin:
            print("📝 Criando usuário administrador...")
            
            auth_service = AuthService(user_repo, None)
            admin_data = {
                "email": admin_email,
                "full_name": "Administrador do Sistema",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "is_active": True,
                "institution_id": None,
                "hashed_password": auth_service.hash_password("admin123456"),
                "created_at": datetime.utcnow(),
                "consent_given": True,
                "consent_date": datetime.utcnow(),
            }
            
            admin_user = await user_repo.create(admin_data)
            print(f"✅ Administrador criado: {admin_user.email}")
        else:
            print("ℹ️  Usuário administrador já existe")


async def create_sample_institution():
    """Criar instituição de exemplo"""
    async with get_async_session() as session:
        institution_repo = InstitutionRepositoryImpl(session)
        
        # Verificar se já existe
        sample_cnpj = "12345678000195"
        existing = await institution_repo.get_by_cnpj(sample_cnpj)
        
        if not existing:
            print("📝 Criando instituição de exemplo...")
            
            institution_data = {
                "name": "Hospital Exemplo PRONAS/PCD",
                "cnpj": sample_cnpj,
                "type": InstitutionType.HOSPITAL,
                "status": InstitutionStatus.ACTIVE,
                "address": "Rua Exemplo, 123",
                "city": "Brasília",
                "state": "DF",
                "zip_code": "70000000",
                "phone": "61999999999",
                "email": "contato@hospital-exemplo.org.br",
                "website": "https://www.hospital-exemplo.org.br",
                "legal_representative_name": "Dr. João Exemplo",
                "legal_representative_cpf": "12345678901",
                "legal_representative_email": "joao@hospital-exemplo.org.br",
                "pronas_registration_number": "PRONAS2024001",
                "pronas_certification_date": datetime.utcnow(),
                "created_by": 1,  # Admin user
                "created_at": datetime.utcnow(),
                "data_processing_consent": True,
                "consent_date": datetime.utcnow(),
            }
            
            institution = await institution_repo.create(institution_data)
            print(f"✅ Instituição criada: {institution.name}")
            return institution.id
        else:
            print("ℹ️  Instituição de exemplo já existe")
            return existing.id


async def create_sample_users(institution_id: int):
    """Criar usuários de exemplo"""
    async with get_async_session() as session:
        user_repo = UserRepositoryImpl(session)
        auth_service = AuthService(user_repo, None)
        
        sample_users = [
            {
                "email": "gestor@hospital-exemplo.org.br",
                "full_name": "Maria Gestora",
                "role": UserRole.GESTOR,
                "institution_id": institution_id,
            },
            {
                "email": "auditor@pronas-pcd.gov.br",
                "full_name": "Carlos Auditor",
                "role": UserRole.AUDITOR,
                "institution_id": None,
            },
            {
                "email": "operador@hospital-exemplo.org.br",
                "full_name": "Ana Operadora",
                "role": UserRole.OPERADOR,
                "institution_id": institution_id,
            }
        ]
        
        for user_data in sample_users:
            existing = await user_repo.get_by_email(user_data["email"])
            if not existing:
                print(f"📝 Criando usuário: {user_data['full_name']}")
                
                full_user_data = {
                    **user_data,
                    "status": UserStatus.ACTIVE,
                    "is_active": True,
                    "hashed_password": auth_service.hash_password("password123"),
                    "created_at": datetime.utcnow(),
                    "consent_given": True,
                    "consent_date": datetime.utcnow(),
                }
                
                user = await user_repo.create(full_user_data)
                print(f"✅ Usuário criado: {user.email}")
            else:
                print(f"ℹ️  Usuário já existe: {user_data['email']}")


async def create_sample_project(institution_id: int, creator_user_id: int):
    """Criar projeto de exemplo"""
    async with get_async_session() as session:
        project_repo = ProjectRepositoryImpl(session)
        
        # Verificar se já existe projeto
        projects = await project_repo.get_by_institution(institution_id)
        if not projects:
            print("📝 Criando projeto de exemplo...")
            
            project_data = {
                "title": "Projeto de Reabilitação Neurológica Pediátrica",
                "description": "Projeto focado na reabilitação de crianças com deficiências neurológicas através de terapias inovadoras e equipamentos especializados.",
                "type": ProjectType.ASSISTENCIAL,
                "status": ProjectStatus.DRAFT,
                "institution_id": institution_id,
                "start_date": date(2024, 1, 1),
                "end_date": date(2025, 12, 31),
                "total_budget": Decimal("500000.00"),
                "pronas_funding": Decimal("350000.00"),
                "own_funding": Decimal("150000.00"),
                "other_funding": Decimal("0.00"),
                "target_population": "Crianças de 0 a 17 anos com deficiências neurológicas",
                "expected_beneficiaries": 200,
                "objectives": "Melhorar a qualidade de vida e autonomia de crianças com deficiências neurológicas através de tratamentos especializados.",
                "methodology": "Terapias multidisciplinares incluindo fisioterapia, terapia ocupacional, fonoaudiologia e psicologia.",
                "technical_manager_name": "Dra. Patricia Especialista",
                "technical_manager_cpf": "98765432100",
                "technical_manager_email": "patricia@hospital-exemplo.org.br",
                "created_by": creator_user_id,
                "created_at": datetime.utcnow(),
            }
            
            project = await project_repo.create(project_data)
            print(f"✅ Projeto criado: {project.title}")
        else:
            print("ℹ️  Projeto de exemplo já existe")


async def main():
    """Script principal de seed"""
    print("🌱 Iniciando seed do banco de dados...")
    print(f"🔗 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    
    try:
        # 1. Criar admin
        await create_admin_user()
        
        # 2. Criar instituição de exemplo
        institution_id = await create_sample_institution()
        
        # 3. Criar usuários de exemplo
        await create_sample_users(institution_id)
        
        # 4. Criar projeto de exemplo
        await create_sample_project(institution_id, 2)  # Gestor user ID
        
        print("")
        print("🎉 Seed completo!")
        print("=" * 50)
        print("Usuários criados:")
        print("• admin@pronas-pcd.gov.br (senha: admin123456)")
        print("• gestor@hospital-exemplo.org.br (senha: password123)")
        print("• auditor@pronas-pcd.gov.br (senha: password123)")
        print("• operador@hospital-exemplo.org.br (senha: password123)")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro durante seed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
EOF

echo "✅ Script de Seed criado!"

echo "📝 Criando Testes Básicos..."

# tests/conftest.py
cat > tests/conftest.py << 'EOF'
"""
Pytest Configuration
Configuração global para testes
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.adapters.database.models.base import Base
from app.adapters.database.session import get_db_session
from app.core.config.settings import get_settings

# Override settings for testing
@pytest.fixture(scope="session")
def settings():
    """Override settings for tests"""
    import os
    os.environ["POSTGRES_DB"] = "pronas_pcd_test"
    os.environ["ENVIRONMENT"] = "test"
    return get_settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine(settings):
    """Create test database engine"""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    
    # Override dependency
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()
EOF

# tests/test_auth.py
cat > tests/test_auth.py << 'EOF'
"""
Authentication Tests
Testes para endpoints de autenticação
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Criar usuário de teste"""
    user_repo = UserRepositoryImpl(db_session)
    auth_service = AuthService(user_repo, None)
    
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": UserRole.OPERADOR,
        "status": UserStatus.ACTIVE,
        "is_active": True,
        "institution_id": None,
        "hashed_password": auth_service.hash_password("password123"),
        "consent_given": True,
    }
    
    return await user_repo.create(user_data)


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Teste de login bem-sucedido"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Teste de login com credenciais inválidas"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Email ou senha incorretos" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Teste de login com usuário inexistente"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Teste para obter usuário atual"""
    # Primeiro fazer login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Obter usuário atual
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Teste com token inválido"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
EOF

# tests/test_users.py
cat > tests/test_users.py << 'EOF'
"""
Users Tests
Testes para endpoints de usuários
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Criar usuário admin de teste"""
    user_repo = UserRepositoryImpl(db_session)
    auth_service = AuthService(user_repo, None)
    
    user_data = {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE,
        "is_active": True,
        "institution_id": None,
        "hashed_password": auth_service.hash_password("admin123"),
        "consent_given": True,
    }
    
    return await user_repo.create(user_data)


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user):
    """Obter token do admin"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_user_as_admin(client: AsyncClient, admin_token):
    """Teste de criação de usuário pelo admin"""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "operador",
            "password": "Password123!",
            "consent_given": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "operador"


@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, admin_token):
    """Teste de listagem de usuários pelo admin"""
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_create_user_invalid_password(client: AsyncClient, admin_token):
    """Teste de criação com senha inválida"""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "invalid@example.com",
            "full_name": "Invalid User",
            "role": "operador",
            "password": "weak",  # Senha muito fraca
            "consent_given": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 422  # Validation error
EOF

echo "✅ Testes básicos criados!"

echo "📝 Atualizando scripts principais..."

# Atualizar scripts/setup.sh para incluir migrações
cat >> scripts/setup.sh << 'EOF'

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
EOF

# Atualizar scripts/migrate.sh
cat > scripts/migrate.sh << 'EOF'
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
EOF

# Atualizar scripts/seed.sh
cat > scripts/seed.sh << 'EOF'
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
EOF

# Dar permissões aos scripts
chmod +x scripts/*.sh

cd ..

echo ""
echo "🎉 LOTE 2 COMPLETO - BACKEND FINALIZADO!"
echo "========================================"
echo ""
echo "📋 RESUMO COMPLETO DO BACKEND:"
echo "• ✅ Clean Architecture com Domain, Adapters e API Layers"
echo "• ✅ FastAPI com autenticação JWT e RBAC"
echo "• ✅ SQLAlchemy 2.0 com models assíncronos"
echo "• ✅ Alembic para migrações de banco"
echo "• ✅ Redis para cache e sessões"
echo "• ✅ Pydantic Schemas com validações avançadas"
echo "• ✅ Sistema de auditoria LGPD-compliant"
echo "• ✅ Scripts de seed com dados de exemplo"
echo "• ✅ Testes unitários com Pytest"
echo "• ✅ Observabilidade (Prometheus, health checks)"
echo ""
echo "🚀 COMO EXECUTAR:"
echo "1. cd backend && source venv/bin/activate"
echo "2. pip install -r requirements-dev.txt"
echo "3. alembic revision --autogenerate -m 'Initial migration'"
echo "4. alembic upgrade head"
echo "5. python scripts/seed_data.py"
echo "6. uvicorn app.main:app --reload"
echo ""
echo "🧪 PARA TESTAR:"
echo "pytest tests/ -v --cov=app"
echo ""
echo "📊 STATUS FINAL:"
echo "• ✅ Lote 1: Estrutura monorepo"
echo "• ✅ Lote 2: Backend FastAPI completo (119 arquivos)"
echo "• ⏳ Lote 3: Frontend Next.js (próximo)"
echo "• ⏳ Lote 4: DevOps completo"
echo ""
echo "🔐 USUÁRIOS DE TESTE:"
echo "• admin@pronas-pcd.gov.br (senha: admin123456)"
echo "• gestor@hospital-exemplo.org.br (senha: password123)"
echo "• auditor@pronas-pcd.gov.br (senha: password123)"
echo ""