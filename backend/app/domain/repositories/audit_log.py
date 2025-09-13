"""
Audit Log Repository Interface
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.repositories.base import BaseRepository
from app.domain.entities.audit_log import AuditLog, AuditAction, AuditResource


class AuditLogRepository(BaseRepository[AuditLog, int]):
    """Interface do repositório de logs de auditoria"""
    
    @abstractmethod
    async def create_log(
        self,
        action: AuditAction,
        resource: AuditResource,
        user_id: int,
        user_email: str,
        user_role: str,
        ip_address: str,
        user_agent: str,
        session_id: str,
        description: str,
        resource_id: Optional[int] = None,
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        data_sensitivity: str = "internal"
    ) -> AuditLog:
        """Criar log de auditoria (método especializado)"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int) -> List[AuditLog]:
        """Buscar logs por usuário"""
        pass
    
    @abstractmethod
    async def get_by_resource(
        self, 
        resource: AuditResource, 
        resource_id: Optional[int] = None
    ) -> List[AuditLog]:
        """Buscar logs por recurso"""
        pass
    
    @abstractmethod
    async def get_by_action(self, action: AuditAction) -> List[AuditLog]:
        """Buscar logs por ação"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[AuditLog]:
        """Buscar logs por período"""
        pass
    
    @abstractmethod
    async def get_failed_operations(self) -> List[AuditLog]:
        """Buscar operações que falharam"""
        pass
    
    @abstractmethod
    async def get_sensitive_data_access(self) -> List[AuditLog]:
        """Buscar acessos a dados sensíveis (LGPD)"""
        pass
    
    @abstractmethod
    async def get_user_activity_summary(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, int]:
        """Obter resumo de atividade do usuário"""
        pass
    
    @abstractmethod
    async def get_system_activity_summary(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Obter resumo de atividade do sistema"""
        pass