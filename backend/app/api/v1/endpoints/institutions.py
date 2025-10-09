"""
Endpoints for Institution Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db_session
from app.schemas.institution import InstitutionCreate, InstitutionUpdate, InstitutionResponse
from app.domain.services.institution_service import InstitutionService
from app.domain.entities.user import User
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution_data: InstitutionCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    service = InstitutionService(session)
    try:
        institution = await service.create_institution(institution_data, current_user.id)
        # Convertendo a entidade de domínio para o schema de resposta
        return InstitutionResponse.from_orm(institution)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    service = InstitutionService(session)
    institution = await service.get_institution(institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
    return InstitutionResponse.from_orm(institution)

@router.get("/", response_model=List[InstitutionResponse])
async def get_all_institutions(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    service = InstitutionService(session)
    institutions = await service.get_all_institutions(skip, limit)
    return [InstitutionResponse.from_orm(inst) for inst in institutions]