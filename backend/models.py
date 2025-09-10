# backend/models.py - Modelos SQLAlchemy baseados na legislação PRONAS/PCD
"""
Modelos de dados baseados na Portaria de Consolidação nº 5/2017
Implementa todas as tabelas necessárias para o sistema PRONAS/PCD
"""

from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Boolean, ForeignKey, Enum, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# ==================== ENUMS ====================

class CredentialStatusEnum(str, enum.Enum):
    """Status de credenciamento das instituições"""
    PENDING = "pending"      # Pendente de análise
    ACTIVE = "active"        # Credenciada ativa
    INACTIVE = "inactive"    # Credenciamento suspenso
    EXPIRED = "expired"      # Credenciamento expirado
    REJECTED = "rejected"    # Credenciamento rejeitado

class InstitutionTypeEnum(str, enum.Enum):
    """Tipos de instituição elegíveis para PRONAS/PCD"""
    HOSPITAL = "hospital"
    APAE = "apae"
    ONG = "ong"
    FUNDACAO = "fundacao"
    ASSOCIACAO = "associacao"
    INSTITUTO = "instituto"
    COOPERATIVA = "cooperativa"
    OSCIP = "oscip"

class ProjectStatusEnum(str, enum.Enum):
    """Status dos projetos PRONAS/PCD"""
    DRAFT = "draft"                 # Rascunho
    SUBMITTED = "submitted"         # Submetido para análise
    UNDER_REVIEW = "under_review"   # Em análise
    APPROVED = "approved"           # Aprovado
    REJECTED = "rejected"           # Rejeitado
    IN_EXECUTION = "in_execution"   # Em execução
    COMPLETED = "completed"         # Concluído
    CANCELLED = "cancelled"         # Cancelado

class FieldOfActionEnum(str, enum.Enum):
    """Campos de atuação dos projetos (Art. 9º)"""
    MEDICO_ASSISTENCIAL = "medico_assistencial"    # Ações médico-assistenciais
    FORMACAO = "formacao"                          # Formação e capacitação
    PESQUISA = "pesquisa"                         # Pesquisa e desenvolvimento

class BudgetCategoryEnum(str, enum.Enum):
    """Categorias de orçamento baseadas na Portaria 448/2002"""
    PESSOAL = "pessoal"                           # 339036, 339037
    MATERIAL_CONSUMO = "material_consumo"         # 339030
    MATERIAL_PERMANENTE = "material_permanente"   # 449052
    DESPESAS_ADMINISTRATIVAS = "despesas_administrativas"  # 339039
    REFORMAS = "reformas"                         # 449051
    CAPTACAO_RECURSOS = "captacao_recursos"       # Máximo 5% ou R$ 50.000
    AUDITORIA = "auditoria"                       # Obrigatória

class MonitoringFrequencyEnum(str, enum.Enum):
    """Frequência de monitoramento"""
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

# ==================== MODELOS PRINCIPAIS ====================

class Institution(Base):
    """
    Instituições elegíveis para PRONAS/PCD
    Baseado nos requisitos de credenciamento (Art. 24)
    """
    __tablename__ = "institutions"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)              # Nome fantasia
    legal_name = Column(String(255), nullable=False)        # Razão social
    institution_type = Column(Enum(InstitutionTypeEnum), nullable=False)
    
    # Endereço
    cep = Column(String(9), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    
    # Contato
    phone = Column(String(20))
    email = Column(String(255), nullable=False)
    website = Column(String(255))
    
    # Responsáveis
    legal_representative = Column(String(255), nullable=False)
    legal_representative_cpf = Column(String(14))
    technical_responsible = Column(String(255))
    technical_responsible_registration = Column(String(50))  # CRM, CRF, etc.
    
    # Experiência e capacidade técnica
    experience_proof = Column(Text)                          # Comprovação de experiência
    services_offered = Column(Text)                         # Serviços oferecidos
    technical_capacity = Column(Text)                       # Capacidade técnica
    partnership_history = Column(Text)                      # Histórico de parcerias
    
    # Status de credenciamento
    credential_status = Column(Enum(CredentialStatusEnum), default=CredentialStatusEnum.PENDING)
    credential_date = Column(DateTime)                      # Data do credenciamento
    credential_expiry = Column(DateTime)                    # Validade do credenciamento
    credential_number = Column(String(50))                  # Número do credenciamento
    
    # Metadados
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String(255))
    
    # Relacionamentos
    projects = relationship("Project", back_populates="institution")
    documents = relationship("InstitutionDocument", back_populates="institution")

class Project(Base):
    """
    Projetos PRONAS/PCD
    Baseado na estrutura definida na Portaria
    """
    __tablename__ = "projects"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Classificação
    field_of_action = Column(Enum(FieldOfActionEnum), nullable=False)
    priority_area_id = Column(Integer, ForeignKey("priority_areas.id"), nullable=False)
    
    # Estrutura do projeto
    general_objective = Column(Text, nullable=False)
    specific_objectives = Column(JSON)                      # Array de objetivos específicos
    justification = Column(Text, nullable=False)           # Mínimo 500 caracteres
    target_audience = Column(Text)                         # Público-alvo
    methodology = Column(Text)                             # Metodologia
    expected_results = Column(Text)                        # Resultados esperados
    sustainability_plan = Column(Text)                     # Plano de sustentabilidade
    
    # Orçamento
    budget_total = Column(Decimal(15, 2), nullable=False)
    budget_captacao = Column(Decimal(15, 2))              # Valor para captação
    budget_captacao_percentage = Column(Decimal(5, 2))    # Percentual de captação
    
    # Cronograma
    timeline_months = Column(Integer, nullable=False)      # Prazo em meses (6-48)
    start_date = Column(Date)                             # Data de início prevista
    end_date = Column(Date)                               # Data de término prevista
    
    # Status e controle
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.DRAFT)
    submission_date = Column(DateTime)                     # Data de submissão
    approval_date = Column(DateTime)                       # Data de aprovação
    execution_start_date = Column(DateTime)                # Início da execução
    execution_end_date = Column(DateTime)                  # Fim da execução
    
    # Avaliação
    evaluation_score = Column(Decimal(5, 2))              # Score de avaliação
    compliance_score = Column(Decimal(5, 2))              # Score de conformidade
    reviewer_comments = Column(Text)                       # Comentários do avaliador
    
    # Metadados
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String(255))
    
    # Relacionamentos
    institution = relationship("Institution", back_populates="projects")
    priority_area = relationship("PriorityArea", back_populates="projects")
    team_members = relationship("ProjectTeam", back_populates="project")
    budget_items = relationship("ProjectBudget", back_populates="project")
    goals = relationship("ProjectGoal", back_populates="project")
    timeline = relationship("ProjectTimeline", back_populates="project")
    monitoring = relationship("ProjectMonitoring", back_populates="project")
    documents = relationship("ProjectDocument", back_populates="project")

class PriorityArea(Base):
    """
    Áreas prioritárias do PRONAS/PCD (Art. 10)
    """
    __tablename__ = "priority_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)  # QSS, RPD, DDP, etc.
    name = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON)                            # Requisitos específicos
    typical_actions = Column(JSON)                         # Ações típicas
    budget_guidelines = Column(JSON)                       # Diretrizes orçamentárias
    team_guidelines = Column(JSON)                         # Diretrizes de equipe
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    projects = relationship("Project", back_populates="priority_area")

class ProjectTeam(Base):
    """
    Equipe técnica dos projetos
    """
    __tablename__ = "project_team"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(255), nullable=False)             # Função na equipe
    name = Column(String(255), nullable=False)
    cpf = Column(String(14))
    qualification = Column(Text, nullable=False)           # Qualificação profissional
    registration_number = Column(String(50))               # Registro profissional
    weekly_hours = Column(Decimal(5, 2), nullable=False)  # Carga horária semanal
    monthly_salary = Column(Decimal(10, 2))               # Salário mensal
    start_date = Column(Date)
    end_date = Column(Date)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="team_members")

class ProjectBudget(Base):
    """
    Orçamento detalhado dos projetos
    Baseado na Portaria 448/2002
    """
    __tablename__ = "project_budget"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(Enum(BudgetCategoryEnum), nullable=False)
    subcategory = Column(String(255))                      # Subcategoria específica
    description = Column(Text, nullable=False)
    
    # Quantidade e valores
    unit = Column(String(50))                             # Unidade (mês, peça, etc.)
    quantity = Column(Decimal(10, 2), nullable=False)
    unit_value = Column(Decimal(12, 2), nullable=False)
    total_value = Column(Decimal(15, 2), nullable=False)
    
    # Classificação contábil
    nature_expense_code = Column(String(10))              # Código da natureza de despesa
    
    # Justificativa
    justification = Column(Text)                          # Justificativa do item
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="budget_items")

class ProjectGoal(Base):
    """
    Metas e indicadores dos projetos
    """
    __tablename__ = "project_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    indicator_name = Column(String(255), nullable=False)
    target_value = Column(Decimal(15, 2), nullable=False)
    measurement_method = Column(Text, nullable=False)
    frequency = Column(Enum(MonitoringFrequencyEnum), nullable=False)
    baseline_value = Column(Decimal(15, 2))               # Valor de baseline
    current_value = Column(Decimal(15, 2))                # Valor atual
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="goals")

class ProjectTimeline(Base):
    """
    Cronograma dos projetos
    """
    __tablename__ = "project_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(String(255), nullable=False)
    start_month = Column(Integer, nullable=False)         # Mês de início (1-48)
    end_month = Column(Integer, nullable=False)           # Mês de fim (1-48)
    deliverables = Column(JSON)                           # Array de entregas
    status = Column(String(50), default="planned")        # planned, in_progress, completed
    completion_percentage = Column(Decimal(5, 2))         # % de conclusão
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="timeline")

class ProjectMonitoring(Base):
    """
    Monitoramento dos projetos
    """
    __tablename__ = "project_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("project_goals.id"))
    monitoring_date = Column(DateTime, nullable=False)
    achieved_value = Column(Decimal(15, 2), nullable=False)
    observations = Column(Text)
    challenges = Column(Text)                             # Dificuldades encontradas
    corrective_actions = Column(Text)                     # Ações corretivas
    created_by = Column(String(255))
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="monitoring")

# ==================== MODELOS DE SUPORTE ====================

class ExpenseNatureCode(Base):
    """
    Códigos de natureza de despesa (Portaria 448/2002)
    """
    __tablename__ = "expense_nature_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)  # Ex: 339030
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)           # CUSTEIO ou CAPITAL
    subcategory = Column(String(100))
    applicable_to = Column(JSON)                           # Array de categorias aplicáveis
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())

class InstitutionDocument(Base):
    """
    Documentos das instituições
    """
    __tablename__ = "institution_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    document_type = Column(String(100), nullable=False)    # estatuto, ata, cnpj, etc.
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    upload_date = Column(DateTime, server_default=func.now())
    uploaded_by = Column(String(255))
    verified = Column(Boolean, default=False)
    
    # Relacionamentos
    institution = relationship("Institution", back_populates="documents")

class ProjectDocument(Base):
    """
    Documentos dos projetos
    """
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    upload_date = Column(DateTime, server_default=func.now())
    uploaded_by = Column(String(255))
    
    # Relacionamentos
    project = relationship("Project", back_populates="documents")

class RegulatoryFramework(Base):
    """
    Marco regulatório e legislação
    """
    __tablename__ = "regulatory_framework"
    
    id = Column(Integer, primary_key=True, index=True)
    law_type = Column(String(50), nullable=False)          # Lei, Decreto, Portaria
    law_number = Column(String(50), nullable=False)
    law_year = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)                                 # Conteúdo da lei
    effective_date = Column(Date)
    revoked_date = Column(Date)
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())

class SystemConfig(Base):
    """
    Configurações do sistema
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=False)
    description = Column(String(255))
    data_type = Column(String(20), default="string")       # string, integer, boolean, json
    category = Column(String(50), default="general")       # general, pronas, ai, etc.
    editable = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class AuditLog(Base):
    """
    Log de auditoria do sistema
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(255))
    action = Column(String(100), nullable=False)           # CREATE, READ, UPDATE, DELETE
    entity_type = Column(String(100))                      # Institution, Project, etc.
    entity_id = Column(Integer)
    old_values = Column(JSON)                              # Valores anteriores
    new_values = Column(JSON)                              # Novos valores
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, server_default=func.now())

# ==================== DADOS INICIAIS ====================

PRIORITY_AREAS_DATA = [
    {
        "code": "QSS",
        "name": "Qualificação de serviços de saúde",
        "description": "Adequação da ambiência de estabelecimentos de saúde que prestam atendimento à pessoa com deficiência",
        "active": True
    },
    {
        "code": "RPD", 
        "name": "Reabilitação/habilitação da pessoa com deficiência",
        "description": "Ações de reabilitação e habilitação da pessoa com deficiência",
        "active": True
    },
    {
        "code": "DDP",
        "name": "Diagnóstico diferencial da pessoa com deficiência",
        "description": "Diagnóstico diferencial da pessoa com deficiência", 
        "active": True
    },
    {
        "code": "EPD",
        "name": "Identificação e estimulação precoce das deficiências",
        "description": "Identificação e estimulação precoce de deficiências em crianças de 0 a 3 anos",
        "active": True
    },
    {
        "code": "ITR",
        "name": "Inserção e reinserção no trabalho",
        "description": "Adaptação, inserção e reinserção da pessoa com deficiência no mercado de trabalho",
        "active": True
    },
    {
        "code": "APE",
        "name": "Apoio à saúde por meio de práticas esportivas",
        "description": "Atividades físicas e esportivas adaptadas para pessoas com deficiência",
        "active": True
    },
    {
        "code": "TAA",
        "name": "Terapia assistida por animais",
        "description": "Terapia assistida por animais (TAA) como complemento terapêutico",
        "active": True
    },
    {
        "code": "APC", 
        "name": "Apoio à saúde por produção artística e cultural",
        "description": "Atividades artísticas e culturais como apoio à saúde da pessoa com deficiência",
        "active": True
    }
]

EXPENSE_NATURE_CODES_DATA = [
    {"code": "339030", "description": "Material de Consumo", "category": "CUSTEIO"},
    {"code": "339036", "description": "Outros Serviços de Terceiros - Pessoa Física", "category": "CUSTEIO"},
    {"code": "339037", "description": "Locação de Mão-de-Obra", "category": "CUSTEIO"},
    {"code": "339039", "description": "Outros Serviços de Terceiros - Pessoa Jurídica", "category": "CUSTEIO"},
    {"code": "449051", "description": "Obras e Instalações", "category": "CAPITAL"},
    {"code": "449052", "description": "Equipamentos e Material Permanente", "category": "CAPITAL"}
]

REGULATORY_FRAMEWORK_DATA = [
    {
        "law_type": "Lei",
        "law_number": "12.715",
        "law_year": 2012,
        "title": "Lei do PRONAS/PCD",
        "description": "Altera a Lei no 9.250, de 26 de dezembro de 1995, para dispor sobre os programmas de apoio à atenção oncológica e à atenção da saúde da pessoa com deficiência",
        "active": True
    },
    {
        "law_type": "Portaria",
        "law_number": "5",
        "law_year": 2017,
        "title": "Portaria de Consolidação nº 5/2017",
        "description": "Consolidação das normas sobre as ações e os serviços de saúde do Sistema Único de Saúde",
        "active": True
    },
    {
        "law_type": "Portaria",
        "law_number": "448",
        "law_year": 2002,
        "title": "Portaria STN nº 448/2002",
        "description": "Divulga o detalhamento das naturezas de despesas",
        "active": True
    },
    {
        "law_type": "Lei",
        "law_number": "13.146",
        "law_year": 2015,
        "title": "Lei Brasileira de Inclusão",
        "description": "Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência)",
        "active": True
    }
]