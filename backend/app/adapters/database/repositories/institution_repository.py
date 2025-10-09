from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.repositories.institution import InstitutionRepository
from app.domain.entities.institution import Institution
from app.adapters.database.models.institution import InstitutionModel

class InstitutionRepositoryImpl(InstitutionRepository):
    def _model_to_entity(self, model: InstitutionModel) -> Institution:
        return Institution(**model.dict())

    async def create(self, entity_data: Dict[str, Any]) -> Institution:
        model = InstitutionModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, entity_id: int) -> Optional[Institution]:
        result = await self.session.execute(select(InstitutionModel).where(InstitutionModel.id == entity_id))
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_cnpj(self, cnpj: str) -> Optional[Institution]:
        result = await self.session.execute(select(InstitutionModel).where(InstitutionModel.cnpj == cnpj))
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    # Implementar os outros métodos da interface aqui...