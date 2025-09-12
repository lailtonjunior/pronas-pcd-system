"""
Model de Projeto - Sistema PRONAS/PCD
Conformidade: Art. 21-92 da Portaria de Consolidação nº 5/2017
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from models.base import BaseModel

class FieldOfAction(str, enum.Enum):
    """Campo de atuação do projeto - Art. 3"""
    MEDICO_ASSISTENCIAL = "medico_assistencial"
    FORMACAO = "formacao"
    PESQUISA = "pesquisa"

class ProjectStatus(str, enum.Enum):
    """Status do projeto no fluxo PRONAS/PCD"""
    DRAFT = "draft"                    # Rascunho
    SUBMITTED = "submitted"            # Submetido ao MS
    UNDER_REVIEW = "under_review"      # Em análise
    APPROVED = "approved"              # Aprovado pelo MS
    REJECTED = "rejected"              # Rejeitado
    PUBLISHED = "published"            # Publicado para captação
    FUNDRAISING = "fundraising"        # Em captação de recursos
    IN_EXECUTION = "in_execution"      # Em execução
    MONITORING = "monitoring"          # Em monitoramento
    COMPLETED = "completed"            # Concluído
    CANCELLED = "cancelled"            # Cancelado
    SUSPENDED = "suspended"            # Suspenso

class Project(BaseModel):
    __tablename__ = "projects"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    protocol_number = Column(String(50), unique=True, nullable=True)  # Protocolo MS
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=False)
    priority_area_id = Column(Integer, ForeignKey('priority_areas.id'), nullable=False)
    
    # Dados básicos do projeto
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    field_of_action = Column(Enum(FieldOfAction), nullable=False)
    
    # Objetivos (Art. 21)
    general_objective = Column(Text, nullable=False)
    specific_objectives = Column(JSON, nullable=False)  # Array de strings
    
    # Justificativa e metodologia
    justification = Column(Text, nullable=False)  # Min 500 caracteres
    target_audience = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    expected_results = Column(Text, nullable=True)
    sustainability_plan = Column(Text, nullable=True)
    
    # Localização de execução
    execution_city = Column(String(100), nullable=True)
    execution_state = Column(String(2), nullable=True)
    execution_address = Column(String(500), nullable=True)
    coverage_area = Column(String(100), nullable=True)  # municipal, estadual, regional, nacional
    
    # Beneficiários
    estimated_beneficiaries = Column(Integer, default=0)
    direct_beneficiaries = Column(Integer, default=0)
    indirect_beneficiaries = Column(Integer, default=0)
    beneficiaries_profile = Column(Text, nullable=True)
    
    # Orçamento e prazo
    budget_total = Column(Numeric(15, 2), nullable=False)
    budget_requested = Column(Numeric(15, 2), nullable=True)  # Valor solicitado ao PRONAS
    budget_approved = Column(Numeric(15, 2), nullable=True)   # Valor aprovado pelo MS
    budget_raised = Column(Numeric(15, 2), default=0)         # Valor captado
    budget_executed = Column(Numeric(15, 2), default=0)       # Valor executado
    
    timeline_months = Column(Integer, nullable=False)  # 6-48 meses
    
    # Status e datas importantes
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    submission_date = Column(DateTime, nullable=True)
    review_start_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    rejection_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    publication_date = Column(DateTime, nullable=True)  # Data publicação DOU
    
    # Captação de recursos
    fundraising_start_date = Column(DateTime, nullable=True)
    fundraising_end_date = Column(DateTime, nullable=True)
    fundraising_goal = Column(Numeric(15, 2), nullable=True)
    fundraising_percentage = Column(Numeric(5, 2), default=0)  # % captado
    
    # Execução
    execution_start_date = Column(DateTime, nullable=True)
    execution_end_date = Column(DateTime, nullable=True)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # Scores e avaliação
    technical_score = Column(Numeric(3, 2), default=0)      # 0-10
    compliance_score = Column(Numeric(3, 2), default=0)     # 0-10
    impact_score = Column(Numeric(3, 2), default=0)         # 0-10
    execution_score = Column(Numeric(3, 2), default=0)      # 0-10
    
    # Flags de controle
    requires_amendment = Column(Boolean, default=False)
    has_pending_reports = Column(Boolean, default=False)
    is_priority = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)  # Destaque no portal
    
    # Auditoria independente (obrigatória - Art. 92)
    audit_required = Column(Boolean, default=True)
    audit_company = Column(String(255), nullable=True)
    audit_report_date = Column(DateTime, nullable=True)
    audit_status = Column(String(50), nullable=True)
    
    # Parecer técnico
    technical_opinion = Column(Text, nullable=True)
    technical_opinion_date = Column(DateTime, nullable=True)
    technical_opinion_by = Column(String(255), nullable=True)
    
    # Relacionamentos
    institution = relationship("Institution", back_populates="projects")
    priority_area = relationship("PriorityArea", back_populates="projects")
    team_members = relationship("ProjectTeam", back_populates="project", cascade="all, delete-orphan")
    budget_items = relationship("ProjectBudget", back_populates="project", cascade="all, delete-orphan")
    goals = relationship("ProjectGoal", back_populates="project", cascade="all, delete-orphan")
    timeline = relationship("ProjectTimeline", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")
    monitoring_reports = relationship("ProjectMonitoring", back_populates="project", cascade="all, delete-orphan")
    amendments = relationship("ProjectAmendment", back_populates="project", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Project {self.title} ({self.status.value})>"
    
    def can_be_edited(self) -> bool:
        """Verifica se projeto pode ser editado"""
        return self.status in [ProjectStatus.DRAFT, ProjectStatus.REJECTED]
    
    def can_receive_funds(self) -> bool:
        """Verifica se pode receber recursos"""
        return self.status in [ProjectStatus.PUBLISHED, ProjectStatus.FUNDRAISING]

class ProjectTeam(BaseModel):
    """Equipe do projeto"""
    __tablename__ = "project_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    role = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=True)
    qualification = Column(Text, nullable=False)
    registry_number = Column(String(50), nullable=True)  # CRM, CRF, etc.
    weekly_hours = Column(Integer, nullable=False)
    monthly_salary = Column(Numeric(10, 2), nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="team_members")

class ProjectBudget(BaseModel):
    """Orçamento detalhado do projeto"""
    __tablename__ = "project_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    category = Column(String(50), nullable=False)  # pessoal, material_consumo, etc.
    subcategory = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    unit = Column(String(50), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_value = Column(Numeric(10, 2), nullable=False)
    total_value = Column(Numeric(12, 2), nullable=False)
    
    nature_expense_code = Column(String(10), nullable=True)  # Código Portaria 448/2002
    justification = Column(Text, nullable=True)
    
    # Execução
    executed_value = Column(Numeric(12, 2), default=0)
    execution_percentage = Column(Numeric(5, 2), default=0)
    
    project = relationship("Project", back_populates="budget_items")

class ProjectGoal(BaseModel):
    """Metas e indicadores do projeto"""
    __tablename__ = "project_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    indicator_name = Column(String(255), nullable=False)
    target_value = Column(Numeric(10, 2), nullable=False)
    measurement_method = Column(Text, nullable=False)
    frequency = Column(String(20), nullable=False)  # mensal, trimestral, etc.
    baseline_value = Column(Numeric(10, 2), nullable=True)
    
    # Acompanhamento
    current_value = Column(Numeric(10, 2), default=0)
    achievement_percentage = Column(Numeric(5, 2), default=0)
    last_measurement_date = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="goals")

class ProjectTimeline(BaseModel):
    """Cronograma do projeto"""
    __tablename__ = "project_timelines"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    phase_name = Column(String(255), nullable=False)
    start_month = Column(Integer, nullable=False)
    end_month = Column(Integer, nullable=False)
    deliverables = Column(JSON, nullable=True)  # Array de strings
    
    # Execução
    status = Column(String(20), default='pending')  # pending, in_progress, completed
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    completion_percentage = Column(Numeric(5, 2), default=0)
    
    project = relationship("Project", back_populates="timeline")

class ProjectDocument(BaseModel):
    """Documentos do projeto"""
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    document_type = Column(String(50), nullable=False)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), nullable=True)
    
    project = relationship("Project", back_populates="documents")

class ProjectMonitoring(BaseModel):
    """Monitoramento e acompanhamento do projeto"""
    __tablename__ = "project_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    report_type = Column(String(50), nullable=False)  # mensal, trimestral, final
    report_period = Column(String(20), nullable=False)  # 2024-Q1, 2024-01, etc.
    report_date = Column(DateTime, nullable=False)
    
    activities_performed = Column(Text, nullable=True)
    results_achieved = Column(Text, nullable=True)
    difficulties_encountered = Column(Text, nullable=True)
    corrective_actions = Column(Text, nullable=True)
    
    beneficiaries_attended = Column(Integer, default=0)
    budget_executed = Column(Numeric(12, 2), default=0)
    
    status = Column(String(20), default='pending')  # pending, submitted, approved, rejected
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_comments = Column(Text, nullable=True)
    
    project = relationship("Project", back_populates="monitoring_reports")

class ProjectAmendment(BaseModel):
    """Termos aditivos do projeto"""
    __tablename__ = "project_amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    amendment_number = Column(Integer, nullable=False)
    amendment_type = Column(String(50), nullable=False)  # prazo, valor, escopo
    justification = Column(Text, nullable=False)
    
    original_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    request_date = Column(DateTime, nullable=False)
    approval_date = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')
    
    project = relationship("Project", back_populates="amendments")