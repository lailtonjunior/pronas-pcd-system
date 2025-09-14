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
