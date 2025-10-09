"""
Institution Pydantic Schemas
"""
from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema
from app.domain.entities.institution import InstitutionType, InstitutionStatus

class InstitutionBase(BaseSchema):
    """Schema base para instituição"""
    name: str = Field(..., min_length=3, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=14)
    type: InstitutionType
    status: InstitutionStatus = Field(default=InstitutionStatus.PENDING_APPROVAL)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=8, max_length=9)
    phone: str = Field(..., min_length=10, max_length=15)
    email: str
    website: Optional[str] = None
    legal_representative_name: str = Field(..., min_length=3, max_length=255)
    legal_representative_cpf: str = Field(..., min_length=11, max_length=11)
    legal_representative_email: str

class InstitutionCreate(InstitutionBase):
    """Schema para criação de instituição"""
    pass

class InstitutionUpdate(BaseSchema):
    """Schema para atualização de instituição"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    type: Optional[InstitutionType] = None
    status: Optional[InstitutionStatus] = None
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, min_length=8, max_length=9)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[str] = None
    website: Optional[str] = None
    legal_representative_name: Optional[str] = Field(None, min_length=3, max_length=255)
    legal_representative_cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    legal_representative_email: Optional[str] = None