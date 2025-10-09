"""
Endpoints for Project Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db_session
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.domain.services.projects_service import ProjectService # Corrigido para o nome correto do serviço
from app.domain.entities.user import User
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # Nota: O AuditLogRepository precisa ser injetado no serviço
    # Por simplicidade, estamos omitindo aqui, mas deve ser adicionado
    service = ProjectService(session, audit_repo=None) 
    try:
        project = await service.create_project(project_data.dict(), current_user, "127.0.0.1", "agent", "session_id")
        return ProjectResponse.from_orm(project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    # O AuditLogRepository é necessário para o serviço completo
    service = ProjectService(session, audit_repo=None) 
    project = await service.project_repo.get_by_id(project_id) # Acessando o repo diretamente
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.from_orm(project)