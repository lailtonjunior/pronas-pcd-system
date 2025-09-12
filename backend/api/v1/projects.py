"""
API Endpoints para Projetos - Sistema PRONAS/PCD
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_permissions
from models.user import User, UserRole
from models.project import Project, ProjectStatus, FieldOfAction
from schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectSchema, ProjectList,
    ProjectSubmit, ProjectApproval, MonitoringReport
)
from services.project_service import ProjectService
from services.ai_service import PronasAIService
from services.export_service import ExportService

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectSchema, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar novo projeto PRONAS/PCD
    
    Validações aplicadas:
    - Instituição com credenciamento válido
    - Máximo 3 projetos por instituição
    - Justificativa mínima 500 caracteres
    - Mínimo 3 objetivos específicos
    - Cronograma 6-48 meses
    - Auditoria obrigatória no orçamento
    - Captação máximo 5% ou R$ 50.000
    """
    service = ProjectService(db)
    
    # Verificar permissões
    if current_user.role == UserRole.GESTOR_INST:
        if current_user.institution_id != project_data.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode criar projetos para sua própria instituição"
            )
    
    project = service.create_project(project_data, current_user.id)
    
    return project

@router.get("/", response_model=ProjectList)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[ProjectStatus] = None,
    institution_id: Optional[int] = None,
    priority_area_id: Optional[int] = None,
    field_of_action: Optional[FieldOfAction] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar projetos com filtros avançados
    """
    service = ProjectService(db)
    
    # Aplicar filtros baseados no role
    if current_user.role == UserRole.GESTOR_INST:
        # Gestor de instituição vê apenas projetos da sua instituição
        institution_id = current_user.institution_id
    
    projects = service.search_projects(
        search_term=search,
        status=status_filter,
        priority_area_id=priority_area_id,
        institution_id=institution_id,
        field_of_action=field_of_action,
        skip=skip,
        limit=limit
    )
    
    total = len(projects)  # Em produção, fazer count separado
    
    return {
        "items": projects,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter detalhes completos de um projeto
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Verificar permissões de visualização
    if current_user.role == UserRole.GESTOR_INST:
        if project.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para visualizar este projeto"
            )
    
    return project

@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar projeto (apenas em status DRAFT ou REJECTED)
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Verificar permissões
    if not current_user.can_manage_institution(project.institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este projeto"
        )
    
    # Verificar se pode ser editado
    if not project.can_be_edited():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Projeto no status {project.status.value} não pode ser editado"
        )
    
    updated_project = service.update_project(project_id, project_data, current_user.id)
    
    return updated_project

@router.post("/{project_id}/submit", response_model=ProjectSchema)
async def submit_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submeter projeto para análise do Ministério da Saúde
    """
    service = ProjectService(db)
    
    project = service.submit_project(project_id, current_user.id)
    
    return project

@router.post("/{project_id}/approve", response_model=ProjectSchema)
async def approve_project(
    project_id: int,
    approval_data: ProjectApproval,
    current_user: User = Depends(require_permissions(["project.approve"])),
    db: Session = Depends(get_db)
):
    """
    Aprovar projeto (apenas Gestor MS)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.GESTOR_MS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores do MS podem aprovar projetos"
        )
    
    service = ProjectService(db)
    project = service.approve_project(
        project_id=project_id,
        user_id=current_user.id,
        comments=approval_data.comments
    )
    
    return project

@router.post("/{project_id}/reject", response_model=ProjectSchema)
async def reject_project(
    project_id: int,
    rejection_data: dict,
    current_user: User = Depends(require_permissions(["project.reject"])),
    db: Session = Depends(get_db)
):
    """
    Rejeitar projeto (apenas Gestor MS)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.GESTOR_MS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores do MS podem rejeitar projetos"
        )
    
    service = ProjectService(db)
    project = service.reject_project(
        project_id=project_id,
        user_id=current_user.id,
        reason=rejection_data["reason"]
    )
    
    return project

@router.post("/{project_id}/monitoring", response_model=dict)
async def add_monitoring_report(
    project_id: int,
    report_data: MonitoringReport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adicionar relatório de monitoramento/prestação de contas
    """
    service = ProjectService(db)
    
    # Verificar permissões
    project = service.get_project_by_id(project_id)
    if not current_user.can_manage_institution(project.institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para adicionar relatórios a este projeto"
        )
    
    report = service.add_monitoring_report(
        project_id=project_id,
        report_data=report_data.dict(),
        user_id=current_user.id
    )
    
    return {
        "message": "Relatório de monitoramento adicionado com sucesso",
        "report_id": report.id,
        "status": report.status
    }

@router.get("/{project_id}/monitoring", response_model=List[dict])
async def get_monitoring_reports(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter relatórios de monitoramento do projeto
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Verificar permissões
    if current_user.role == UserRole.GESTOR_INST:
        if project.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para visualizar relatórios deste projeto"
            )
    
    reports = project.monitoring_reports
    
    return [
        {
            "id": r.id,
            "report_type": r.report_type,
            "report_period": r.report_period,
            "report_date": r.report_date,
            "beneficiaries_attended": r.beneficiaries_attended,
            "budget_executed": float(r.budget_executed),
            "status": r.status,
            "reviewed_by": r.reviewed_by,
            "reviewed_at": r.reviewed_at
        }
        for r in reports
    ]

@router.post("/{project_id}/validate", response_model=dict)
async def validate_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validar conformidade do projeto com regras PRONAS/PCD
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    validation = service.validate_project_completeness(project)
    
    # Validações adicionais
    budget_validation = service.validate_budget_compliance(project)
    timeline_validation = service.validate_timeline_compliance(project)
    
    return {
        "is_valid": validation["is_complete"] and budget_validation["is_valid"] and timeline_validation["is_valid"],
        "completeness": validation,
        "budget_compliance": budget_validation,
        "timeline_compliance": timeline_validation,
        "compliance_score": service.calculate_compliance_score(project)
    }

@router.post("/{project_id}/documents", response_model=dict)
async def upload_project_documents(
    project_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de documentos do projeto
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not current_user.can_manage_institution(project.institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para adicionar documentos a este projeto"
        )
    
    uploaded_files = await service.upload_documents(
        project_id=project_id,
        files=files,
        user_id=current_user.id
    )
    
    return {
        "message": f"{len(uploaded_files)} documentos enviados com sucesso",
        "files": uploaded_files
    }

@router.get("/{project_id}/export", response_model=dict)
async def export_project(
    project_id: int,
    format: str = Query("pdf", regex="^(pdf|excel|word)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exportar projeto em diferentes formatos
    """
    service = ProjectService(db)
    export_service = ExportService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Verificar permissões
    if current_user.role == UserRole.GESTOR_INST:
        if project.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para exportar este projeto"
            )
    
    file_path = await export_service.export_project(project, format)
    
    return {
        "message": f"Projeto exportado com sucesso em formato {format.upper()}",
        "download_url": f"/api/v1/download/{file_path}"
    }

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: User = Depends(require_permissions(["project.delete"])),
    db: Session = Depends(get_db)
):
    """
    Excluir projeto (soft delete)
    Apenas projetos em DRAFT podem ser excluídos
    """
    service = ProjectService(db)
    
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    if project.status != ProjectStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas projetos em rascunho podem ser excluídos"
        )
    
    if not current_user.can_manage_institution(project.institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para excluir este projeto"
        )
    
    service.soft_delete_project(project_id, current_user.id)
    
    return