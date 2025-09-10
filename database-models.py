# models.py - Database Models for PRONAS/PCD System
# Based on Portaria de Consolidação nº 05/2017 - Anexo LXXXVI

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Decimal, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

# Enums baseados na legislação
class InstitutionType(enum.Enum):
    HOSPITAL = "hospital"
    APAE = "apae"
    ONG = "ong"
    FUNDACAO = "fundacao"
    ASSOCIACAO = "associacao"
    INSTITUTO = "instituto"

class CredentialStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REJECTED = "rejected"

class FieldOfAction(enum.Enum):
    MEDICO_ASSISTENCIAL = "medico_assistencial"
    FORMACAO = "formacao"
    PESQUISA = "pesquisa"

class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BudgetCategory(enum.Enum):
    PESSOAL = "pessoal"
    MATERIAL_CONSUMO = "material_consumo"
    MATERIAL_PERMANENTE = "material_permanente"
    DESPESAS_ADMINISTRATIVAS = "despesas_administrativas"
    REFORMAS = "reformas"
    CAPTACAO_RECURSOS = "captacao_recursos"
    AUDITORIA = "auditoria"
    OUTROS = "outros"

class MonitoringFrequency(enum.Enum):
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

# Tabela 1: INSTITUTIONS
class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=False)
    institution_type = Column(Enum(InstitutionType), nullable=False)
    cep = Column(String(9), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    phone = Column(String(15))
    email = Column(String(255), nullable=False)
    legal_representative = Column(String(255), nullable=False)
    technical_responsible = Column(String(255))
    experience_proof = Column(Text)
    credential_status = Column(Enum(CredentialStatus), default=CredentialStatus.PENDING)
    credential_date = Column(DateTime)
    credential_expiry = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    projects = relationship("Project", back_populates="institution")

# Tabela 2: PRIORITY_AREAS (Art. 10 da Portaria)
class PriorityArea(Base):
    __tablename__ = "priority_areas"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON)  # Requisitos específicos da área
    active = Column(Boolean, default=True)
    
    # Relacionamentos
    projects = relationship("Project", back_populates="priority_area_ref")

# Tabela 3: EXPENSE_NATURE_CODES (Portaria 448/2002)
class ExpenseNatureCode(Base):
    __tablename__ = "expense_nature_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(100))
    active = Column(Boolean, default=True)

# Tabela 4: PROJECTS
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    field_of_action = Column(Enum(FieldOfAction), nullable=False)
    priority_area_id = Column(Integer, ForeignKey("priority_areas.id"), nullable=False)
    general_objective = Column(Text, nullable=False)
    specific_objectives = Column(JSON, nullable=False)  # Lista de objetivos específicos
    justification = Column(Text, nullable=False)  # Mínimo 500 caracteres
    target_audience = Column(Text)
    methodology = Column(Text)
    expected_results = Column(Text)
    budget_total = Column(Decimal(15, 2), nullable=False)
    timeline_months = Column(Integer, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    submission_date = Column(DateTime)
    approval_date = Column(DateTime)
    execution_start_date = Column(DateTime)
    execution_end_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    institution = relationship("Institution", back_populates="projects")
    priority_area_ref = relationship("PriorityArea", back_populates="projects")
    budget_items = relationship("ProjectBudget", back_populates="project")
    team_members = relationship("ProjectTeam", back_populates="project")
    goals = relationship("ProjectGoal", back_populates="project")
    timeline = relationship("ProjectTimeline", back_populates="project")
    documents = relationship("ProjectDocument", back_populates="project")
    monitoring = relationship("ProjectMonitoring", back_populates="project")

# Tabela 5: PROJECT_BUDGET
class ProjectBudget(Base):
    __tablename__ = "project_budget"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(Enum(BudgetCategory), nullable=False)
    subcategory = Column(String(100))
    description = Column(String(255), nullable=False)
    unit = Column(String(50))
    quantity = Column(Decimal(10, 2), nullable=False)
    unit_value = Column(Decimal(15, 2), nullable=False)
    total_value = Column(Decimal(15, 2), nullable=False)
    nature_expense_code = Column(String(20))  # Baseado na Portaria 448/2002
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="budget_items")

# Tabela 6: PROJECT_TEAM
class ProjectTeam(Base):
    __tablename__ = "project_team"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    cpf = Column(String(14))
    qualification = Column(Text, nullable=False)
    weekly_hours = Column(Integer, nullable=False)
    monthly_salary = Column(Decimal(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="team_members")

# Tabela 7: PROJECT_GOALS
class ProjectGoal(Base):
    __tablename__ = "project_goals"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    indicator_name = Column(String(255), nullable=False)
    target_value = Column(Decimal(15, 2), nullable=False)
    measurement_method = Column(Text, nullable=False)
    frequency = Column(Enum(MonitoringFrequency), nullable=False)
    baseline_value = Column(Decimal(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="goals")
    monitoring_entries = relationship("ProjectMonitoring", back_populates="goal")

# Tabela 8: PROJECT_TIMELINE
class ProjectTimeline(Base):
    __tablename__ = "project_timeline"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(String(255), nullable=False)
    start_month = Column(Integer, nullable=False)  # Mês de início (1-N)
    end_month = Column(Integer, nullable=False)    # Mês de fim (1-N)
    deliverables = Column(JSON)  # Lista de entregáveis da fase
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="timeline")

# Tabela 9: PROJECT_DOCUMENTS
class ProjectDocument(Base):
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # estatuto, ata, cnpj, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String(255))
    
    # Relacionamentos
    project = relationship("Project", back_populates="documents")

# Tabela 10: PROJECT_MONITORING
class ProjectMonitoring(Base):
    __tablename__ = "project_monitoring"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("project_goals.id"), nullable=False)
    monitoring_date = Column(DateTime, nullable=False)
    achieved_value = Column(Decimal(15, 2), nullable=False)
    observations = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="monitoring")
    goal = relationship("ProjectGoal", back_populates="monitoring_entries")

# Tabela 11: REGULATORY_FRAMEWORK
class RegulatoryFramework(Base):
    __tablename__ = "regulatory_framework"
    
    id = Column(Integer, primary_key=True)
    law_decree_type = Column(String(50), nullable=False)  # lei, decreto, portaria
    number = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    full_text = Column(Text)
    status = Column(String(20), default="active")  # active, revoked, superseded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Tabela para dados de configuração do sistema
class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Dados iniciais das áreas prioritárias (Art. 10 da Portaria)
PRIORITY_AREAS_DATA = [
    {
        "code": "QSS", 
        "name": "Qualificação de serviços de saúde", 
        "description": "Por meio da adequação da ambiência de estabelecimentos"
    },
    {
        "code": "RPD", 
        "name": "Reabilitação/habilitação da pessoa com deficiência", 
        "description": "Ações de reabilitação e habilitação de pessoas com deficiência"
    },
    {
        "code": "DDP", 
        "name": "Diagnóstico diferencial da pessoa com deficiência", 
        "description": "Diagnóstico especializado e diferencial"
    },
    {
        "code": "EPD", 
        "name": "Identificação e estimulação precoce das deficiências", 
        "description": "Detecção e intervenção precoce"
    },
    {
        "code": "ITR", 
        "name": "Adaptação, inserção e reinserção da pessoa com deficiência no trabalho", 
        "description": "Inclusão e reinclusão no mercado de trabalho"
    },
    {
        "code": "APE", 
        "name": "Apoio a saúde por meio de práticas esportivas", 
        "description": "Atividades esportivas como apoio à saúde"
    },
    {
        "code": "TAA", 
        "name": "Apoio a saúde por meio de terapia assistida por animais (TAA)", 
        "description": "Terapia com animais como complemento ao tratamento"
    },
    {
        "code": "APC", 
        "name": "Apoio a saúde por meio de produção artística e cultural", 
        "description": "Atividades artísticas e culturais como apoio à saúde"
    }
]