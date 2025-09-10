# database.py - Database Configuration for PRONAS/PCD System

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

def init_database():
    """
    Inicializar banco de dados com dados básicos
    """
    from models import PriorityArea, ExpenseNatureCode, SystemConfig, PRIORITY_AREAS_DATA
    
    db = SessionLocal()
    try:
        # Criar áreas prioritárias se não existirem
        if db.query(PriorityArea).count() == 0:
            for area_data in PRIORITY_AREAS_DATA:
                area = PriorityArea(**area_data)
                db.add(area)
        
        # Criar códigos de natureza de despesa (Portaria 448/2002)
        if db.query(ExpenseNatureCode).count() == 0:
            expense_codes = [
                {"code": "339030", "description": "Material de Consumo", "category": "CUSTEIO"},
                {"code": "339036", "description": "Outros Serviços de Terceiros - Pessoa Física", "category": "CUSTEIO"},
                {"code": "339037", "description": "Locação de Mão-de-Obra", "category": "CUSTEIO"},
                {"code": "339039", "description": "Outros Serviços de Terceiros - Pessoa Jurídica", "category": "CUSTEIO"},
                {"code": "449052", "description": "Equipamentos e Material Permanente", "category": "CAPITAL"},
                {"code": "449051", "description": "Obras e Instalações", "category": "CAPITAL"}
            ]
            
            for code_data in expense_codes:
                expense_code = ExpenseNatureCode(**code_data)
                db.add(expense_code)
        
        # Configurações do sistema
        if db.query(SystemConfig).count() == 0:
            configs = [
                {"key": "submission_period_days", "value": "45", "description": "Dias para submissão após portaria"},
                {"key": "max_projects_per_institution", "value": "3", "description": "Máximo de projetos por instituição"},
                {"key": "min_captacao_percentage", "value": "0.6", "description": "Captação mínima (60%)"},
                {"key": "max_captacao_percentage", "value": "1.2", "description": "Captação máxima (120%)"},
                {"key": "max_captacao_absolute", "value": "50000", "description": "Máximo absoluto para captação"},
                {"key": "current_year_budget", "value": "500000000", "description": "Orçamento do ano atual"},
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


# auth.py - Authentication and Authorization

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
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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


# crud.py - CRUD Operations for PRONAS/PCD System

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models import *
from schemas import *

# ==================== INSTITUTION CRUD ====================

def get_institution_by_id(db: Session, institution_id: int) -> Optional[Institution]:
    """Obter instituição por ID"""
    return db.query(Institution).filter(Institution.id == institution_id).first()

def get_institution_by_cnpj(db: Session, cnpj: str) -> Optional[Institution]:
    """Obter instituição por CNPJ"""
    return db.query(Institution).filter(Institution.cnpj == cnpj).first()

def get_institutions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[CredentialStatusEnum] = None
) -> List[Institution]:
    """Listar instituições com filtros"""
    query = db.query(Institution)
    
    if status:
        query = query.filter(Institution.credential_status == status)
    
    return query.offset(skip).limit(limit).all()

def get_institutions_count(
    db: Session, 
    status: Optional[CredentialStatusEnum] = None
) -> int:
    """Contar instituições"""
    query = db.query(Institution)
    
    if status:
        query = query.filter(Institution.credential_status == status)
    
    return query.count()

def create_institution_db(db: Session, institution: InstitutionCreate) -> Institution:
    """Criar nova instituição"""
    db_institution = Institution(**institution.dict())
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def update_institution_db(
    db: Session, 
    institution_id: int, 
    institution_update: InstitutionUpdate
) -> Optional[Institution]:
    """Atualizar instituição"""
    db_institution = get_institution_by_id(db, institution_id)
    if not db_institution:
        return None
    
    update_data = institution_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_institution, key, value)
    
    db.commit()
    db.refresh(db_institution)
    return db_institution

# ==================== PROJECT CRUD ====================

def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    """Obter projeto por ID com relacionamentos"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProjectStatusEnum] = None,
    institution_id: Optional[int] = None,
    field_of_action: Optional[FieldOfActionEnum] = None
) -> List[Project]:
    """Listar projetos com filtros"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    if institution_id:
        query = query.filter(Project.institution_id == institution_id)
    if field_of_action:
        query = query.filter(Project.field_of_action == field_of_action)
    
    return query.offset(skip).limit(limit).all()

def get_projects_by_institution(
    db: Session, 
    institution_id: int,
    status: Optional[ProjectStatusEnum] = None
) -> List[Project]:
    """Obter projetos de uma instituição"""
    query = db.query(Project).filter(Project.institution_id == institution_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    return query.all()

def get_projects_count(
    db: Session,
    status: Optional[ProjectStatusEnum] = None
) -> int:
    """Contar projetos"""
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    return query.count()

def get_projects_count_by_priority_area(db: Session, priority_area_code: str) -> int:
    """Contar projetos por área prioritária"""
    # Assumindo que existe mapeamento código -> ID
    area_ids = {"QSS": 1, "RPD": 2, "DDP": 3, "EPD": 4, "ITR": 5, "APE": 6, "TAA": 7, "APC": 8}
    area_id = area_ids.get(priority_area_code, 1)
    
    return db.query(Project).filter(Project.priority_area_id == area_id).count()

def create_project_db(db: Session, project: ProjectCreate) -> Project:
    """Criar novo projeto com relacionamentos"""
    # Criar projeto principal
    project_data = project.dict(exclude={
        'team_members', 'budget_items', 'goals', 'timeline'
    })
    db_project = Project(**project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Criar relacionamentos
    if project.team_members:
        for team_member in project.team_members:
            db_team_member = ProjectTeam(
                project_id=db_project.id,
                **team_member.dict()
            )
            db.add(db_team_member)
    
    if project.budget_items:
        for budget_item in project.budget_items:
            db_budget_item = ProjectBudget(
                project_id=db_project.id,
                **budget_item.dict()
            )
            db.add(db_budget_item)
    
    if project.goals:
        for goal in project.goals:
            db_goal = ProjectGoal(
                project_id=db_project.id,
                **goal.dict()
            )
            db.add(db_goal)
    
    if project.timeline:
        for phase in project.timeline:
            db_phase = ProjectTimeline(
                project_id=db_project.id,
                **phase.dict()
            )
            db.add(db_phase)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_status(
    db: Session, 
    project_id: int, 
    status: ProjectStatusEnum
) -> Optional[Project]:
    """Atualizar status do projeto"""
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    db_project.status = status
    if status == ProjectStatusEnum.SUBMITTED:
        db_project.submission_date = datetime.now()
    elif status == ProjectStatusEnum.APPROVED:
        db_project.approval_date = datetime.now()
    elif status == ProjectStatusEnum.IN_EXECUTION:
        db_project.execution_start_date = datetime.now()
    
    db.commit()
    db.refresh(db_project)
    return db_project

def get_total_budget_requested(db: Session) -> float:
    """Obter total de orçamento solicitado"""
    result = db.query(func.sum(Project.budget_total)).filter(
        Project.status.in_([
            ProjectStatusEnum.SUBMITTED, 
            ProjectStatusEnum.APPROVED,
            ProjectStatusEnum.IN_EXECUTION
        ])
    ).scalar()
    return float(result) if result else 0.0

def get_total_budget_approved(db: Session) -> float:
    """Obter total de orçamento aprovado"""
    result = db.query(func.sum(Project.budget_total)).filter(
        Project.status.in_([
            ProjectStatusEnum.APPROVED,
            ProjectStatusEnum.IN_EXECUTION,
            ProjectStatusEnum.COMPLETED
        ])
    ).scalar()
    return float(result) if result else 0.0

# ==================== MONITORING CRUD ====================

def get_project_monitoring_data(db: Session, project_id: int) -> List[Dict[str, Any]]:
    """Obter dados de monitoramento do projeto"""
    monitoring_entries = db.query(ProjectMonitoring).filter(
        ProjectMonitoring.project_id == project_id
    ).all()
    
    return [
        {
            "id": entry.id,
            "monitoring_date": entry.monitoring_date.isoformat(),
            "goal_id": entry.goal_id,
            "achieved_value": float(entry.achieved_value),
            "observations": entry.observations,
            "created_by": entry.created_by
        }
        for entry in monitoring_entries
    ]

def add_project_monitoring(
    db: Session, 
    project_id: int, 
    monitoring_data: Dict[str, Any]
) -> ProjectMonitoring:
    """Adicionar entrada de monitoramento"""
    db_monitoring = ProjectMonitoring(
        project_id=project_id,
        **monitoring_data
    )
    db.add(db_monitoring)
    db.commit()
    db.refresh(db_monitoring)
    return db_monitoring