# schemas.py - Pydantic Schemas for PRONAS/PCD System
# Based on official PRONAS/PCD guidelines

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Enums para validação
class InstitutionTypeEnum(str, Enum):
    HOSPITAL = "hospital"
    APAE = "apae"
    ONG = "ong"
    FUNDACAO = "fundacao"
    ASSOCIACAO = "associacao"
    INSTITUTO = "instituto"

class CredentialStatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REJECTED = "rejected"

class FieldOfActionEnum(str, Enum):
    MEDICO_ASSISTENCIAL = "medico_assistencial"
    FORMACAO = "formacao"
    PESQUISA = "pesquisa"

class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BudgetCategoryEnum(str, Enum):
    PESSOAL = "pessoal"
    MATERIAL_CONSUMO = "material_consumo"
    MATERIAL_PERMANENTE = "material_permanente"
    DESPESAS_ADMINISTRATIVAS = "despesas_administrativas"
    REFORMAS = "reformas"
    CAPTACAO_RECURSOS = "captacao_recursos"
    AUDITORIA = "auditoria"
    OUTROS = "outros"

class MonitoringFrequencyEnum(str, Enum):
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# Institution schemas
class InstitutionBase(BaseSchema):
    cnpj: str = Field(..., regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', description="CNPJ no formato XX.XXX.XXX/XXXX-XX")
    name: str = Field(..., min_length=3, max_length=255)
    legal_name: str = Field(..., min_length=3, max_length=255)
    institution_type: InstitutionTypeEnum
    cep: str = Field(..., regex=r'^\d{5}-\d{3}$', description="CEP no formato XXXXX-XXX")
    address: str = Field(..., min_length=10, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., regex=r'^[A-Z]{2}$', description="UF do estado (2 letras maiúsculas)")
    phone: Optional[str] = Field(None, regex=r'^\(\d{2}\) \d{4,5}-\d{4}$')
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    legal_representative: str = Field(..., min_length=3, max_length=255)
    technical_responsible: Optional[str] = Field(None, max_length=255)
    experience_proof: Optional[str] = Field(None, min_length=50, description="Comprovação de experiência mínima de 50 caracteres")

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=3, max_length=255)
    institution_type: Optional[InstitutionTypeEnum] = None
    cep: Optional[str] = Field(None, regex=r'^\d{5}-\d{3}$')
    address: Optional[str] = Field(None, min_length=10, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, regex=r'^[A-Z]{2}$')
    phone: Optional[str] = Field(None, regex=r'^\(\d{2}\) \d{4,5}-\d{4}$')
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    legal_representative: Optional[str] = Field(None, min_length=3, max_length=255)
    technical_responsible: Optional[str] = Field(None, max_length=255)
    experience_proof: Optional[str] = Field(None, min_length=50)

class Institution(InstitutionBase):
    id: int
    credential_status: CredentialStatusEnum
    credential_date: Optional[datetime] = None
    credential_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Project Team schemas
class ProjectTeamBase(BaseSchema):
    role: str = Field(..., min_length=3, max_length=100, description="Função na equipe")
    name: str = Field(..., min_length=3, max_length=255, description="Nome completo")
    cpf: Optional[str] = Field(None, regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', description="CPF no formato XXX.XXX.XXX-XX")
    qualification: str = Field(..., min_length=10, description="Qualificação profissional detalhada")
    weekly_hours: int = Field(..., ge=1, le=44, description="Carga horária semanal (1-44h)")
    monthly_salary: Optional[Decimal] = Field(None, ge=0, description="Salário mensal se aplicável")

class ProjectTeamCreate(ProjectTeamBase):
    pass

class ProjectTeam(ProjectTeamBase):
    id: int
    project_id: int
    created_at: datetime

# Project Budget schemas
class ProjectBudgetBase(BaseSchema):
    category: BudgetCategoryEnum
    subcategory: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=3, max_length=255, description="Descrição detalhada do item")
    unit: Optional[str] = Field(None, max_length=50, description="Unidade de medida")
    quantity: Decimal = Field(..., gt=0, description="Quantidade do item")
    unit_value: Decimal = Field(..., gt=0, description="Valor unitário")
    total_value: Decimal = Field(..., gt=0, description="Valor total (quantity * unit_value)")
    nature_expense_code: Optional[str] = Field(None, description="Código da natureza de despesa (Portaria 448/2002)")

    @validator('total_value', always=True)
    def validate_total_value(cls, v, values):
        """Valida se o valor total está correto"""
        if 'quantity' in values and 'unit_value' in values:
            expected_total = values['quantity'] * values['unit_value']
            if abs(v - expected_total) > 0.01:  # Margem de erro para decimais
                raise ValueError('Valor total deve ser quantidade × valor unitário')
        return v

class ProjectBudgetCreate(ProjectBudgetBase):
    pass

class ProjectBudget(ProjectBudgetBase):
    id: int
    project_id: int
    created_at: datetime

# Project Goal schemas
class ProjectGoalBase(BaseSchema):
    indicator_name: str = Field(..., min_length=3, max_length=255, description="Nome do indicador")
    target_value: Decimal = Field(..., ge=0, description="Meta a ser atingida")
    measurement_method: str = Field(..., min_length=10, description="Método de medição detalhado")
    frequency: MonitoringFrequencyEnum
    baseline_value: Optional[Decimal] = Field(None, ge=0, description="Valor base atual")

class ProjectGoalCreate(ProjectGoalBase):
    pass

class ProjectGoal(ProjectGoalBase):
    id: int
    project_id: int
    created_at: datetime

# Project Timeline schemas
class ProjectTimelineBase(BaseSchema):
    phase_name: str = Field(..., min_length=3, max_length=255, description="Nome da fase")
    start_month: int = Field(..., ge=1, description="Mês de início (1, 2, 3, ...)")
    end_month: int = Field(..., ge=1, description="Mês de término")
    deliverables: Optional[List[str]] = Field(None, description="Lista de entregáveis da fase")

    @validator('end_month')
    def validate_end_month(cls, v, values):
        """Valida se o mês de término é posterior ao de início"""
        if 'start_month' in values and v < values['start_month']:
            raise ValueError('Mês de término deve ser maior ou igual ao mês de início')
        return v

class ProjectTimelineCreate(ProjectTimelineBase):
    pass

class ProjectTimeline(ProjectTimelineBase):
    id: int
    project_id: int
    created_at: datetime

# Project schemas
class ProjectBase(BaseSchema):
    title: str = Field(..., min_length=10, max_length=255, description="Título do projeto")
    description: Optional[str] = Field(None, min_length=50, description="Descrição geral do projeto")
    field_of_action: FieldOfActionEnum
    priority_area_id: int = Field(..., description="ID da área prioritária (Art. 10)")
    general_objective: str = Field(..., min_length=50, description="Objetivo geral detalhado")
    specific_objectives: List[str] = Field(..., min_items=3, description="Mínimo 3 objetivos específicos")
    justification: str = Field(..., min_length=500, description="Justificativa com mínimo 500 caracteres")
    target_audience: Optional[str] = Field(None, min_length=20, description="Público-alvo detalhado")
    methodology: Optional[str] = Field(None, min_length=50, description="Metodologia do projeto")
    expected_results: Optional[str] = Field(None, min_length=50, description="Resultados esperados")
    budget_total: Decimal = Field(..., gt=0, description="Orçamento total do projeto")
    timeline_months: int = Field(..., ge=6, le=48, description="Prazo em meses (6-48 meses)")

    @validator('specific_objectives')
    def validate_specific_objectives(cls, v):
        """Valida os objetivos específicos"""
        if len(v) < 3:
            raise ValueError('Mínimo de 3 objetivos específicos é obrigatório')
        for obj in v:
            if len(obj.strip()) < 20:
                raise ValueError('Cada objetivo específico deve ter pelo menos 20 caracteres')
        return v

class ProjectCreate(ProjectBase):
    # Dados relacionados que podem ser criados junto
    team_members: Optional[List[ProjectTeamCreate]] = Field(None, min_items=1, description="Equipe do projeto")
    budget_items: Optional[List[ProjectBudgetCreate]] = Field(None, min_items=1, description="Itens do orçamento")
    goals: Optional[List[ProjectGoalCreate]] = Field(None, min_items=1, description="Metas e indicadores")
    timeline: Optional[List[ProjectTimelineCreate]] = Field(None, min_items=3, description="Cronograma do projeto")

    @validator('budget_items', always=True)
    def validate_budget_consistency(cls, v, values):
        """Valida consistência do orçamento"""
        if v and 'budget_total' in values:
            total_budget = sum(item.total_value for item in v)
            if abs(total_budget - values['budget_total']) > 0.01:
                raise ValueError('Soma dos itens do orçamento deve ser igual ao orçamento total')
            
            # Validar que auditoria independente está incluída
            has_audit = any(item.category == BudgetCategoryEnum.AUDITORIA for item in v)
            if not has_audit:
                raise ValueError('Auditoria independente é obrigatória (art. 92 do Anexo LXXXVI)')
                
            # Validar limite de captação de recursos (máximo 5% ou R$ 50.000)
            captacao_items = [item for item in v if item.category == BudgetCategoryEnum.CAPTACAO_RECURSOS]
            if captacao_items:
                total_captacao = sum(item.total_value for item in captacao_items)
                max_captacao = min(values['budget_total'] * 0.05, 50000)
                if total_captacao > max_captacao:
                    raise ValueError(f'Captação de recursos limitada a 5% do total ou R$ 50.000 (máximo: R$ {max_captacao:.2f})')
        
        return v

    @validator('timeline', always=True)
    def validate_timeline_consistency(cls, v, values):
        """Valida consistência do cronograma"""
        if v and 'timeline_months' in values:
            max_month = max(phase.end_month for phase in v)
            if max_month > values['timeline_months']:
                raise ValueError(f'Cronograma excede o prazo do projeto ({values["timeline_months"]} meses)')
        return v

class ProjectUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, min_length=50)
    general_objective: Optional[str] = Field(None, min_length=50)
    specific_objectives: Optional[List[str]] = Field(None, min_items=3)
    justification: Optional[str] = Field(None, min_length=500)
    target_audience: Optional[str] = Field(None, min_length=20)
    methodology: Optional[str] = Field(None, min_length=50)
    expected_results: Optional[str] = Field(None, min_length=50)
    budget_total: Optional[Decimal] = Field(None, gt=0)
    timeline_months: Optional[int] = Field(None, ge=6, le=48)

class Project(ProjectBase):
    id: int
    institution_id: int
    status: ProjectStatusEnum
    submission_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    execution_start_date: Optional[datetime] = None
    execution_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relacionamentos (quando necessário)
    institution: Optional[Institution] = None
    team_members: Optional[List[ProjectTeam]] = None
    budget_items: Optional[List[ProjectBudget]] = None
    goals: Optional[List[ProjectGoal]] = None
    timeline: Optional[List[ProjectTimeline]] = None

# Priority Area schemas
class PriorityAreaBase(BaseSchema):
    code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    active: bool = True

class PriorityAreaCreate(PriorityAreaBase):
    pass

class PriorityArea(PriorityAreaBase):
    id: int

# AI Generated Project Response
class AIProjectResponse(BaseSchema):
    project: ProjectCreate
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confiança na geração (0-1)")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Score de conformidade com as diretrizes")
    recommendations: List[str] = Field(..., description="Recomendações para melhoria")
    validation_results: Dict[str, Any] = Field(..., description="Resultados da validação automática")
    similar_projects: Optional[List[Dict[str, Any]]] = Field(None, description="Projetos similares para referência")

# System Configuration
class SystemConfigBase(BaseSchema):
    key: str = Field(..., min_length=1, max_length=100)
    value: Optional[str] = None
    description: Optional[str] = Field(None, max_length=255)

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfig(SystemConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Response schemas for API
class StandardResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Validation schemas for specific business rules
class ProjectSubmissionValidation(BaseSchema):
    """Validação específica para submissão de projetos"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    compliance_score: float
    required_documents: List[str]
    missing_documents: List[str]

class BudgetValidation(BaseSchema):
    """Validação específica de orçamento"""
    is_valid: bool
    total_valid: bool
    category_distribution: Dict[str, Decimal]
    compliance_issues: List[str]
    nature_code_issues: List[str]