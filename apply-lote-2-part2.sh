#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 2 - PARTE 2
# PRONAS/PCD System - Domain Layer Completo
# Execute na raiz do projeto após aplicar o Lote 2 Parte 1

set -e

echo "🚀 LOTE 2 PARTE 2: Implementando Domain Layer Completo"
echo "======================================================"

# Verificar se backend existe
if [ ! -d "backend" ]; then
    echo "❌ Diretório backend não encontrado. Execute Lotes 1 e 2.1 primeiro."
    exit 1
fi

cd backend

echo "📝 Criando Domain Entities..."

# app/domain/entities/user.py
cat > app/domain/entities/user.py << 'EOF'
"""
User Entity - Domínio PRONAS/PCD
Entidade central para autenticação e autorização
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    """Papéis de usuário no sistema"""
    ADMIN = "admin"
    GESTOR = "gestor"
    AUDITOR = "auditor"
    OPERADOR = "operador"


class UserStatus(str, Enum):
    """Status do usuário"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


@dataclass
class User:
    """Entidade de usuário do domínio"""
    id: Optional[int]
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    is_active: bool
    institution_id: Optional[int]
    hashed_password: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Campos para conformidade LGPD
    consent_given: bool
    consent_date: Optional[datetime]
    data_retention_date: Optional[datetime]
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Verificar permissões do usuário"""
        # Admins têm acesso total
        if self.role == UserRole.ADMIN:
            return True
        
        # Gestores podem gerenciar sua instituição
        if self.role == UserRole.GESTOR:
            if resource == "institution" and self.institution_id:
                return action in ["read", "update"]
            if resource == "project":
                return action in ["read", "create", "update"]
            if resource == "document":
                return action in ["read", "create"]
        
        # Auditores têm acesso de leitura
        if self.role == UserRole.AUDITOR:
            return action == "read"
        
        # Operadores têm acesso limitado
        if self.role == UserRole.OPERADOR:
            if resource in ["project", "document"]:
                return action in ["read", "create"]
        
        return False
    
    def can_access_institution(self, institution_id: int) -> bool:
        """Verificar se pode acessar instituição específica"""
        if self.role == UserRole.ADMIN:
            return True
        
        if self.role in [UserRole.GESTOR, UserRole.OPERADOR]:
            return self.institution_id == institution_id
        
        if self.role == UserRole.AUDITOR:
            return True  # Auditores veem todas
        
        return False
EOF

# app/domain/entities/institution.py
cat > app/domain/entities/institution.py << 'EOF'
"""
Institution Entity - Instituições PRONAS/PCD
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class InstitutionType(str, Enum):
    """Tipos de instituição"""
    HOSPITAL = "hospital"
    CLINICA = "clinica"
    CENTRO_REABILITACAO = "centro_reabilitacao"
    APAE = "apae"
    OSC = "osc"  # Organização da Sociedade Civil
    OUTRO = "outro"


class InstitutionStatus(str, Enum):
    """Status da instituição"""
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


@dataclass
class Institution:
    """Entidade de instituição do domínio"""
    id: Optional[int]
    name: str
    cnpj: str
    type: InstitutionType
    status: InstitutionStatus
    
    # Endereço
    address: str
    city: str
    state: str
    zip_code: str
    
    # Contato
    phone: str
    email: str
    website: Optional[str]
    
    # Responsável legal
    legal_representative_name: str
    legal_representative_cpf: str
    legal_representative_email: str
    
    # Dados PRONAS/PCD
    pronas_registration_number: Optional[str]
    pronas_certification_date: Optional[datetime]
    
    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    
    # Conformidade LGPD
    data_processing_consent: bool
    consent_date: Optional[datetime]
EOF

# app/domain/entities/project.py
cat > app/domain/entities/project.py << 'EOF'
"""
Project Entity - Projetos PRONAS/PCD
"""

from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class ProjectStatus(str, Enum):
    """Status do projeto"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, Enum):
    """Tipos de projeto PRONAS/PCD"""
    ASSISTENCIAL = "assistencial"
    PESQUISA = "pesquisa"
    DESENVOLVIMENTO_TECNOLOGICO = "desenvolvimento_tecnologico"
    CAPACITACAO = "capacitacao"
    INFRAESTRUTURA = "infraestrutura"


@dataclass
class Project:
    """Entidade de projeto do domínio"""
    id: Optional[int]
    title: str
    description: str
    type: ProjectType
    status: ProjectStatus
    institution_id: int
    
    # Cronograma
    start_date: date
    end_date: date
    
    # Financeiro
    total_budget: Decimal
    pronas_funding: Decimal
    own_funding: Decimal
    other_funding: Optional[Decimal]
    
    # Técnico
    target_population: str
    expected_beneficiaries: int
    objectives: str
    methodology: str
    
    # Documentação
    technical_proposal_url: Optional[str]
    budget_detailed_url: Optional[str]
    
    # Responsável técnico
    technical_manager_name: str
    technical_manager_cpf: str
    technical_manager_email: str
    
    # Workflow
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    reviewer_id: Optional[int]
    review_notes: Optional[str]
    
    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    
    def calculate_funding_percentage(self) -> dict:
        """Calcular percentual de financiamentos"""
        total = float(self.total_budget)
        if total == 0:
            return {"pronas": 0, "own": 0, "other": 0}
        
        return {
            "pronas": (float(self.pronas_funding) / total) * 100,
            "own": (float(self.own_funding) / total) * 100,
            "other": (float(self.other_funding or 0) / total) * 100,
        }
    
    def is_editable(self) -> bool:
        """Verificar se projeto pode ser editado"""
        return self.status in [ProjectStatus.DRAFT, ProjectStatus.REJECTED]
    
    def can_be_submitted(self) -> bool:
        """Verificar se pode ser submetido"""
        return (
            self.status == ProjectStatus.DRAFT
            and self.technical_proposal_url is not None
            and self.budget_detailed_url is not None
        )
EOF

# app/domain/entities/document.py
cat > app/domain/entities/document.py << 'EOF'
"""
Document Entity - Documentos do Sistema
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class DocumentType(str, Enum):
    """Tipos de documento"""
    TECHNICAL_PROPOSAL = "technical_proposal"
    DETAILED_BUDGET = "detailed_budget"
    PROGRESS_REPORT = "progress_report"
    FINAL_REPORT = "final_report"
    CERTIFICATION = "certification"
    CONTRACT = "contract"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Status do documento"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class Document:
    """Entidade de documento do domínio"""
    id: Optional[int]
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    file_path: str
    
    # Classificação
    document_type: DocumentType
    status: DocumentStatus
    
    # Relacionamentos
    project_id: Optional[int]
    institution_id: Optional[int]
    
    # Metadados
    description: Optional[str]
    version: int
    
    # Hash para integridade
    file_hash: str
    
    # Auditoria
    uploaded_by: int
    uploaded_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    
    # LGPD - Dados sensíveis
    contains_personal_data: bool
    data_classification: str  # "public", "internal", "confidential", "restricted"
    retention_period_months: Optional[int]
    
    def get_display_size(self) -> str:
        """Obter tamanho formatado para exibição"""
        size = self.size_bytes
        
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.1f} GB"
    
    def is_editable_by_user(self, user_id: int, user_role: str) -> bool:
        """Verificar se documento pode ser editado pelo usuário"""
        # Admin pode editar todos
        if user_role == "admin":
            return True
        
        # Usuário que fez upload pode editar se status permite
        if self.uploaded_by == user_id and self.status in ["uploaded", "rejected"]:
            return True
        
        return False
EOF

# app/domain/entities/audit_log.py
cat > app/domain/entities/audit_log.py << 'EOF'
"""
Audit Log Entity - Trilha de auditoria
Conformidade LGPD - Registro de operações
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json


class AuditAction(str, Enum):
    """Ações auditáveis"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"


class AuditResource(str, Enum):
    """Recursos auditáveis"""
    USER = "user"
    INSTITUTION = "institution"
    PROJECT = "project"
    DOCUMENT = "document"
    SYSTEM = "system"
    REPORT = "report"


@dataclass
class AuditLog:
    """Entidade de log de auditoria - IMUTÁVEL após criação"""
    id: Optional[int]
    
    # Ação realizada
    action: AuditAction
    resource: AuditResource
    resource_id: Optional[int]
    
    # Usuário que executou a ação
    user_id: int
    user_email: str
    user_role: str
    
    # Contexto da requisição
    ip_address: str
    user_agent: str
    session_id: str
    
    # Detalhes da operação
    description: str
    previous_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    
    # Metadados
    success: bool
    error_message: Optional[str]
    
    # Timestamp (imutável)
    timestamp: datetime
    
    # LGPD - Classificação do dado
    data_sensitivity: str  # "public", "internal", "confidential", "restricted"
    
    def to_json(self) -> str:
        """Serializar para JSON para armazenamento"""
        return json.dumps({
            "id": self.id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_role": self.user_role,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "description": self.description,
            "previous_values": self.previous_values,
            "new_values": self.new_values,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "data_sensitivity": self.data_sensitivity,
        }, ensure_ascii=False, default=str)
EOF

echo "✅ Domain Entities criadas!"

echo "📝 Criando Domain Repositories (Interfaces)..."

# app/domain/repositories/base.py
cat > app/domain/repositories/base.py << 'EOF'
"""
Base Repository Interface
Repositório base com operações CRUD genéricas
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

EntityType = TypeVar("EntityType")
IDType = TypeVar("IDType")


class BaseRepository(ABC, Generic[EntityType, IDType]):
    """Interface base para repositórios"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> EntityType:
        """Criar nova entidade"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: IDType) -> Optional[EntityType]:
        """Buscar entidade por ID"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[EntityType]:
        """Buscar todas as entidades com paginação e filtros"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: IDType, update_data: Dict[str, Any]) -> Optional[EntityType]:
        """Atualizar entidade"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: IDType) -> bool:
        """Excluir entidade"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar entidades com filtros opcionais"""
        pass
EOF

# app/domain/repositories/user.py
cat > app/domain/repositories/user.py << 'EOF'
"""
User Repository Interface
"""

from abc import abstractmethod
from typing import Optional, List
from app.domain.repositories.base import BaseRepository
from app.domain.entities.user import User, UserRole, UserStatus


class UserRepository(BaseRepository[User, int]):
    """Interface do repositório de usuários"""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        pass
    
    @abstractmethod
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuários por papel/role"""
        pass
    
    @abstractmethod
    async def get_by_institution(self, institution_id: int) -> List[User]:
        """Buscar usuários de uma instituição"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int) -> None:
        """Atualizar último login do usuário"""
        pass
    
    @abstractmethod
    async def change_password(self, user_id: int, new_hashed_password: str) -> bool:
        """Alterar senha do usuário"""
        pass
    
    @abstractmethod
    async def update_status(self, user_id: int, status: UserStatus) -> bool:
        """Atualizar status do usuário"""
        pass
    
    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """Buscar apenas usuários ativos"""
        pass
EOF

echo "✅ Domain Repositories criadas!"

echo "📝 Criando Core Configuration..."

# app/core/config/settings.py
cat > app/core/config/settings.py << 'EOF'
"""
Configuration Settings
Configurações centralizadas com Pydantic Settings
"""

from functools import lru_cache
from typing import List, Optional, Union
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    Field,
    validator,
)


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Database Settings
    postgres_host: str = Field(env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(env="POSTGRES_DB")
    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD")
    
    # Redis Settings
    redis_host: str = Field(env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # JWT Settings
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(env="JWT_REFRESH_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=30, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # MinIO Settings
    minio_endpoint: str = Field(env="MINIO_ENDPOINT")
    minio_access_key: str = Field(env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="pronas-pcd-documents", env="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    
    # Security Settings
    cors_origins: List[AnyHttpUrl] = Field(default=[], env="CORS_ORIGINS")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    
    # Computed Properties
    @property
    def database_url(self) -> str:
        """URL de conexão com PostgreSQL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url(self) -> str:
        """URL de conexão com Redis"""
        auth_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Processar origens CORS"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Obter configurações (cached)"""
    return Settings()
EOF

# app/core/security/auth.py
cat > app/core/security/auth.py << 'EOF'
"""
Authentication and JWT Security
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any]) -> str:
    """Criar token JWT de acesso"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Criar token JWT de refresh"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.jwt_refresh_secret_key,
        algorithm=settings.jwt_algorithm
    )


def verify_jwt_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verificar e decodificar token JWT"""
    try:
        secret_key = (
            settings.jwt_secret_key
            if token_type == "access"
            else settings.jwt_refresh_secret_key
        )
        
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verificar se é o tipo correto de token
        if payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash da senha"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return pwd_context.verify(plain_password, hashed_password)
EOF

echo "✅ Core Configuration criada!"

cd ..

echo ""
echo "🎉 LOTE 2 PARTE 2 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• 5 Domain Entities completas (User, Institution, Project, Document, AuditLog)"
echo "• Base Repository e User Repository interfaces"
echo "• Core Configuration (Settings, JWT Auth)"
echo "• Estrutura Clean Architecture com separação clara de responsabilidades"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 2 Parte 3 (Adapters Layer - SQLAlchemy Models)"
echo "2. Aguarde Lote 2 Parte 4 (API Layer - FastAPI Routers)"
echo "3. Aguarde Lote 2 Parte 5 (Database - Alembic + Seeds)"
echo ""
echo "📊 Status atual:"
echo "• Lote 1: ✅ Estrutura monorepo"
echo "• Lote 2.1: ✅ Configuração Python"
echo "• Lote 2.2: ✅ Domain Layer (Entities, Repositories, Core)"
echo "• Lote 2.3: ⏳ Adapters Layer (próximo)"
echo "• Lote 2.4: ⏳ API Layer"
echo "• Lote 2.5: ⏳ Database Setup"
echo ""