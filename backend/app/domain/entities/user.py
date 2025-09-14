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
