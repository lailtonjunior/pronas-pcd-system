"""
Implementação do Repositório de Logs de Auditoria
"""
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.audit_log import AuditLogRepository
from app.domain.entities.audit_log import AuditLog
from app.adapters.database.models.audit_log import AuditLogModel

class AuditLogRepositoryImpl(AuditLogRepository):
    """Implementação concreta do repositório de logs de auditoria."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: AuditLogModel) -> AuditLog:
        """Converte o modelo SQLAlchemy para uma entidade de domínio."""
        return AuditLog.from_orm(model)

    async def create(self, entity_data: Dict[str, Any]) -> AuditLog:
        """Cria um novo registro de log de auditoria."""
        model = AuditLogModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_user_id(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Busca os logs de auditoria mais recentes de um usuário."""
        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .order_by(AuditLogModel.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]