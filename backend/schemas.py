# backend/schemas.py - Schemas Pydantic para validação baseados nas regras PRONAS/PCD
"""
Schemas de validação baseados na Portaria de Consolidação nº 5/2017
Implementa todas as validações necessárias para conformidade PRONAS/PCD
"""

from pydantic import BaseModel, validator, Field, EmailStr
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

# ==================== ENUMS PYDANTIC ====================

class CredentialStatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REJECTED = "rejected"

class InstitutionTypeEnum(str, Enum):
    HOSPITAL = "hospital"
    APAE = "apae"
    ONG = "ong"
    FUNDACAO = "fundacao"
    ASSOCIACAO = "associacao"
    INSTITUTO = "instituto"
    COOPERATIVA = "cooperativa"
    OSCIP = "oscip"

class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class FieldOfActionEnum(str, Enum):
    MEDICO_ASSISTENCIAL = "medico_assistencial"
    FORMACAO = "formacao"
    PESQUISA = "pesquisa"

class BudgetCategoryEnum(str, Enum):
    PESSOAL = "pessoal"
    MATERIAL_CONSUMO = "material_consumo"
    MATERIAL_PERMANENTE = "material_permanente"
    DESPESAS_ADMINISTRATIVAS = "despesas_administrativas"
    REFORMAS = "reformas"
    CAPTACAO_RECURSOS = "captacao_recursos"
    AUDITORIA = "auditoria"

class MonitoringFrequencyEnum(str, Enum):
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

# ==================== INSTITUTION SCHEMAS ====================

class InstitutionBase(BaseModel):
    """Schema base para instituições"""
    cnpj: str = Field(..., min_length=18, max_length=18, description="CNPJ no formato XX.XXX.XXX/XXXX-XX")
    name: str = Field(..., min_length=3, max_length=255, description="Nome fantasia")
    legal_name: str = Field(..., min_length=3, max_length=255, description="Razão social")
    institution_type: InstitutionTypeEnum
    cep: str = Field(..., min_length=9, max_length=9, description="CEP no formato XXXXX-XXX")
    address: str = Field(..., min_length=10, max_length=500, description="Endereço completo")
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=2, description="UF com 2 letras")
    phone: Optional[str] = Field(None, max_length=20)
    email: EmailStr
    website: Optional[str] = Field(None, max_length=255)
    legal_representative: str = Field(..., min_length=3, max_length=255)
    legal_representative_cpf: Optional[str] = Field(None, min_length=14, max_length=14)
    technical_responsible: Optional[str] = Field(None, max_length=255)
    technical_responsible_registration: Optional[str] = Field(None, max_length=50)
    experience_proof: Optional[str] = Field(None, min_length=50, description="Mínimo 50 caracteres")
    services_offered: Optional[str] = None
    technical_capacity: Optional[str] = None
    partnership_history: Optional[str] = None

    @validator('cnpj')
    def validate_cnpj(cls, v):
        """Validar formato do CNPJ"""
        import re
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$', v):
            raise ValueError('CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX')
        return v

    @validator('cep')
    def validate_cep(cls, v):
        """Validar formato do CEP"""
        import re
        if not re.match(r'^\d{5}-\d{3}$', v):
            raise ValueError('CEP deve estar no formato XXXXX-XXX')
        return v

    @validator('state')
    def validate_state(cls, v):
        """Validar UF"""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if v.upper() not in valid_states:
            raise ValueError('UF deve ser um estado válido')
        return v.upper()

    @validator('phone')
    def validate_phone(cls, v):
        """Validar formato do telefone"""
        if v:
            import re
            if not re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', v):
                raise ValueError('Telefone deve estar no formato (XX) XXXXX-XXXX')
        return v

    @validator('legal_representative_cpf')
    def validate_cpf(cls, v):
        """Validar formato do CPF"""
        if v:
            import re
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
                raise ValueError('CPF deve estar no formato XXX.XXX.XXX-XX')
        return v

class InstitutionCreate(InstitutionBase):
    """Schema para criação de instituição"""
    pass

class InstitutionUpdate(BaseModel):
    """Schema para atualização de instituição"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=3, max_length=255)
    institution_type: Optional[InstitutionTypeEnum] = None
    cep: Optional[str] = Field(None, min_length=9, max_length=9)
    address: Optional[str] = Field(None, min_length=10, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    legal_representative: Optional[str] = Field(None, min_length=3, max_length=255)
    legal_representative_cpf: Optional[str] = Field(None, min_length=14, max_length=14)
    technical_responsible: Optional[str] = Field(None, max_length=255)
    technical_responsible_registration: Optional[str] = Field(None, max_length=50)
    experience_proof: Optional[str] = Field(None, min_length=50)
    services_offered: Optional[str] = None
    technical_capacity: Optional[str] = None
    partnership_history: Optional[str] = None
    credential_status: Optional[CredentialStatusEnum] = None

class Institution(InstitutionBase):
    """Schema completo da instituição"""
    id: int
    credential_status: CredentialStatusEnum
    credential_date: Optional[datetime]
    credential_expiry: Optional[datetime]
    credential_number: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]

    class Config:
        orm_mode = True

# ==================== PROJECT TEAM SCHEMAS ====================

class ProjectTeamBase(BaseModel):
    """Schema base para membro da equipe"""
    role: str = Field(..., min_length=3, max_length=255, description="Função na equipe")
    name: str = Field(..., min_length=3, max_length=255)
    cpf: Optional[str] = Field(None, min_length=14, max_length=14)
    qualification: str = Field(..., min_length=10, description="Qualificação profissional")
    registration_number: Optional[str] = Field(None, max_length=50, description="CRM, CRF, etc.")
    weekly_hours: Decimal = Field(..., gt=0, le=44, description="Carga horária semanal")
    monthly_salary: Optional[Decimal] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @validator('cpf')
    def validate_cpf(cls, v):
        if v:
            import re
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', v):
                raise ValueError('CPF deve estar no formato XXX.XXX.XXX-XX')
        return v

class ProjectTeamCreate(ProjectTeamBase):
    pass

class ProjectTeam(ProjectTeamBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== PROJECT BUDGET SCHEMAS ====================

class ProjectBudgetBase(BaseModel):
    """Schema base para item orçamentário"""
    category: BudgetCategoryEnum
    subcategory: Optional[str] = Field(None, max_length=255)
    description: str = Field(..., min_length=10, description="Descrição detalhada do item")
    unit: Optional[str] = Field(None, max_length=50, description="Unidade (mês, peça, etc.)")
    quantity: Decimal = Field(..., gt=0, description="Quantidade")
    unit_value: Decimal = Field(..., gt=0, description="Valor unitário")
    total_value: Decimal = Field(..., gt=0, description="Valor total")
    nature_expense_code: Optional[str] = Field(None, max_length=10, description="Código Portaria 448/2002")
    justification: Optional[str] = None

    @validator('total_value', always=True)
    def validate_total_value(cls, v, values):
        """Validar se total = quantidade * valor unitário"""
        if 'quantity' in values and 'unit_value' in values:
            expected_total = values['quantity'] * values['unit_value']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Valor total deve ser igual a quantidade × valor unitário')
        return v

class ProjectBudgetCreate(ProjectBudgetBase):
    pass

class ProjectBudget(ProjectBudgetBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== PROJECT GOAL SCHEMAS ====================

class ProjectGoalBase(BaseModel):
    """Schema base para meta do projeto"""
    indicator_name: str = Field(..., min_length=5, max_length=255, description="Nome do indicador")
    target_value: Decimal = Field(..., gt=0, description="Meta a ser alcançada")
    measurement_method: str = Field(..., min_length=20, description="Método de mensuração")
    frequency: MonitoringFrequencyEnum
    baseline_value: Optional[Decimal] = Field(None, ge=0, description="Valor inicial")

class ProjectGoalCreate(ProjectGoalBase):
    pass

class ProjectGoal(ProjectGoalBase):
    id: int
    project_id: int
    current_value: Optional[Decimal]
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== PROJECT TIMELINE SCHEMAS ====================

class ProjectTimelineBase(BaseModel):
    """Schema base para fase do cronograma"""
    phase_name: str = Field(..., min_length=5, max_length=255, description="Nome da fase")
    start_month: int = Field(..., ge=1, le=48, description="Mês de início (1-48)")
    end_month: int = Field(..., ge=1, le=48, description="Mês de fim (1-48)")
    deliverables: Optional[List[str]] = Field(None, description="Lista de entregas")

    @validator('end_month')
    def validate_end_month(cls, v, values):
        """Validar se mês de fim é posterior ao de início"""
        if 'start_month' in values and v <= values['start_month']:
            raise ValueError('Mês de fim deve ser posterior ao mês de início')
        return v

class ProjectTimelineCreate(ProjectTimelineBase):
    pass

class ProjectTimeline(ProjectTimelineBase):
    id: int
    project_id: int
    status: str
    completion_percentage: Optional[Decimal]
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== PROJECT MAIN SCHEMAS ====================

class ProjectBase(BaseModel):
    """Schema base para projeto PRONAS/PCD"""
    institution_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=10, max_length=500, description="Título do projeto")
    description: Optional[str] = None
    field_of_action: FieldOfActionEnum
    priority_area_id: int = Field(..., ge=1, le=8, description="Área prioritária (1-8)")
    general_objective: str = Field(..., min_length=50, description="Objetivo geral (mín. 50 caracteres)")
    specific_objectives: List[str] = Field(..., min_items=3, description="Mínimo 3 objetivos específicos")
    justification: str = Field(..., min_length=500, description="Justificativa (mín. 500 caracteres)")
    target_audience: Optional[str] = None
    methodology: Optional[str] = None
    expected_results: Optional[str] = None
    sustainability_plan: Optional[str] = None
    budget_total: Decimal = Field(..., gt=0, description="Orçamento total")
    budget_captacao: Optional[Decimal] = Field(None, ge=0, description="Valor para captação")
    budget_captacao_percentage: Optional[Decimal] = Field(None, ge=60, le=120, description="60% a 120%")
    timeline_months: int = Field(..., ge=6, le=48, description="Prazo em meses (6-48)")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @validator('specific_objectives')
    def validate_specific_objectives(cls, v):
        """Validar objetivos específicos"""
        if len(v) < 3:
            raise ValueError('Deve haver pelo menos 3 objetivos específicos')
        for obj in v:
            if len(obj.strip()) < 20:
                raise ValueError('Cada objetivo específico deve ter pelo menos 20 caracteres')
        return v

    @validator('budget_captacao')
    def validate_budget_captacao(cls, v, values):
        """Validar valor de captação"""
        if v and 'budget_total' in values:
            # Máximo de 5% do orçamento total ou R$ 50.000 (o menor)
            max_percentage = values['budget_total'] * Decimal('0.05')
            max_absolute = Decimal('50000')
            max_allowed = min(max_percentage, max_absolute)
            
            if v > max_allowed:
                raise ValueError(f'Captação não pode exceder 5% do orçamento total ou R$ 50.000')
        return v

    @validator('budget_captacao_percentage')
    def validate_captacao_percentage(cls, v, values):
        """Validar percentual de captação"""
        if v:
            if v < 60 or v > 120:
                raise ValueError('Percentual de captação deve estar entre 60% e 120%')
        return v

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validar data de fim"""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('Data de fim deve ser posterior à data de início')
        return v

class ProjectCreate(ProjectBase):
    """Schema para criação de projeto"""
    team_members: Optional[List[ProjectTeamCreate]] = []
    budget_items: Optional[List[ProjectBudgetCreate]] = []
    goals: Optional[List[ProjectGoalCreate]] = []
    timeline: Optional[List[ProjectTimelineCreate]] = []

    @validator('budget_items')
    def validate_budget_items(cls, v, values):
        """Validar itens orçamentários"""
        if v and 'budget_total' in values:
            total_budget = sum(item.total_value for item in v)
            if abs(total_budget - values['budget_total']) > Decimal('0.01'):
                raise ValueError('Soma dos itens orçamentários deve ser igual ao orçamento total')
            
            # Verificar se há auditoria (obrigatória)
            has_audit = any(item.category == BudgetCategoryEnum.AUDITORIA for item in v)
            if not has_audit:
                raise ValueError('Orçamento deve incluir item de auditoria independente')
        
        return v

    @validator('timeline')
    def validate_timeline(cls, v, values):
        """Validar cronograma"""
        if v and 'timeline_months' in values:
            max_month = max(phase.end_month for phase in v) if v else 0
            if max_month > values['timeline_months']:
                raise ValueError('Cronograma não pode exceder o prazo do projeto')
        return v

class ProjectUpdate(BaseModel):
    """Schema para atualização de projeto"""
    title: Optional[str] = Field(None, min_length=10, max_length=500)
    description: Optional[str] = None
    field_of_action: Optional[FieldOfActionEnum] = None
    priority_area_id: Optional[int] = Field(None, ge=1, le=8)
    general_objective: Optional[str] = Field(None, min_length=50)
    specific_objectives: Optional[List[str]] = Field(None, min_items=3)
    justification: Optional[str] = Field(None, min_length=500)
    target_audience: Optional[str] = None
    methodology: Optional[str] = None
    expected_results: Optional[str] = None
    sustainability_plan: Optional[str] = None
    budget_total: Optional[Decimal] = Field(None, gt=0)
    budget_captacao: Optional[Decimal] = Field(None, ge=0)
    budget_captacao_percentage: Optional[Decimal] = Field(None, ge=60, le=120)
    timeline_months: Optional[int] = Field(None, ge=6, le=48)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ProjectStatusEnum] = None

class Project(ProjectBase):
    """Schema completo do projeto"""
    id: int
    status: ProjectStatusEnum
    submission_date: Optional[datetime]
    approval_date: Optional[datetime]
    execution_start_date: Optional[datetime]
    execution_end_date: Optional[datetime]
    evaluation_score: Optional[Decimal]
    compliance_score: Optional[Decimal]
    reviewer_comments: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    # Relacionamentos
    institution: Optional[Institution]
    team_members: Optional[List[ProjectTeam]]
    budget_items: Optional[List[ProjectBudget]]
    goals: Optional[List[ProjectGoal]]
    timeline: Optional[List[ProjectTimeline]]

    class Config:
        orm_mode = True

# ==================== PRIORITY AREA SCHEMAS ====================

class PriorityAreaBase(BaseModel):
    """Schema base para área prioritária"""
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    typical_actions: Optional[List[str]] = None
    budget_guidelines: Optional[Dict[str, Any]] = None
    team_guidelines: Optional[Dict[str, Any]] = None
    active: bool = True

class PriorityAreaCreate(PriorityAreaBase):
    pass

class PriorityArea(PriorityAreaBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== AI SCHEMAS ====================

class AIProjectResponse(BaseModel):
    """Resposta da geração de projeto por IA"""
    project: Dict[str, Any]
    confidence_score: float = Field(..., ge=0, le=1, description="Confiança da IA (0-1)")
    compliance_score: float = Field(..., ge=0, le=1, description="Score de conformidade (0-1)")
    recommendations: List[str] = Field(default_factory=list)
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    similar_projects: Optional[List[Dict[str, Any]]] = None
    generation_time: Optional[float] = None

class ProjectValidation(BaseModel):
    """Resultado da validação de projeto"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    compliance_score: float = Field(..., ge=0, le=1)
    required_documents: List[str] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    validation_details: Optional[Dict[str, Any]] = None

class ProjectSubmissionValidation(ProjectValidation):
    """Validação específica para submissão"""
    submission_period_valid: bool = True
    institution_limit_ok: bool = True
    budget_compliance_ok: bool = True
    team_adequacy_ok: bool = True

# ==================== MONITORING SCHEMAS ====================

class ProjectMonitoringBase(BaseModel):
    """Schema base para monitoramento"""
    goal_id: Optional[int] = None
    monitoring_date: datetime
    achieved_value: Decimal = Field(..., ge=0)
    observations: Optional[str] = None
    challenges: Optional[str] = None
    corrective_actions: Optional[str] = None

class ProjectMonitoringCreate(ProjectMonitoringBase):
    pass

class ProjectMonitoring(ProjectMonitoringBase):
    id: int
    project_id: int
    created_by: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

# ==================== DOCUMENT SCHEMAS ====================

class DocumentBase(BaseModel):
    """Schema base para documentos"""
    document_type: str = Field(..., min_length=3, max_length=100)
    document_name: str = Field(..., min_length=3, max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)

class InstitutionDocumentCreate(DocumentBase):
    pass

class InstitutionDocument(DocumentBase):
    id: int
    institution_id: int
    upload_date: datetime
    uploaded_by: Optional[str]
    verified: bool

    class Config:
        orm_mode = True

class ProjectDocumentCreate(DocumentBase):
    pass

class ProjectDocument(DocumentBase):
    id: int
    project_id: int
    upload_date: datetime
    uploaded_by: Optional[str]

    class Config:
        orm_mode = True

# ==================== SYSTEM SCHEMAS ====================

class SystemConfigBase(BaseModel):
    """Schema base para configuração do sistema"""
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., max_length=500)
    description: Optional[str] = Field(None, max_length=255)
    data_type: str = Field(default="string", max_length=20)
    category: str = Field(default="general", max_length=50)
    editable: bool = True

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfig(SystemConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class HealthCheck(BaseModel):
    """Schema para health check"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    system_info: Dict[str, Any]

class DashboardData(BaseModel):
    """Schema para dados do dashboard"""
    institutions: Dict[str, int]
    projects: Dict[str, int]
    budget: Dict[str, float]
    by_priority_area: Dict[str, int]
    generated_at: datetime

# ==================== RESPONSE SCHEMAS ====================

class StandardResponse(BaseModel):
    """Schema padrão para respostas da API"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Schema para respostas paginadas"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class ErrorResponse(BaseModel):
    """Schema para respostas de erro"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    error_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)