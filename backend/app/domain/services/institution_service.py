"""
Institution Service
Serviços de negócio para Instituições
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.institution import Institution
from app.adapters.database.repositories.institution_repository import InstitutionRepositoryImpl
from app.schemas.institution import InstitutionCreate, InstitutionUpdate

class InstitutionService:
    def __init__(self, session: AsyncSession):
        self.repo = InstitutionRepositoryImpl(session)

    async def create_institution(self, institution_data: InstitutionCreate, user_id: int) -> Institution:
        existing_institution = await self.repo.get_by_cnpj(institution_data.cnpj)
        if existing_institution:
            raise ValueError("Uma instituição com este CNPJ já está cadastrada.")

        institution_dict = institution_data.dict()
        institution_dict['created_by'] = user_id
        
        return await self.repo.create(institution_dict)

    async def get_institution(self, institution_id: int) -> Optional[Institution]:
        return await self.repo.get_by_id(institution_id)

    async def get_all_institutions(self, skip: int = 0, limit: int = 100) -> List[Institution]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def update_institution(self, institution_id: int, update_data: InstitutionUpdate) -> Optional[Institution]:
        update_dict = update_data.dict(exclude_unset=True)
        return await self.repo.update(institution_id, update_dict)