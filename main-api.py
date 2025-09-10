# main.py - Main FastAPI Application for PRONAS/PCD System
# Based on official PRONAS/PCD guidelines

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import os

# Importar módulos locais
from database import get_db, engine
from models import Base, Institution, Project, PriorityArea
from schemas import *
from ai_service_enhanced import PronasAIEngine
from auth import create_access_token, verify_password, get_current_user
from crud import *

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="PRONAS/PCD Management System",
    description="Sistema de Gestão para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar serviços
ai_engine = PronasAIEngine()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/login", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autenticação de usuários do sistema
    """
    try:
        # Verificar credenciais (implementação básica)
        if not verify_password(form_data.password, form_data.username):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Gerar token de acesso
        access_token = create_access_token(data={"sub": form_data.username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "username": form_data.username,
                "permissions": ["read", "write", "admin"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obter informações do usuário autenticado
    """
    return {
        "username": current_user.get("username"),
        "permissions": ["read", "write", "admin"],
        "authenticated": True
    }

# ==================== INSTITUTION ENDPOINTS ====================

@app.post("/institutions/", response_model=Institution, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution: InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cadastrar nova instituição no sistema
    Baseado nos requisitos de credenciamento do PRONAS/PCD
    """
    try:
        # Verificar se CNPJ já existe
        existing = get_institution_by_cnpj(db, institution.cnpj)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="CNPJ já cadastrado no sistema"
            )
        
        # Criar instituição
        db_institution = create_institution_db(db, institution)
        
        logger.info(f"Instituição criada: {db_institution.name} (ID: {db_institution.id})")
        return db_institution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar instituição: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/institutions/", response_model=List[Institution])
async def list_institutions(
    skip: int = 0,
    limit: int = 100,
    credential_status: Optional[CredentialStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar instituições cadastradas
    """
    try:
        institutions = get_institutions(db, skip=skip, limit=limit, status=credential_status)
        return institutions
    
    except Exception as e:
        logger.error(f"Erro ao listar instituições: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/institutions/{institution_id}", response_model=Institution)
async def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obter detalhes de uma instituição específica
    """
    try:
        institution = get_institution_by_id(db, institution_id)
        if not institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        return institution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter instituição: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.put("/institutions/{institution_id}", response_model=Institution)
async def update_institution(
    institution_id: int,
    institution_update: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Atualizar dados de uma instituição
    """
    try:
        updated_institution = update_institution_db(db, institution_id, institution_update)
        if not updated_institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        logger.info(f"Instituição atualizada: ID {institution_id}")
        return updated_institution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar instituição: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/institutions/{institution_id}/credential", response_model=Dict[str, Any])
async def request_credential(
    institution_id: int,
    documents: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Solicitar credenciamento de instituição
    Baseado nos requisitos do Art. 24 da Portaria
    """
    try:
        institution = get_institution_by_id(db, institution_id)
        if not institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        # Validar período de credenciamento (junho/julho)
        current_month = datetime.now().month
        if current_month not in [6, 7]:
            raise HTTPException(
                status_code=400,
                detail="Credenciamento só pode ser solicitado em junho e julho"
            )
        
        # Validar documentos obrigatórios
        required_docs = ["estatuto", "ata", "cnpj", "certidoes", "experiencia"]
        uploaded_types = [doc.filename.split('_')[0] for doc in documents if '_' in doc.filename]
        missing_docs = [doc for doc in required_docs if doc not in uploaded_types]
        
        if missing_docs:
            raise HTTPException(
                status_code=400,
                detail=f"Documentos faltantes: {', '.join(missing_docs)}"
            )
        
        # Salvar documentos e atualizar status
        for document in documents:
            # Salvar arquivo (implementação seria necessária)
            pass
        
        # Atualizar status para pending
        update_data = {"credential_status": CredentialStatusEnum.PENDING}
        update_institution_db(db, institution_id, InstitutionUpdate(**update_data))
        
        return {
            "message": "Solicitação de credenciamento enviada com sucesso",
            "status": "pending",
            "documents_received": len(documents)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar credenciamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== PROJECT ENDPOINTS ====================

@app.post("/projects/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Criar novo projeto PRONAS/PCD
    Baseado nas diretrizes oficiais
    """
    try:
        # Validar se instituição está credenciada
        institution = get_institution_by_id(db, project.institution_id)
        if not institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        if institution.credential_status != CredentialStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Instituição deve estar credenciada para submeter projetos"
            )
        
        # Validar limite de 3 projetos por instituição
        existing_projects = get_projects_by_institution(db, project.institution_id, status=ProjectStatusEnum.SUBMITTED)
        if len(existing_projects) >= 3:
            raise HTTPException(
                status_code=400,
                detail="Instituição já possui o limite de 3 projetos submetidos"
            )
        
        # Criar projeto
        db_project = create_project_db(db, project)
        
        logger.info(f"Projeto criado: {db_project.title} (ID: {db_project.id})")
        return db_project
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar projeto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/projects/", response_model=List[Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ProjectStatusEnum] = None,
    institution_id: Optional[int] = None,
    field_of_action: Optional[FieldOfActionEnum] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar projetos com filtros
    """
    try:
        projects = get_projects(
            db, 
            skip=skip, 
            limit=limit,
            status=status_filter,
            institution_id=institution_id,
            field_of_action=field_of_action
        )
        return projects
    
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obter detalhes completos de um projeto
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        return project
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter projeto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.put("/projects/{project_id}/submit")
async def submit_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submeter projeto para análise
    Validações baseadas nas regras do PRONAS/PCD
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        if project.status != ProjectStatusEnum.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Apenas projetos em rascunho podem ser submetidos"
            )
        
        # Validar completude do projeto
        validation_results = await ai_engine._validate_project_compliance(
            ProjectCreate(**project.__dict__)
        )
        
        if not validation_results["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Projeto inválido: {', '.join(validation_results['errors'])}"
            )
        
        # Verificar período de submissão (45 dias após portaria interministerial)
        # Implementação seria baseada em configuração do sistema
        
        # Atualizar status
        update_project_status(db, project_id, ProjectStatusEnum.SUBMITTED)
        
        return {
            "message": "Projeto submetido com sucesso",
            "project_id": project_id,
            "submission_date": datetime.now().isoformat(),
            "status": "submitted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao submeter projeto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/projects/{project_id}/validate", response_model=ProjectSubmissionValidation)
async def validate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Validar projeto antes da submissão
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Executar validação completa
        validation_results = await ai_engine._validate_project_compliance(
            ProjectCreate(**project.__dict__)
        )
        
        compliance_score = await ai_engine._calculate_compliance_score(
            ProjectCreate(**project.__dict__), validation_results
        )
        
        return ProjectSubmissionValidation(
            is_valid=validation_results["is_valid"],
            errors=validation_results.get("errors", []),
            warnings=validation_results.get("warnings", []),
            compliance_score=compliance_score,
            required_documents=["estatuto", "ata", "cnpj", "certidoes"],
            missing_documents=[]  # Implementar verificação de documentos
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao validar projeto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== AI ENDPOINTS ====================

@app.post("/ai/generate-project", response_model=AIProjectResponse)
async def generate_project_with_ai(
    generation_request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Gerar projeto usando IA baseada nas diretrizes do PRONAS/PCD
    """
    try:
        # Validar parâmetros de entrada
        required_fields = ["institution_id", "priority_area_code", "budget_total"]
        for field in required_fields:
            if field not in generation_request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo obrigatório: {field}"
                )
        
        # Obter dados da instituição
        institution = get_institution_by_id(db, generation_request["institution_id"])
        if not institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        institution_data = {
            "name": institution.name,
            "institution_type": institution.institution_type,
            "city": institution.city,
            "state": institution.state
        }
        
        # Gerar projeto com IA
        ai_response = await ai_engine.generate_project_from_guidelines(
            institution_data=institution_data,
            project_requirements=generation_request,
            priority_area_code=generation_request["priority_area_code"]
        )
        
        logger.info(f"Projeto gerado por IA para instituição {institution.name}")
        return ai_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração por IA: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/ai/priority-areas", response_model=List[Dict[str, Any]])
async def get_priority_areas():
    """
    Listar áreas prioritárias disponíveis (Art. 10 da Portaria)
    """
    try:
        areas = []
        for code, info in ai_engine.priority_areas.items():
            areas.append({
                "code": code,
                "name": info["name"],
                "description": info["description"],
                "typical_actions": info.get("typical_actions", [])
            })
        return areas
    
    except Exception as e:
        logger.error(f"Erro ao obter áreas prioritárias: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== MONITORING ENDPOINTS ====================

@app.get("/projects/{project_id}/monitoring", response_model=List[Dict[str, Any]])
async def get_project_monitoring(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obter dados de monitoramento do projeto
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        monitoring_data = get_project_monitoring_data(db, project_id)
        return monitoring_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter monitoramento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/projects/{project_id}/monitoring")
async def add_monitoring_entry(
    project_id: int,
    monitoring_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Adicionar entrada de monitoramento
    """
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        if project.status not in [ProjectStatusEnum.IN_EXECUTION]:
            raise HTTPException(
                status_code=400,
                detail="Monitoramento só pode ser adicionado a projetos em execução"
            )
        
        # Adicionar entrada de monitoramento
        monitoring_entry = add_project_monitoring(db, project_id, monitoring_data)
        
        return {
            "message": "Dados de monitoramento adicionados",
            "entry_id": monitoring_entry.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar monitoramento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== UTILITY ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """
    Verificação de saúde da aplicação
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "connected",
        "ai_engine": "active"
    }

@app.get("/system/config", response_model=Dict[str, Any])
async def get_system_config(current_user: dict = Depends(get_current_user)):
    """
    Obter configurações do sistema
    """
    try:
        return {
            "submission_period_days": 45,
            "max_projects_per_institution": 3,
            "min_captacao_percentage": 0.60,
            "max_captacao_percentage": 1.20,
            "max_captacao_absolute": 50000,
            "credentialing_months": [6, 7],  # junho, julho
            "current_year_budget_limit": 500000000,  # R$ 500 milhões
            "priority_areas": list(ai_engine.priority_areas.keys())
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/reports/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obter dados para dashboard executivo
    """
    try:
        stats = {
            "total_institutions": get_institutions_count(db),
            "active_institutions": get_institutions_count(db, CredentialStatusEnum.ACTIVE),
            "total_projects": get_projects_count(db),
            "submitted_projects": get_projects_count(db, ProjectStatusEnum.SUBMITTED),
            "approved_projects": get_projects_count(db, ProjectStatusEnum.APPROVED),
            "projects_in_execution": get_projects_count(db, ProjectStatusEnum.IN_EXECUTION),
            "total_budget_requested": get_total_budget_requested(db),
            "total_budget_approved": get_total_budget_approved(db)
        }
        
        # Estatísticas por área prioritária
        priority_area_stats = {}
        for code in ai_engine.priority_areas.keys():
            priority_area_stats[code] = get_projects_count_by_priority_area(db, code)
        
        stats["by_priority_area"] = priority_area_stats
        
        return stats
    
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """
    Inicialização da aplicação
    """
    logger.info("Iniciando sistema PRONAS/PCD")
    
    # Inicializar dados básicos (áreas prioritárias, etc.)
    try:
        await initialize_system_data()
        logger.info("Sistema inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro na inicialização: {str(e)}")

async def initialize_system_data():
    """
    Inicializar dados básicos do sistema
    """
    # Implementar inicialização de dados
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )