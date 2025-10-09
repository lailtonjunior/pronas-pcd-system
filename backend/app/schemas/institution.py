"""
Institution Pydantic Schemas
"""

from typing import Optional
from pydantic import Field, EmailStr
from app.schemas.base import BaseSchema, BaseResponse
from app.domain.entities.institution import InstitutionType, InstitutionStatus

class InstitutionBase(BaseSchema):
    name: str = Field(..., min_length=3, max_length=255)
    cnpj: str = Field(..., min_length=14, max_length=14, description="CNPJ contendo apenas números")
    type: InstitutionType
    address: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str
    phone: Optional[str] = None
    email: EmailStr
    legal_representative_name: str
    legal_representative_cpf: str = Field(..., min_length=11, max_length=11, description="CPF contendo apenas números")

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionUpdate(BaseSchema):
    name: Optional[str] = None
    type: Optional[InstitutionType] = None
    status: Optional[InstitutionStatus] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    legal_representative_name: Optional[str] = None
    legal_representative_cpf: Optional[str] = None

class InstitutionResponse(BaseResponse, InstitutionBase):
    status: InstitutionStatus
    pronas_registration_number: Optional[str] = None