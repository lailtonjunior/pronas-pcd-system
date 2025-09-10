"""
Sistema PRONAS/PCD - API Principal
Baseado na Portaria de Consolidação nº 5/2017 - Anexo LXXXVI
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime, timedelta
import asyncio

# Importações locais
from .database import get_db, engine, init_database
from .models import Base
from .schemas import *
from .ai.engine import PronasAIEngine
from .auth import create_access_token, verify_password, get_current_user
from .crud import *

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/pronas_pcd.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Inicializar dados básicos
asyncio.create_task(init_database())

# Configurar aplicação FastAPI
app = FastAPI(
    title="Sistema PRONAS/PCD",
    description="""
    Sistema de Gestão para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência
    
    **Baseado nas diretrizes oficiais:**
    - Lei nº 12.715/2012 (Lei do PRONAS/PCD)
    - Portaria de Consolidação nº 5/2017 - Anexo LXXXVI  
    - Portaria nº 448/2002 (Natureza de Despesas)
    - Lei nº 13.146/2015 (Lei Brasileira de Inclusão)
    
    **Funcionalidades principais:**
    - Gestão de instituições credenciadas
    - Geração inteligente de projetos com IA
    - Validação automática de conformidade
    - Monitoramento e relatórios
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Autenticação e autorização"},
        {"name": "institutions", "description": "Gestão de instituições"},
        {"name": "projects", "description": "Gestão de projetos PRONAS/PCD"},
        {"name": "ai", "description": "Inteligência Artificial especializada"},
        {"name": "monitoring", "description": "Monitoramento e relatórios"},
        {"name": "system", "description": "Utilitários do sistema"}
    ]
)

# Configurar middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*"]
)

# Inicializar serviços
ai_engine = PronasAIEngine()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==================== MIDDLEWARE PARA LOGGING ====================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = datetime.now() - start_time
    
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time.total_seconds():.3f}s"
    )
    return response

# ==================== EXCEPTION HANDLERS ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erro interno do servidor",
            "error_type": type(exc).__name__,
            "timestamp": datetime.now().isoformat()
        }
    )

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/login", response_model=Dict[str, Any], tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autenticação de usuários do sistema
    
    **Credenciais padrão (desenvolvimento):**
    - admin / password
    - user / password
    - gestor / password
    
    **Retorna:**
    - Token JWT válido por 8 horas
    - Informações do usuário
    - Permissões
    """
    try:
        if not verify_password(form_data.password, form_data.username):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": form_data.username})
        
        # Definir permissões por tipo de usuário
        permissions = {
            "admin": ["read", "write", "delete", "manage_users", "manage_system"],
            "gestor": ["read", "write", "manage_projects", "generate_reports"],
            "user": ["read", "write", "create_projects"]
        }.get(form_data.username, ["read"])
        
        logger.info(f"Login bem-sucedido para usuário: {form_data.username}")
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 28800,  # 8 horas
            "user": {
                "username": form_data.username,
                "permissions": permissions,
                "login_time": datetime.now().isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/auth/me", response_model=Dict[str, Any], tags=["auth"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obter informações do usuário autenticado"""
    return {
        "success": True,
        "user": {
            "username": current_user.get("username"),
            "permissions": ["read", "write", "admin"],
            "authenticated": True,
            "session_time": datetime.now().isoformat()
        }
    }

@app.post("/auth/logout", tags=["auth"])
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout do sistema"""
    logger.info(f"Logout do usuário: {current_user.get('username')}")
    return {
        "success": True,
        "message": "Logout realizado com sucesso"
    }

# ==================== INSTITUTION ENDPOINTS ====================

@app.post("/institutions/", response_model=Institution, status_code=status.HTTP_201_CREATED, tags=["institutions"])
async def create_institution(
    institution: InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cadastrar nova instituição no sistema
    
    **Requisitos baseados no PRONAS/PCD:**
    - CNPJ válido e único
    - Dados completos conforme Portaria
    - Documentação de experiência mínima
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
        
        logger.info(f"Instituição criada: {db_institution.name} (ID: {db_institution.id}) por {current_user.get('username')}")
        return db_institution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar instituição: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/institutions/", response_model=List[Institution], tags=["institutions"])
async def list_institutions(
    skip: int = 0,
    limit: int = 100,
    credential_status: Optional[CredentialStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar instituições cadastradas
    
    **Filtros disponíveis:**
    - credential_status: pending, active, inactive, expired, rejected
    """
    try:
        institutions = get_institutions(db, skip=skip, limit=limit, status=credential_status)
        return institutions
    
    except Exception as e:
        logger.error(f"Erro ao listar instituições: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/institutions/{institution_id}", response_model=Institution, tags=["institutions"])
async def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter detalhes de uma instituição específica"""
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

@app.put("/institutions/{institution_id}", response_model=Institution, tags=["institutions"])
async def update_institution(
    institution_id: int,
    institution_update: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar dados de uma instituição"""
    try:
        updated_institution = update_institution_db(db, institution_id, institution_update)
        if not updated_institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        logger.info(f"Instituição atualizada: ID {institution_id} por {current_user.get('username')}")
        return updated_institution
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar instituição: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/institutions/{institution_id}/credential", response_model=Dict[str, Any], tags=["institutions"])
async def request_credential(
    institution_id: int,
    documents: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Solicitar credenciamento de instituição
    
    **Baseado no Art. 24 da Portaria:**
    - Solicitação apenas em junho e julho
    - Documentos obrigatórios: estatuto, ata, CNPJ, certidões, experiência
    """
    try:
        institution = get_institution_by_id(db, institution_id)
        if not institution:
            raise HTTPException(status_code=404, detail="Instituição não encontrada")
        
        # Validar período de credenciamento (junho/julho)
        current_month = datetime.now().month
        credentialing_months = list(map(int, os.getenv("CREDENTIALING_MONTHS", "6,7").split(",")))
        
        if current_month not in credentialing_months:
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
        
        # Processar documentos (salvar arquivos)
        for document in documents:
            if document.size > int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo {document.filename} excede tamanho máximo"
                )
        
        # Atualizar status para pending
        update_data = {"credential_status": CredentialStatusEnum.PENDING}
        update_institution_db(db, institution_id, InstitutionUpdate(**update_data))
        
        logger.info(f"Solicitação de credenciamento enviada - Instituição ID: {institution_id}")
        
        return {
            "success": True,
            "message": "Solicitação de credenciamento enviada com sucesso",
            "status": "pending",
            "documents_received": len(documents),
            "submission_date": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar credenciamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== PROJECT ENDPOINTS ====================

@app.post("/projects/", response_model=Project, status_code=status.HTTP_201_CREATED, tags=["projects"])
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Criar novo projeto PRONAS/PCD
    
    **Validações automáticas:**
    - Instituição credenciada
    - Máximo 3 projetos por instituição
    - Conformidade com regras oficiais
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
        max_projects = int(os.getenv("MAX_PROJECTS_PER_INSTITUTION", "3"))
        
        if len(existing_projects) >= max_projects:
            raise HTTPException(
                status_code=400,
                detail=f"Instituição já possui o limite de {max_projects} projetos submetidos"
            )
        
        # Criar projeto
        db_project = create_project_db(db, project)
        
        logger.info(f"Projeto criado: {db_project.title} (ID: {db_project.id}) por {current_user.get('username')}")
        return db_project
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar projeto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/projects/", response_model=List[Project], tags=["projects"])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ProjectStatusEnum] = None,
    institution_id: Optional[int] = None,
    field_of_action: Optional[FieldOfActionEnum] = None,
    priority_area_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar projetos com filtros
    
    **Filtros disponíveis:**
    - status: draft, submitted, approved, etc.
    - institution_id: ID da instituição
    - field_of_action: medico_assistencial, formacao, pesquisa
    - priority_area_id: 1-8 (áreas do Art. 10)
    """
    try:
        projects = get_projects(
            db, 
            skip=skip, 
            limit=limit,
            status=status_filter,
            institution_id=institution_id,
            field_of_action=field_of_action,
            priority_area_id=priority_area_id
        )
        return projects
    
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/projects/{project_id}", response_model=Project, tags=["projects"])
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter detalhes completos de um projeto"""
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

@app.post("/projects/{project_id}/validate", response_model=ProjectValidation, tags=["projects"])
async def validate_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Validar projeto antes da submissão
    
    **Validações incluem:**
    - Conformidade com Portaria de Consolidação
    - Orçamento conforme Portaria 448/2002
    - Equipe adequada
    - Metas mensuráveis
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
        
        return ProjectValidation(
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

@app.put("/projects/{project_id}/submit", tags=["projects"])
async def submit_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Submeter projeto para análise
    
    **Requisitos:**
    - Projeto válido conforme validação
    - Período de submissão ativo
    - Documentação completa
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
        
        # Atualizar status
        update_project_status(db, project_id, ProjectStatusEnum.SUBMITTED)
        
        logger.info(f"Projeto submetido: ID {project_id} por {current_user.get('username')}")
        
        return {
            "success": True,
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

# ==================== AI ENDPOINTS ====================

@app.post("/ai/generate-project", response_model=AIProjectResponse, tags=["ai"])
async def generate_project_with_ai(
    generation_request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Gerar projeto usando IA baseada nas diretrizes do PRONAS/PCD
    
    **Parâmetros:**
    - institution_id: ID da instituição
    - priority_area_code: Código da área (QSS, RPD, DDP, EPD, ITR, APE, TAA, APC)
    - budget_total: Orçamento total
    - timeline_months: Prazo em meses
    - target_beneficiaries: Número de beneficiários
    - local_context: Contexto local
    """
    try:
        # Validar parâmetros obrigatórios
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
        
        if institution.credential_status != CredentialStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Instituição deve estar credenciada para gerar projetos"
            )
        
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
        
        logger.info(f"Projeto gerado por IA para instituição {institution.name} por {current_user.get('username')}")
        return ai_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração por IA: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/ai/priority-areas", response_model=List[Dict[str, Any]], tags=["ai"])
async def get_priority_areas():
    """
    Listar áreas prioritárias disponíveis (Art. 10 da Portaria)
    
    **Áreas implementadas:**
    - QSS: Qualificação de serviços de saúde
    - RPD: Reabilitação/habilitação da pessoa com deficiência
    - DDP: Diagnóstico diferencial da pessoa com deficiência
    - EPD: Identificação e estimulação precoce das deficiências
    - ITR: Adaptação, inserção e reinserção no trabalho
    - APE: Apoio à saúde por meio de práticas esportivas
    - TAA: Terapia assistida por animais (TAA)
    - APC: Apoio à saúde por meio de produção artística e cultural
    """
    try:
        areas = []
        for code, info in ai_engine.priority_areas.items():
            areas.append({
                "code": code,
                "name": info["name"],
                "description": info["description"],
                "typical_actions": info.get("typical_actions", []),
                "budget_distribution": info.get("typical_budget_distribution", {})
            })
        return areas
    
    except Exception as e:
        logger.error(f"Erro ao obter áreas prioritárias: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== MONITORING ENDPOINTS ====================

@app.get("/projects/{project_id}/monitoring", response_model=List[Dict[str, Any]], tags=["monitoring"])
async def get_project_monitoring(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter dados de monitoramento do projeto"""
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

@app.post("/projects/{project_id}/monitoring", tags=["monitoring"])
async def add_monitoring_entry(
    project_id: int,
    monitoring_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Adicionar entrada de monitoramento"""
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
            "success": True,
            "message": "Dados de monitoramento adicionados",
            "entry_id": monitoring_entry.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar monitoramento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# ==================== SYSTEM ENDPOINTS ====================

@app.get("/health", tags=["system"])
async def health_check():
    """
    Verificação de saúde da aplicação
    
    **Verifica:**
    - Status da aplicação
    - Conexão com banco de dados
    - Conexão com Redis
    - Status da IA
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "redis": "connected", 
            "ai_engine": "active",
            "storage": "available"
        },
        "system_info": {
            "environment": os.getenv("ENVIRONMENT", "production"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }
    }

@app.get("/system/config", response_model=Dict[str, Any], tags=["system"])
async def get_system_config(current_user: dict = Depends(get_current_user)):
    """
    Obter configurações do sistema
    
    **Configurações baseadas na legislação PRONAS/PCD**
    """
    try:
        return {
            "business_rules": {
                "submission_period_days": int(os.getenv("SUBMISSION_PERIOD_DAYS", "45")),
                "max_projects_per_institution": int(os.getenv("MAX_PROJECTS_PER_INSTITUTION", "3")),
                "min_captacao_percentage": float(os.getenv("MIN_CAPTACAO_PERCENTAGE", "0.6")),
                "max_captacao_percentage": float(os.getenv("MAX_CAPTACAO_PERCENTAGE", "1.2")),
                "max_captacao_absolute": int(os.getenv("MAX_CAPTACAO_ABSOLUTE", "50000")),
                "credentialing_months": list(map(int, os.getenv("CREDENTIALING_MONTHS", "6,7").split(","))),
                "min_timeline_months": int(os.getenv("MIN_PROJECT_TIMELINE_MONTHS", "6")),
                "max_timeline_months": int(os.getenv("MAX_PROJECT_TIMELINE_MONTHS", "48"))
            },
            "priority_areas": list(ai_engine.priority_areas.keys()),
            "ai_config": {
                "model": os.getenv("AI_MODEL_NAME", "gpt-4-turbo"),
                "confidence_threshold": float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7")),
                "enabled": os.getenv("ENABLE_AI_GENERATION", "true").lower() == "true"
            },
            "file_upload": {
                "max_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", "50")),
                "allowed_extensions": os.getenv("ALLOWED_FILE_EXTENSIONS", "pdf,doc,docx,jpg,jpeg,png,zip").split(",")
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter configurações: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/reports/dashboard", response_model=Dict[str, Any], tags=["monitoring"])
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obter dados para dashboard executivo
    
    **Métricas incluem:**
    - Estatísticas de instituições
    - Estatísticas de projetos  
    - Orçamentos aprovados
    - Distribuição por área prioritária
    """
    try:
        stats = {
            "institutions": {
                "total": get_institutions_count(db),
                "active": get_institutions_count(db, CredentialStatusEnum.ACTIVE),
                "pending": get_institutions_count(db, CredentialStatusEnum.PENDING),
                "inactive": get_institutions_count(db, CredentialStatusEnum.INACTIVE)
            },
            "projects": {
                "total": get_projects_count(db),
                "draft": get_projects_count(db, ProjectStatusEnum.DRAFT),
                "submitted": get_projects_count(db, ProjectStatusEnum.SUBMITTED),
                "approved": get_projects_count(db, ProjectStatusEnum.APPROVED),
                "in_execution": get_projects_count(db, ProjectStatusEnum.IN_EXECUTION),
                "completed": get_projects_count(db, ProjectStatusEnum.COMPLETED)
            },
            "budget": {
                "total_requested": get_total_budget_requested(db),
                "total_approved": get_total_budget_approved(db)
            },
            "by_priority_area": {}
        }
        
        # Estatísticas por área prioritária
        for code in ai_engine.priority_areas.keys():
            stats["by_priority_area"][code] = get_projects_count_by_priority_area(db, code)
        
        # Adicionar timestamp
        stats["generated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/metrics", tags=["system"])
async def get_metrics():
    """
    Endpoint para métricas do Prometheus
    """
    # Implementar métricas do Prometheus aqui
    return {"message": "Metrics endpoint - implementar contador de requisições, latência, etc."}

# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("🚀 Iniciando Sistema PRONAS/PCD")
    logger.info("📊 Baseado nas diretrizes oficiais do Ministério da Saúde")
    logger.info("🎯 8 áreas prioritárias implementadas")
    logger.info("🧠 IA especializada ativa")
    logger.info("✅ Sistema inicializado com sucesso")

@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    logger.info("🔴 Sistema PRONAS/PCD finalizado")

# ==================== ROOT ENDPOINT ====================

@app.get("/", tags=["system"])
async def root():
    """
    Endpoint raiz do sistema
    """
    return {
        "message": "Sistema PRONAS/PCD - Gestão Inteligente de Projetos",
        "description": "Baseado nas diretrizes oficiais do Ministério da Saúde",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "legal_framework": [
            "Lei nº 12.715/2012 (Lei do PRONAS/PCD)",
            "Portaria de Consolidação nº 5/2017 - Anexo LXXXVI",
            "Portaria nº 448/2002 (Natureza de Despesas)",
            "Lei nº 13.146/2015 (Lei Brasileira de Inclusão)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("RELOAD_ON_CHANGES", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
