#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 2 - PARTE 3
# PRONAS/PCD System - Adapters Layer (SQLAlchemy + Redis + MinIO)
# Execute na raiz do projeto após aplicar as Partes 1 e 2

set -e

echo "🚀 LOTE 2 PARTE 3: Implementando Adapters Layer"
echo "==============================================="

# Verificar se backend existe
if [ ! -d "backend" ]; then
    echo "❌ Diretório backend não encontrado. Execute Lotes anteriores primeiro."
    exit 1
fi

cd backend

echo "📝 Criando SQLAlchemy Models..."

# app/adapters/database/models/base.py
cat > app/adapters/database/models/base.py << 'EOF'
"""
SQLAlchemy Base Model
Modelo base para todas as tabelas
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()


class BaseModel(Base):
    """Modelo base com campos comuns"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        # Gerar nome da tabela automaticamente
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def dict(self):
        """Converter para dicionário"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
EOF

# app/adapters/database/models/user.py
cat > app/adapters/database/models/user.py << 'EOF'
"""
User SQLAlchemy Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.user import UserRole, UserStatus


class UserModel(BaseModel):
    """Modelo SQLAlchemy para usuários"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Enum fields
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.OPERADOR)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Institution relationship
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    institution = relationship("InstitutionModel", back_populates="users")
    
    # LGPD fields
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True))
    data_retention_date = Column(DateTime(timezone=True))
    
    # Relationships
    created_projects = relationship("ProjectModel", back_populates="creator")
    uploaded_documents = relationship("DocumentModel", back_populates="uploader")
    audit_logs = relationship("AuditLogModel", back_populates="user")
EOF

# app/adapters/database/models/institution.py
cat > app/adapters/database/models/institution.py << 'EOF'
"""
Institution SQLAlchemy Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.institution import InstitutionType, InstitutionStatus


class InstitutionModel(BaseModel):
    """Modelo SQLAlchemy para instituições"""
    __tablename__ = "institutions"
    
    name = Column(String(255), nullable=False, index=True)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    
    # Enum fields
    type = Column(SQLEnum(InstitutionType), nullable=False)
    status = Column(SQLEnum(InstitutionStatus), nullable=False, default=InstitutionStatus.PENDING_APPROVAL)
    
    # Address
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    
    # Contact
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    
    # Legal representative
    legal_representative_name = Column(String(255), nullable=False)
    legal_representative_cpf = Column(String(11), nullable=False)
    legal_representative_email = Column(String(255), nullable=False)
    
    # PRONAS/PCD data
    pronas_registration_number = Column(String(50), nullable=True, unique=True)
    pronas_certification_date = Column(DateTime(timezone=True))
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # LGPD
    data_processing_consent = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True))
    
    # Relationships
    users = relationship("UserModel", back_populates="institution")
    projects = relationship("ProjectModel", back_populates="institution")
    documents = relationship("DocumentModel", back_populates="institution")
EOF

# app/adapters/database/models/project.py
cat > app/adapters/database/models/project.py << 'EOF'
"""
Project SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Numeric, Date
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.project import ProjectStatus, ProjectType


class ProjectModel(BaseModel):
    """Modelo SQLAlchemy para projetos"""
    __tablename__ = "projects"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Enum fields
    type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    
    # Relationships
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    institution = relationship("InstitutionModel", back_populates="projects")
    
    # Schedule
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Budget
    total_budget = Column(Numeric(15, 2), nullable=False)
    pronas_funding = Column(Numeric(15, 2), nullable=False)
    own_funding = Column(Numeric(15, 2), nullable=False)
    other_funding = Column(Numeric(15, 2), nullable=True)
    
    # Technical details
    target_population = Column(String(500), nullable=False)
    expected_beneficiaries = Column(Integer, nullable=False)
    objectives = Column(Text, nullable=False)
    methodology = Column(Text, nullable=False)
    
    # Documentation URLs
    technical_proposal_url = Column(String(500), nullable=True)
    budget_detailed_url = Column(String(500), nullable=True)
    
    # Technical manager
    technical_manager_name = Column(String(255), nullable=False)
    technical_manager_cpf = Column(String(11), nullable=False)
    technical_manager_email = Column(String(255), nullable=False)
    
    # Workflow
    submitted_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("UserModel", back_populates="created_projects", foreign_keys=[created_by])
    reviewer = relationship("UserModel", foreign_keys=[reviewer_id])
    documents = relationship("DocumentModel", back_populates="project")
EOF

# app/adapters/database/models/document.py
cat > app/adapters/database/models/document.py << 'EOF'
"""
Document SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.document import DocumentType, DocumentStatus


class DocumentModel(BaseModel):
    """Modelo SQLAlchemy para documentos"""
    __tablename__ = "documents"
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Classification
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("ProjectModel", back_populates="documents")
    
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    institution = relationship("InstitutionModel", back_populates="documents")
    
    # Metadata
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # File integrity
    file_hash = Column(String(64), nullable=False, index=True)
    
    # Audit
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text, nullable=True)
    
    # LGPD - Personal data
    contains_personal_data = Column(Boolean, default=False, nullable=False)
    data_classification = Column(String(20), default="internal", nullable=False)
    retention_period_months = Column(Integer, nullable=True)
    
    # Relationships
    uploader = relationship("UserModel", back_populates="uploaded_documents", foreign_keys=[uploaded_by])
    reviewer = relationship("UserModel", foreign_keys=[reviewed_by])
EOF

# app/adapters/database/models/audit_log.py
cat > app/adapters/database/models/audit_log.py << 'EOF'
"""
Audit Log SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.audit_log import AuditAction, AuditResource


class AuditLogModel(BaseModel):
    """Modelo SQLAlchemy para logs de auditoria - IMUTÁVEL"""
    __tablename__ = "audit_logs"
    
    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource = Column(SQLEnum(AuditResource), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # User details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(50), nullable=False)
    
    # Request context
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(Text, nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Operation details
    description = Column(Text, nullable=False)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Result
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # LGPD
    data_sensitivity = Column(String(20), default="internal", nullable=False, index=True)
    
    # Immutable timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="audit_logs")
    
    # Override created_at/updated_at behavior for immutability
    def __init__(self, **kwargs):
        # Remove created_at and updated_at from kwargs to prevent override
        kwargs.pop('created_at', None)
        kwargs.pop('updated_at', None)
        super().__init__(**kwargs)
EOF

echo "✅ SQLAlchemy Models criados!"

echo "📝 Criando Database Session e Connection..."

# app/adapters/database/session.py
cat > app/adapters/database/session.py << 'EOF'
"""
Database Session Management
Gerenciamento de sessões assíncronas com SQLAlchemy
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config.settings import get_settings

settings = get_settings()

# Criar engine assíncrono
engine = create_async_engine(
    settings.database_url,
    echo=settings.api_debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    poolclass=NullPool if settings.environment == "test" else None,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager para obter sessão assíncrona"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection para FastAPI"""
    async with get_async_session() as session:
        yield session
EOF

echo "✅ Database Session criado!"

echo "📝 Criando Repository Implementations..."

# app/adapters/database/repositories/user_repository.py
cat > app/adapters/database/repositories/user_repository.py << 'EOF'
"""
User Repository Implementation
Implementação do repositório de usuários com SQLAlchemy
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.domain.repositories.user import UserRepository
from app.domain.entities.user import User, UserRole, UserStatus
from app.adapters.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """Implementação do repositório de usuários"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Converter SQLAlchemy model para domain entity"""
        if not model:
            return None
        
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            role=model.role,
            status=model.status,
            is_active=model.is_active,
            institution_id=model.institution_id,
            hashed_password=model.hashed_password,
            last_login=model.last_login,
            created_at=model.created_at,
            updated_at=model.updated_at,
            consent_given=model.consent_given,
            consent_date=model.consent_date,
            data_retention_date=model.data_retention_date,
        )
    
    async def create(self, entity_data: Dict[str, Any]) -> User:
        """Criar novo usuário"""
        model = UserModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Buscar usuário por ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuários por papel/role"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.role == role)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_institution(self, institution_id: int) -> List[User]:
        """Buscar usuários de uma instituição"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.institution_id == institution_id)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_active_users(self) -> List[User]:
        """Buscar apenas usuários ativos"""
        result = await self.session.execute(
            select(UserModel).where(
                and_(UserModel.is_active == True, UserModel.status == UserStatus.ACTIVE)
            )
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update_last_login(self, user_id: int) -> None:
        """Atualizar último login do usuário"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.session.commit()
    
    async def change_password(self, user_id: int, new_hashed_password: str) -> bool:
        """Alterar senha do usuário"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_status(self, user_id: int, status: UserStatus) -> bool:
        """Atualizar status do usuário"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(status=status)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Buscar todos os usuários com paginação"""
        query = select(UserModel).offset(skip).limit(limit)
        
        if filters:
            if "role" in filters:
                query = query.where(UserModel.role == filters["role"])
            if "status" in filters:
                query = query.where(UserModel.status == filters["status"])
            if "is_active" in filters:
                query = query.where(UserModel.is_active == filters["is_active"])
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Atualizar usuário"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .returning(UserModel)
        )
        await self.session.commit()
        
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def delete(self, user_id: int) -> bool:
        """Excluir usuário (soft delete - marcar como inativo)"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False, status=UserStatus.INACTIVE)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar usuários com filtros opcionais"""
        from sqlalchemy import func
        
        query = select(func.count(UserModel.id))
        
        if filters:
            if "role" in filters:
                query = query.where(UserModel.role == filters["role"])
            if "status" in filters:
                query = query.where(UserModel.status == filters["status"])
            if "is_active" in filters:
                query = query.where(UserModel.is_active == filters["is_active"])
        
        result = await self.session.execute(query)
        return result.scalar()
EOF

echo "✅ Repository Implementation criada!"

echo "📝 Criando Redis Client..."

# app/adapters/external/cache/redis_client.py
cat > app/adapters/external/cache/redis_client.py << 'EOF'
"""
Redis Client Adapter
Cliente Redis para cache e sessões
"""

import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.core.config.settings import get_settings

settings = get_settings()

# Global Redis connection
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Obter cliente Redis (singleton)"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
        )
    
    return _redis_client


async def close_redis_client():
    """Fechar conexão Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


class RedisCache:
    """Wrapper para operações de cache Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Definir valor no cache"""
        if not isinstance(value, str):
            value = json.dumps(value, default=str)
        
        if expire:
            return await self.redis.setex(key, expire, value)
        else:
            return await self.redis.set(key, value)
    
    async def delete(self, key: str) -> bool:
        """Remover chave do cache"""
        return await self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Verificar se chave existe"""
        return await self.redis.exists(key) > 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Incrementar valor numérico"""
        return await self.redis.incr(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Definir expiração para chave"""
        return await self.redis.expire(key, seconds)
EOF

echo "✅ Redis Client criado!"

cd ..

echo ""
echo "🎉 LOTE 2 PARTE 3 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• SQLAlchemy Models para todas as entidades (User, Institution, Project, Document, AuditLog)"
echo "• Base Model com campos comuns e configuração automática"
echo "• Database Session management com connection pooling"
echo "• User Repository Implementation completa"
echo "• Redis Client adapter para cache e sessões"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 2 Parte 4 (API Layer - FastAPI Routers + Schemas)"
echo "2. Aguarde Lote 2 Parte 5 (Alembic Migrations + Seeds)"
echo "3. Então execute testes com: cd backend && pytest"
echo ""
echo "📊 Status atual:"
echo "• Lote 1: ✅ Estrutura monorepo"
echo "• Lote 2.1: ✅ Configuração Python"
echo "• Lote 2.2: ✅ Domain Layer"
echo "• Lote 2.3: ✅ Adapters Layer (SQLAlchemy, Redis)"
echo "• Lote 2.4: ⏳ API Layer (próximo)"
echo "• Lote 2.5: ⏳ Database Migrations"
echo ""
echo "🔧 Para testar a configuração atual:"
echo "cd backend"
echo "python -c \"from app.core.config.settings import get_settings; print('✅ Settings OK')\" "
echo "python -c \"from app.adapters.database.models.user import UserModel; print('✅ Models OK')\""
echo ""