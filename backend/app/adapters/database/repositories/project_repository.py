"""
Implementação do Repositório de Projetos
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.project import ProjectRepository
from app.domain.entities.project import Project
from app.adapters.database.models.project import ProjectModel

class ProjectRepositoryImpl(ProjectRepository):
    """Implementação concreta do repositório de projetos usando SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ProjectModel) -> Project:
        """Converte o modelo SQLAlchemy para uma entidade de domínio."""
        return Project.from_orm(model)

    async def create(self, entity_data: Dict[str, Any]) -> Project:
        """Cria um novo registro de projeto no banco de dados."""
        model = ProjectModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, entity_id: int) -> Optional[Project]:
        """Busca um projeto pelo seu ID."""
        stmt = select(ProjectModel).where(ProjectModel.id == entity_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Busca todos os projetos com paginação."""
        stmt = select(ProjectModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, entity_id: int, update_data: Dict[str, Any]) -> Optional[Project]:
        """Atualiza um projeto existente."""
        stmt = update(ProjectModel).where(ProjectModel.id == entity_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(entity_id)

    async def delete(self, entity_id: int) -> None:
        """Deleta um projeto pelo seu ID."""
        stmt = delete(ProjectModel).where(ProjectModel.id == entity_id)
        await self.session.execute(stmt)
        await self.session.commit()