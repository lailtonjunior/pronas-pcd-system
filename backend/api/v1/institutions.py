"""
API Endpoints para Instituições - Sistema PRONAS/PCD
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_permissions
from models.user import User, UserRole
from models.institution import Institution, CredentialStatus
from schemas.institution import (
    InstitutionCreate, InstitutionUpdate, Institution as InstitutionSchema,
    InstitutionList, CredentialRequest, DocumentUpload
)
from services.institution_service import InstitutionService
from services.audit_service import AuditService

router = APIRouter(prefix="/institutions", tags=["Institutions"])

@router.post("/", response_model=InstitutionSchema, status_code=201)
async def create_institution(
    institution_data: InstitutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova instituição
    Requer: Autenticação e permissão de criação
    """
    # Verificar permissões
    if current_user.role not in [UserRole.ADMIN, UserRole.GESTOR_MS]:
        if current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já vinculado a uma instituição"
            )
    
    service = InstitutionService(db)
    
    # Validar CNPJ na Receita Federal
    cnpj_data = await service.validate_cnpj(institution_data.cnpj)
    if not cnpj_data or cnpj_data.get("status") == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido ou não encontrado na Receita Federal"
        )
    
    # Criar instituição
    institution = service.create_institution(institution_data, current_user.id)
    
    # Se usuário comum, vincular à instituição criada
    if current_user.role == UserRole.USUARIO:
        current_user.institution_id = institution.id
        current_user.role = UserRole.GESTOR_INST
        db.commit()
    
    return institution

@router.get("/", response_model=InstitutionList)
async def list_institutions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    credential_status: Optional[CredentialStatus] = None,
    institution_type: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar instituições com filtros
    Requer: Autenticação
    """
    service = InstitutionService(db)
    
    # Aplicar filtros baseados no role
    if current_user.role == UserRole.GESTOR_INST:
        # Gestor de instituição vê apenas sua própria
        if not current_user.institution_id:
            return {"items": [], "total": 0, "page": 1, "pages": 0}
        
        institutions = [service.get_institution_by_id(current_user.institution_id)]
        total = 1 if institutions[0] else 0
    else:
        # Admin e Gestor MS veem todas
        institutions, total = service.search_institutions(
            skip=skip,
            limit=limit,
            credential_status=credential_status,
            institution_type=institution_type,
            state=state,
            search=search
        )
    
    return {
        "items": institutions,
        "total": total,
        "page": (skip // limit) + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{institution_id}", response_model=InstitutionSchema)
async def get_institution(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter detalhes de uma instituição
    Requer: Autenticação e permissão de visualização
    """
    service = InstitutionService(db)
    
    # Verificar permissões
    if current_user.role == UserRole.GESTOR_INST:
        if current_user.institution_id != institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para visualizar esta instituição"
            )
    
    institution = service.get_institution_by_id(institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instituição não encontrada"
        )
    
    return institution

@router.put("/{institution_id}", response_model=InstitutionSchema)
async def update_institution(
    institution_id: int,
    institution_data: InstitutionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar dados da instituição
    Requer: Permissão de edição (admin ou gestor da própria instituição)
    """
    service = InstitutionService(db)
    
    # Verificar permissões
    if not current_user.can_manage_institution(institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar esta instituição"
        )
    
    institution = service.update_institution(institution_id, institution_data, current_user.id)
    
    return institution

@router.post("/{institution_id}/credential", response_model=dict)
async def request_credential(
    institution_id: int,
    documents: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Solicitar credenciamento no PRONAS/PCD
    Permitido apenas em junho e julho conforme Art. 14
    Requer: Upload de documentos obrigatórios
    """
    service = InstitutionService(db)
    
    # Verificar permissões
    if not current_user.can_manage_institution(institution_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para solicitar credenciamento"
        )
    
    # Verificar período de credenciamento (junho/julho)
    current_month = datetime.now().month
    if current_month not in [6, 7]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciamento permitido apenas nos meses de junho e julho"
        )
    
    # Verificar documentos obrigatórios
    required_docs = [
        "estatuto_social",
        "ata_eleicao",
        "cnpj_card",
        "certidao_federal",
        "certidao_estadual",
        "certidao_municipal",
        "certidao_fgts",
        "certidao_trabalhista",
        "balanco_patrimonial",
        "experiencia_comprovacao"
    ]
    
    uploaded_types = [doc.filename.split('_')[0] for doc in documents]
    missing_docs = set(required_docs) - set(uploaded_types)
    
    if missing_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Documentos faltando: {', '.join(missing_docs)}"
        )
    
    # Processar documentos
    result = await service.process_credential_request(
        institution_id=institution_id,
        documents=documents,
        user_id=current_user.id
    )
    
    return {
        "message": "Solicitação de credenciamento enviada com sucesso",
        "protocol": result["protocol"],
        "documents_uploaded": len(documents),
        "status": "pending"
    }

@router.get("/{institution_id}/verify-credentials", response_model=dict)
async def verify_credentials(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar validade das certidões e credenciamento
    """
    service = InstitutionService(db)
    
    institution = service.get_institution_by_id(institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instituição não encontrada"
        )
    
    # Verificar validade das certidões
    now = datetime.utcnow()
    credentials_status = {
        "credential_valid": institution.is_credential_valid(),
        "credential_expiry": institution.credential_expiry_date,
        "cndt_valid": institution.cndt_valid_until and institution.cndt_valid_until > now,
        "cndt_expiry": institution.cndt_valid_until,
        "crf_valid": institution.crf_valid_until and institution.crf_valid_until > now,
        "crf_expiry": institution.crf_valid_until,
        "cnda_valid": institution.cnda_valid_until and institution.cnda_valid_until > now,
        "cnda_expiry": institution.cnda_valid_until,
        "all_valid": institution.is_credential_valid() and all([
            institution.cndt_valid_until and institution.cndt_valid_until > now,
            institution.crf_valid_until and institution.crf_valid_until > now,
            institution.cnda_valid_until and institution.cnda_valid_until > now
        ])
    }
    
    return credentials_status

@router.post("/{institution_id}/approve-credential", response_model=InstitutionSchema)
async def approve_credential(
    institution_id: int,
    comments: Optional[str] = None,
    current_user: User = Depends(require_permissions(["credential.approve"])),
    db: Session = Depends(get_db)
):
    """
    Aprovar credenciamento (apenas Gestor MS)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.GESTOR_MS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores do MS podem aprovar credenciamento"
        )
    
    service = InstitutionService(db)
    institution = service.approve_credential(
        institution_id=institution_id,
        approved_by=current_user.id,
        comments=comments
    )
    
    return institution

@router.post("/{institution_id}/reject-credential", response_model=InstitutionSchema)
async def reject_credential(
    institution_id: int,
    reason: str,
    current_user: User = Depends(require_permissions(["credential.reject"])),
    db: Session = Depends(get_db)
):
    """
    Rejeitar credenciamento (apenas Gestor MS)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.GESTOR_MS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gestores do MS podem rejeitar credenciamento"
        )
    
    service = InstitutionService(db)
    institution = service.reject_credential(
        institution_id=institution_id,
        rejected_by=current_user.id,
        reason=reason
    )
    
    return institution

@router.get("/{institution_id}/statistics", response_model=dict)
async def get_institution_statistics(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter estatísticas da instituição
    """
    service = InstitutionService(db)
    
    # Verificar permissões
    if current_user.role == UserRole.GESTOR_INST:
        if current_user.institution_id != institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para visualizar estatísticas desta instituição"
            )
    
    stats = service.get_institution_statistics(institution_id)
    
    return stats

@router.delete("/{institution_id}", status_code=204)
async def delete_institution(
    institution_id: int,
    current_user: User = Depends(require_permissions(["institution.delete"])),
    db: Session = Depends(get_db)
):
    """
    Excluir instituição (soft delete)
    Apenas Admin pode excluir
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir instituições"
        )
    
    service = InstitutionService(db)
    
    # Verificar se tem projetos ativos
    institution = service.get_institution_by_id(institution_id)
    if institution.active_projects_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir instituição com projetos ativos"
        )
    
    service.soft_delete_institution(institution_id, current_user.id)
    
    return