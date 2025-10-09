"""
Implementação do Repositório de Documentos
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.document import DocumentRepository
from app.domain.entities.document import Document
from app.adapters.database.models.document import DocumentModel

class DocumentRepositoryImpl(DocumentRepository):
    """Implementação concreta do repositório de documentos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: DocumentModel) -> Document:
        """Converte o modelo SQLAlchemy para uma entidade de domínio."""
        return Document.from_orm(model)

    async def create(self, entity_data: Dict[str, Any]) -> Document:
        """Cria um novo registro de documento."""
        model = DocumentModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, entity_id: int) -> Optional[Document]:
        """Busca um documento pelo seu ID."""
        stmt = select(DocumentModel).where(DocumentModel.id == entity_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_project_id(self, project_id: int) -> List[Document]:
        """Busca todos os documentos associados a um projeto."""
        stmt = select(DocumentModel).where(DocumentModel.project_id == project_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete(self, entity_id: int) -> None:
        """Deleta um documento pelo seu ID."""
        stmt = delete(DocumentModel).where(DocumentModel.id == entity_id)
        await self.session.execute(stmt)
        await self.session.commit()