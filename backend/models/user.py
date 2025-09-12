"""
Model de Usuário - Sistema PRONAS/PCD
Conformidade: LGPD e segurança de dados
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from models.base import BaseModel

# Associação many-to-many para permissões
user_permissions = Table(
    'user_permissions',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class UserRole(str, enum.Enum):
    """Roles do sistema baseados em responsabilidades PRONAS/PCD"""
    ADMIN = "admin"              # Administrador geral do sistema
    GESTOR_MS = "gestor_ms"      # Gestor do Ministério da Saúde
    GESTOR_INST = "gestor_inst"  # Gestor de instituição
    ANALISTA = "analista"        # Analista de projetos
    AUDITOR = "auditor"          # Auditor independente
    USUARIO = "usuario"          # Usuário comum

class User(BaseModel):
    __tablename__ = "users"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=True)  # Para auditoria
    
    # Autenticação
    hashed_password = Column(String(255), nullable=False)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Dados pessoais
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Controle de acesso
    role = Column(Enum(UserRole), default=UserRole.USUARIO, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Auditoria
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    failed_login_count = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Two-Factor Authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Relacionamentos
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=True)
    institution = relationship("Institution", back_populates="users")
    
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
    
    def has_permission(self, permission_name: str) -> bool:
        """Verifica se usuário tem determinada permissão"""
        return any(p.name == permission_name for p in self.permissions)
    
    def can_manage_institution(self, institution_id: int) -> bool:
        """Verifica se pode gerenciar uma instituição específica"""
        if self.role in [UserRole.ADMIN, UserRole.GESTOR_MS]:
            return True
        return self.institution_id == institution_id and self.role == UserRole.GESTOR_INST

class UserSession(BaseModel):
    """Sessões de usuário para controle de acesso"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")

class Permission(BaseModel):
    """Permissões granulares do sistema"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    resource = Column(String(100), nullable=False)  # Ex: 'project', 'institution'
    action = Column(String(50), nullable=False)     # Ex: 'create', 'read', 'update', 'delete'
    
    users = relationship("User", secondary=user_permissions, back_populates="permissions")