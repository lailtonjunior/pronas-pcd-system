"""
Project Pydantic Schemas
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import Field, validator
from app.schemas.base import BaseSchema, BaseResponse
from app.domain.entities.project import ProjectStatus, ProjectType


class ProjectBase(BaseSchema):
    """Schema base para projeto"""
    title: str = Field(..., min_length=10, max_length=255)
    description: str = Field(..., min_length=50)
    type: ProjectType
    institution_id: int
    
    # Cronograma
    start_date: date
    end_date: date
    
    # Financeiro
    total_budget: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    pronas_funding: Decimal = Field(..., ge=0, max_digits=15, decimal_places=2)
    own_funding: Decimal = Field(..., ge=0, max_digits=15, decimal_places=2)
    other_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Técnico
    target_population: str = Field(..., min_length=10, max_length=500)
    expected_beneficiaries: int = Field(..., gt=0)
    objectives: str = Field(..., min_length=50)
    methodology: str = Field(..., min_length=50)
    
    # Responsável técnico
    technical_manager_name: str = Field(..., min_length=5, max_length=255)
    technical_manager_cpf: str = Field(..., regex=r'^\d{11}$')
    technical_manager_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validar datas do projeto"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('Data de fim deve ser posterior à data de início')
        return v
    
    @validator('total_budget')
    def validate_budget_consistency(cls, v, values):
        """Validar consistência do orçamento"""
        pronas = values.get('pronas_funding', Decimal('0'))
        own = values.get('own_funding', Decimal('0'))
        other = values.get('other_funding', Decimal('0'))
        
        total_funding = pronas + own + other
        if abs(total_funding - v) > Decimal('0.01'):
            raise ValueError('Soma dos financiamentos deve ser igual ao orçamento total')
        
        # PRONAS não pode exceder 80%
        if pronas > v * Decimal('0.8'):
            raise ValueError('Financiamento PRONAS não pode exceder 80% do orçamento total')
        
        return v


class ProjectCreate(ProjectBase):
    """Schema para criação de projeto"""
    pass


class ProjectUpdate(BaseSchema):
    """Schema para atualização de projeto"""
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, min_length=50)
    type: Optional[ProjectType] = None
    
    # Cronograma
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Financeiro
    total_budget: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    pronas_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    own_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    other_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Técnico
    target_population: Optional[str] = Field(None, min_length=10, max_length=500)
    expected_beneficiaries: Optional[int] = Field(None, gt=0)
    objectives: Optional[str] = Field(None, min_length=50)
    methodology: Optional[str] = Field(None, min_length=50)


class ProjectResponse(BaseResponse):
    """Schema de response para projeto"""
    title: str
    description: str
    type: ProjectType
    status: ProjectStatus
    institution_id: int
    
    # Cronograma
    start_date: date
    end_date: date
    
    # Financeiro
    total_budget: Decimal
    pronas_funding: Decimal
    own_funding: Decimal
    other_funding: Optional[Decimal] = None
    
    # Técnico
    target_population: str
    expected_beneficiaries: int
    objectives: str
    methodology: str
    
    # Responsável técnico
    technical_manager_name: str
    technical_manager_cpf: str
    technical_manager_email: str
    
    # Workflow
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    review_notes: Optional[str] = None
    
    created_by: int


class ProjectReview(BaseSchema):
    """Schema para revisão de projeto"""
    decision: ProjectStatus = Field(..., regex="^(approved|rejected)$")
    review_notes: str = Field(..., min_length=10, max_length=1000)


class ProjectStatusUpdate(BaseSchema):
    """Schema para atualização de status"""
    status: ProjectStatus
    notes: Optional[str] = None
