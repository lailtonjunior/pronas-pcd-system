"""
Institution Entity - Instituições PRONAS/PCD
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class InstitutionType(str, Enum):
    """Tipos de instituição"""
    HOSPITAL = "hospital"
    CLINICA = "clinica"
    CENTRO_REABILITACAO = "centro_reabilitacao"
    APAE = "apae"
    OSC = "osc"  # Organização da Sociedade Civil
    OUTRO = "outro"


class InstitutionStatus(str, Enum):
    """Status da instituição"""
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


@dataclass
class Institution:
    """Entidade de instituição do domínio"""
    id: Optional[int]
    name: str
    cnpj: str
    type: InstitutionType
    status: InstitutionStatus
    
    # Endereço
    address: str
    city: str
    state: str
    zip_code: str
    
    # Contato
    phone: str
    email: str
    website: Optional[str]
    
    # Responsável legal
    legal_representative_name: str
    legal_representative_cpf: str
    legal_representative_email: str
    
    # Dados PRONAS/PCD
    pronas_registration_number: Optional[str]
    pronas_certification_date: Optional[datetime]
    
    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    
    # Conformidade LGPD
    data_processing_consent: bool
    consent_date: Optional[datetime]
