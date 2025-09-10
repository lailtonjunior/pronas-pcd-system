# backend/database.py - Configuração de banco de dados
"""
Configuração de banco de dados PostgreSQL para o Sistema PRONAS/PCD
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# Configurações do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pronas_user:pronas_password@localhost:5432/pronas_pcd_db")

# Para desenvolvimento local com Docker
if "localhost" in DATABASE_URL:
    DATABASE_URL = "postgresql://pronas_user:pronas_password@localhost:5432/pronas_pcd_db"

# Criar engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=30,
    echo=os.getenv("DB_ECHO", "false").lower() == "true"
)

# Criar sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """
    Inicializar banco de dados com dados básicos
    """
    from .models import (
        PriorityArea, ExpenseNatureCode, SystemConfig, RegulatoryFramework,
        PRIORITY_AREAS_DATA, EXPENSE_NATURE_CODES_DATA, REGULATORY_FRAMEWORK_DATA
    )
    
    db = SessionLocal()
    try:
        # Criar áreas prioritárias se não existirem
        if db.query(PriorityArea).count() == 0:
            for area_data in PRIORITY_AREAS_DATA:
                area = PriorityArea(**area_data)
                db.add(area)
        
        # Criar códigos de natureza de despesa (Portaria 448/2002)
        if db.query(ExpenseNatureCode).count() == 0:
            for code_data in EXPENSE_NATURE_CODES_DATA:
                expense_code = ExpenseNatureCode(**code_data)
                db.add(expense_code)
        
        # Criar marco regulatório
        if db.query(RegulatoryFramework).count() == 0:
            for law_data in REGULATORY_FRAMEWORK_DATA:
                law = RegulatoryFramework(**law_data)
                db.add(law)
        
        # Configurações do sistema
        if db.query(SystemConfig).count() == 0:
            configs = [
                {"key": "submission_period_days", "value": "45", "description": "Dias para submissão após portaria"},
                {"key": "max_projects_per_institution", "value": "3", "description": "Máximo de projetos por instituição"},
                {"key": "min_captacao_percentage", "value": "0.6", "description": "Captação mínima (60%)"},
                {"key": "max_captacao_percentage", "value": "1.2", "description": "Captação máxima (120%)"},
                {"key": "max_captacao_absolute", "value": "50000", "description": "Máximo absoluto para captação"},
                {"key": "current_year_budget", "value": "500000000", "description": "Orçamento do ano atual"},
                {"key": "credentialing_months", "value": "6,7", "description": "Meses de credenciamento"},
                {"key": "min_timeline_months", "value": "6", "description": "Prazo mínimo do projeto"},
                {"key": "max_timeline_months", "value": "48", "description": "Prazo máximo do projeto"}
            ]
            
            for config_data in configs:
                config = SystemConfig(**config_data)
                db.add(config)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

---

# backend/auth.py - Sistema de autenticação
"""
Sistema de autenticação e autorização para o PRONAS/PCD
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

# Configurações de segurança
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "pronas-pcd-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, username: str) -> bool:
    """
    Verificar senha do usuário
    Implementação básica - em produção usar banco de dados
    """
    # Usuários padrão para desenvolvimento
    users = {
        "admin": "$2b$12$EixZaYVK1e.JSqU7lR1dZ.eJz.ay2./d2B/2A.KjH2A.8nZk2KzKy",  # password
        "user": "$2b$12$EixZaYVK1e.JSqU7lR1dZ.eJz.ay2./d2B/2A.KjH2A.8nZk2KzKy",   # password
        "gestor": "$2b$12$EixZaYVK1e.JSqU7lR1dZ.eJz.ay2./d2B/2A.KjH2A.8nZk2KzKy" # password
    }
    
    if username not in users:
        return False
    
    return pwd_context.verify(plain_password, users[username])

def get_password_hash(password: str) -> str:
    """
    Gerar hash da senha
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Criar token JWT de acesso
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verificar validade do token JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Obter usuário atual baseado no token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = verify_token(token)
    if user is None:
        raise credentials_exception
    
    return user

def get_user_permissions(username: str) -> list:
    """
    Obter permissões do usuário
    """
    permissions = {
        "admin": ["read", "write", "delete", "manage_users", "manage_system"],
        "gestor": ["read", "write", "manage_projects", "generate_reports"],
        "user": ["read", "write", "create_projects"]
    }
    return permissions.get(username, ["read"])

def require_permission(permission: str):
    """
    Decorator para exigir permissão específica
    """
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = get_user_permissions(current_user.get("username"))
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission}"
            )
        return current_user
    return permission_checker

---

# backend/crud.py - Operações CRUD
"""
Operações CRUD para o Sistema PRONAS/PCD
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from . import models, schemas

# ==================== INSTITUTION CRUD ====================

def get_institution_by_id(db: Session, institution_id: int) -> Optional[models.Institution]:
    """Obter instituição por ID"""
    return db.query(models.Institution).filter(models.Institution.id == institution_id).first()

def get_institution_by_cnpj(db: Session, cnpj: str) -> Optional[models.Institution]:
    """Obter instituição por CNPJ"""
    return db.query(models.Institution).filter(models.Institution.cnpj == cnpj).first()

def get_institutions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[models.CredentialStatusEnum] = None,
    institution_type: Optional[models.InstitutionTypeEnum] = None,
    state: Optional[str] = None,
    search: Optional[str] = None
) -> List[models.Institution]:
    """Listar instituições com filtros"""
    query = db.query(models.Institution)
    
    if status:
        query = query.filter(models.Institution.credential_status == status)
    
    if institution_type:
        query = query.filter(models.Institution.institution_type == institution_type)
    
    if state:
        query = query.filter(models.Institution.state == state)
    
    if search:
        search_filter = or_(
            models.Institution.name.ilike(f"%{search}%"),
            models.Institution.legal_name.ilike(f"%{search}%"),
            models.Institution.cnpj.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()

def get_institutions_count(
    db: Session, 
    status: Optional[models.CredentialStatusEnum] = None
) -> int:
    """Contar instituições"""
    query = db.query(models.Institution)
    
    if status:
        query = query.filter(models.Institution.credential_status == status)
    
    return query.count()

def create_institution_db(db: Session, institution: schemas.InstitutionCreate) -> models.Institution:
    """Criar nova instituição"""
    db_institution = models.Institution(**institution.dict())
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def update_institution_db(
    db: Session, 
    institution_id: int, 
    institution_update: schemas.InstitutionUpdate
) -> Optional[models.Institution]:
    """Atualizar instituição"""
    db_institution = get_institution_by_id(db, institution_id)
    if not db_institution:
        return None
    
    update_data = institution_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_institution, key, value)
    
    db_institution.updated_at = datetime.now()
    db.commit()
    db.refresh(db_institution)
    return db_institution

def delete_institution_db(db: Session, institution_id: int) -> bool:
    """Deletar instituição"""
    db_institution = get_institution_by_id(db, institution_id)
    if not db_institution:
        return False
    
    db.delete(db_institution)
    db.commit()
    return True

# ==================== PROJECT CRUD ====================

def get_project_by_id(db: Session, project_id: int) -> Optional[models.Project]:
    """Obter projeto por ID com relacionamentos"""
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.ProjectStatusEnum] = None,
    institution_id: Optional[int] = None,
    field_of_action: Optional[models.FieldOfActionEnum] = None,
    priority_area_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[models.Project]:
    """Listar projetos com filtros"""
    query = db.query(models.Project)
    
    if status:
        query = query.filter(models.Project.status == status)
    if institution_id:
        query = query.filter(models.Project.institution_id == institution_id)
    if field_of_action:
        query = query.filter(models.Project.field_of_action == field_of_action)
    if priority_area_id:
        query = query.filter(models.Project.priority_area_id == priority_area_id)
    
    if search:
        search_filter = or_(
            models.Project.title.ilike(f"%{search}%"),
            models.Project.description.ilike(f"%{search}%"),
            models.Project.general_objective.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()

def get_projects_by_institution(
    db: Session, 
    institution_id: int,
    status: Optional[models.ProjectStatusEnum] = None
) -> List[models.Project]:
    """Obter projetos de uma instituição"""
    query = db.query(models.Project).filter(models.Project.institution_id == institution_id)
    
    if status:
        query = query.filter(models.Project.status == status)
    
    return query.all()

def get_projects_count(
    db: Session,
    status: Optional[models.ProjectStatusEnum] = None,
    institution_id: Optional[int] = None
) -> int:
    """Contar projetos"""
    query = db.query(models.Project)
    
    if status:
        query = query.filter(models.Project.status == status)
    
    if institution_id:
        query = query.filter(models.Project.institution_id == institution_id)
    
    return query.count()

def get_projects_count_by_priority_area(db: Session, priority_area_id: int) -> int:
    """Contar projetos por área prioritária"""
    return db.query(models.Project).filter(
        models.Project.priority_area_id == priority_area_id
    ).count()

def create_project_db(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Criar novo projeto com relacionamentos"""
    # Criar projeto principal
    project_data = project.dict(exclude={
        'team_members', 'budget_items', 'goals', 'timeline'
    })
    db_project = models.Project(**project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Criar relacionamentos
    if project.team_members:
        for team_member in project.team_members:
            db_team_member = models.ProjectTeam(
                project_id=db_project.id,
                **team_member.dict()
            )
            db.add(db_team_member)
    
    if project.budget_items:
        for budget_item in project.budget_items:
            db_budget_item = models.ProjectBudget(
                project_id=db_project.id,
                **budget_item.dict()
            )
            db.add(db_budget_item)
    
    if project.goals:
        for goal in project.goals:
            db_goal = models.ProjectGoal(
                project_id=db_project.id,
                **goal.dict()
            )
            db.add(db_goal)
    
    if project.timeline:
        for phase in project.timeline:
            db_phase = models.ProjectTimeline(
                project_id=db_project.id,
                **phase.dict()
            )
            db.add(db_phase)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_db(
    db: Session, 
    project_id: int, 
    project_update: schemas.ProjectUpdate
) -> Optional[models.Project]:
    """Atualizar projeto"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_status(
    db: Session, 
    project_id: int, 
    status: models.ProjectStatusEnum,
    comment: Optional[str] = None
) -> Optional[models.Project]:
    """Atualizar status do projeto"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    db_project.status = status
    if comment:
        db_project.reviewer_comments = comment
        
    if status == models.ProjectStatusEnum.SUBMITTED:
        db_project.submission_date = datetime.now()
    elif status == models.ProjectStatusEnum.APPROVED:
        db_project.approval_date = datetime.now()
    elif status == models.ProjectStatusEnum.IN_EXECUTION:
        db_project.execution_start_date = datetime.now()
    elif status == models.ProjectStatusEnum.COMPLETED:
        db_project.execution_end_date = datetime.now()
    
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project_db(db: Session, project_id: int) -> bool:
    """Deletar projeto"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return False
    
    # Deletar relacionamentos primeiro
    db.query(models.ProjectTeam).filter(models.ProjectTeam.project_id == project_id).delete()
    db.query(models.ProjectBudget).filter(models.ProjectBudget.project_id == project_id).delete()
    db.query(models.ProjectGoal).filter(models.ProjectGoal.project_id == project_id).delete()
    db.query(models.ProjectTimeline).filter(models.ProjectTimeline.project_id == project_id).delete()
    db.query(models.ProjectMonitoring).filter(models.ProjectMonitoring.project_id == project_id).delete()
    
    # Deletar projeto
    db.delete(db_project)
    db.commit()
    return True

def get_total_budget_requested(db: Session) -> float:
    """Obter total de orçamento solicitado"""
    result = db.query(func.sum(models.Project.budget_total)).filter(
        models.Project.status.in_([
            models.ProjectStatusEnum.SUBMITTED, 
            models.ProjectStatusEnum.APPROVED,
            models.ProjectStatusEnum.IN_EXECUTION
        ])
    ).scalar()
    return float(result) if result else 0.0

def get_total_budget_approved(db: Session) -> float:
    """Obter total de orçamento aprovado"""
    result = db.query(func.sum(models.Project.budget_total)).filter(
        models.Project.status.in_([
            models.ProjectStatusEnum.APPROVED,
            models.ProjectStatusEnum.IN_EXECUTION,
            models.ProjectStatusEnum.COMPLETED
        ])
    ).scalar()
    return float(result) if result else 0.0

# ==================== PRIORITY AREA CRUD ====================

def get_priority_areas(db: Session, active_only: bool = True) -> List[models.PriorityArea]:
    """Listar áreas prioritárias"""
    query = db.query(models.PriorityArea)
    if active_only:
        query = query.filter(models.PriorityArea.active == True)
    return query.all()

def get_priority_area_by_id(db: Session, area_id: int) -> Optional[models.PriorityArea]:
    """Obter área prioritária por ID"""
    return db.query(models.PriorityArea).filter(models.PriorityArea.id == area_id).first()

def get_priority_area_by_code(db: Session, code: str) -> Optional[models.PriorityArea]:
    """Obter área prioritária por código"""
    return db.query(models.PriorityArea).filter(models.PriorityArea.code == code).first()

# ==================== MONITORING CRUD ====================

def get_project_monitoring_data(db: Session, project_id: int) -> List[models.ProjectMonitoring]:
    """Obter dados de monitoramento do projeto"""
    return db.query(models.ProjectMonitoring).filter(
        models.ProjectMonitoring.project_id == project_id
    ).order_by(models.ProjectMonitoring.monitoring_date.desc()).all()

def add_project_monitoring(
    db: Session, 
    project_id: int, 
    monitoring_data: schemas.ProjectMonitoringCreate,
    created_by: str
) -> models.ProjectMonitoring:
    """Adicionar entrada de monitoramento"""
    db_monitoring = models.ProjectMonitoring(
        project_id=project_id,
        created_by=created_by,
        **monitoring_data.dict()
    )
    db.add(db_monitoring)
    db.commit()
    db.refresh(db_monitoring)
    return db_monitoring

# ==================== DOCUMENT CRUD ====================

def create_institution_document(
    db: Session, 
    institution_id: int, 
    document: schemas.InstitutionDocumentCreate,
    uploaded_by: str
) -> models.InstitutionDocument:
    """Criar documento da instituição"""
    db_document = models.InstitutionDocument(
        institution_id=institution_id,
        uploaded_by=uploaded_by,
        **document.dict()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def create_project_document(
    db: Session, 
    project_id: int, 
    document: schemas.ProjectDocumentCreate,
    uploaded_by: str
) -> models.ProjectDocument:
    """Criar documento do projeto"""
    db_document = models.ProjectDocument(
        project_id=project_id,
        uploaded_by=uploaded_by,
        **document.dict()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# ==================== SYSTEM CONFIG CRUD ====================

def get_system_config(db: Session, key: str) -> Optional[models.SystemConfig]:
    """Obter configuração do sistema"""
    return db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()

def get_all_system_configs(db: Session) -> List[models.SystemConfig]:
    """Obter todas as configurações do sistema"""
    return db.query(models.SystemConfig).all()

def update_system_config(db: Session, key: str, value: str) -> Optional[models.SystemConfig]:
    """Atualizar configuração do sistema"""
    config = get_system_config(db, key)
    if config:
        config.value = value
        config.updated_at = datetime.now()
        db.commit()
        db.refresh(config)
    return config

# ==================== AUDIT LOG CRUD ====================

def create_audit_log(
    db: Session,
    user: str,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> models.AuditLog:
    """Criar log de auditoria"""
    audit_log = models.AuditLog(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[models.AuditLog]:
    """Obter logs de auditoria"""
    query = db.query(models.AuditLog)
    
    if user:
        query = query.filter(models.AuditLog.user == user)
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    if start_date:
        query = query.filter(models.AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(models.AuditLog.timestamp <= end_date)
    
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# ==================== STATISTICS CRUD ====================

def get_dashboard_statistics(db: Session) -> Dict[str, Any]:
    """Obter estatísticas para o dashboard"""
    
    # Estatísticas de instituições
    institutions_stats = {
        "total": db.query(models.Institution).count(),
        "active": db.query(models.Institution).filter(
            models.Institution.credential_status == models.CredentialStatusEnum.ACTIVE
        ).count(),
        "pending": db.query(models.Institution).filter(
            models.Institution.credential_status == models.CredentialStatusEnum.PENDING
        ).count(),
        "inactive": db.query(models.Institution).filter(
            models.Institution.credential_status == models.CredentialStatusEnum.INACTIVE
        ).count()
    }
    
    # Estatísticas de projetos
    projects_stats = {
        "total": db.query(models.Project).count(),
        "draft": db.query(models.Project).filter(
            models.Project.status == models.ProjectStatusEnum.DRAFT
        ).count(),
        "submitted": db.query(models.Project).filter(
            models.Project.status == models.ProjectStatusEnum.SUBMITTED
        ).count(),
        "approved": db.query(models.Project).filter(
            models.Project.status == models.ProjectStatusEnum.APPROVED
        ).count(),
        "in_execution": db.query(models.Project).filter(
            models.Project.status == models.ProjectStatusEnum.IN_EXECUTION
        ).count(),
        "completed": db.query(models.Project).filter(
            models.Project.status == models.ProjectStatusEnum.COMPLETED
        ).count()
    }
    
    # Estatísticas orçamentárias
    budget_stats = {
        "total_requested": get_total_budget_requested(db),
        "total_approved": get_total_budget_approved(db)
    }
    
    # Estatísticas por área prioritária
    priority_area_stats = {}
    priority_areas = get_priority_areas(db)
    for area in priority_areas:
        priority_area_stats[area.code] = get_projects_count_by_priority_area(db, area.id)
    
    # Estatísticas por estado
    state_stats = db.query(
        models.Institution.state,
        func.count(models.Institution.id).label('count')
    ).group_by(models.Institution.state).all()
    
    state_stats_dict = {state: count for state, count in state_stats}
    
    return {
        "institutions": institutions_stats,
        "projects": projects_stats,
        "budget": budget_stats,
        "by_priority_area": priority_area_stats,
        "by_state": state_stats_dict,
        "generated_at": datetime.now().isoformat()
    }