"""
Model de Instituição - Sistema PRONAS/PCD
Conformidade: Art. 14-20 da Portaria de Consolidação nº 5/2017
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from models.base import BaseModel

class InstitutionType(str, enum.Enum):
    """Tipos de instituição elegíveis ao PRONAS/PCD"""
    HOSPITAL = "hospital"
    APAE = "apae"
    ONG = "ong"
    FUNDACAO = "fundacao"
    ASSOCIACAO = "associacao"
    INSTITUTO = "instituto"
    UNIVERSIDADE = "universidade"
    CLINICA = "clinica"

class CredentialStatus(str, enum.Enum):
    """Status do credenciamento conforme Art. 14"""
    PENDING = "pending"        # Aguardando análise
    ACTIVE = "active"          # Credenciamento ativo
    INACTIVE = "inactive"      # Inativo temporariamente
    EXPIRED = "expired"        # Expirado (renovar anualmente)
    REJECTED = "rejected"      # Rejeitado pelo MS
    SUSPENDED = "suspended"    # Suspenso por irregularidade

class Institution(BaseModel):
    __tablename__ = "institutions"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)  # Nome fantasia
    legal_name = Column(String(255), nullable=False)  # Razão social
    institution_type = Column(Enum(InstitutionType), nullable=False)
    
    # Endereço completo
    cep = Column(String(9), nullable=False)
    address = Column(String(500), nullable=False)
    number = Column(String(20), nullable=True)
    complement = Column(String(255), nullable=True)
    neighborhood = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    
    # Contato
    phone = Column(String(20), nullable=True)
    phone_secondary = Column(String(20), nullable=True)
    email = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    
    # Responsáveis
    legal_representative = Column(String(255), nullable=False)
    legal_representative_cpf = Column(String(14), nullable=False)
    legal_representative_email = Column(String(255), nullable=True)
    legal_representative_phone = Column(String(20), nullable=True)
    
    technical_responsible = Column(String(255), nullable=True)
    technical_responsible_cpf = Column(String(14), nullable=True)
    technical_responsible_registry = Column(String(50), nullable=True)  # CRM, CRF, etc.
    technical_responsible_email = Column(String(255), nullable=True)
    
    # Dados bancários para repasse
    bank_code = Column(String(5), nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_agency = Column(String(10), nullable=True)
    bank_account = Column(String(20), nullable=True)
    bank_account_type = Column(String(20), nullable=True)  # conta_corrente, poupanca
    
    # Experiência e capacidade técnica
    experience_proof = Column(Text, nullable=True)
    years_of_experience = Column(Integer, default=0)
    staff_count = Column(Integer, default=0)
    specialized_staff_count = Column(Integer, default=0)
    
    # Áreas de atuação (pode atuar em múltiplas)
    area_qss = Column(Boolean, default=False)  # Qualificação de serviços
    area_rpd = Column(Boolean, default=False)  # Reabilitação
    area_ddp = Column(Boolean, default=False)  # Diagnóstico diferencial
    area_epd = Column(Boolean, default=False)  # Estimulação precoce
    area_itr = Column(Boolean, default=False)  # Inserção no trabalho
    area_ape = Column(Boolean, default=False)  # Práticas esportivas
    area_taa = Column(Boolean, default=False)  # Terapia com animais
    area_apc = Column(Boolean, default=False)  # Produção artística
    
    # Credenciamento
    credential_status = Column(Enum(CredentialStatus), default=CredentialStatus.PENDING)
    credential_request_date = Column(DateTime, nullable=True)
    credential_approval_date = Column(DateTime, nullable=True)
    credential_expiry_date = Column(DateTime, nullable=True)
    credential_rejection_reason = Column(Text, nullable=True)
    credential_protocol = Column(String(50), nullable=True)  # Número do protocolo no MS
    
    # Regularidade fiscal e trabalhista
    cndt_valid_until = Column(DateTime, nullable=True)  # Certidão Negativa Débitos Trabalhistas
    crf_valid_until = Column(DateTime, nullable=True)   # Certificado Regularidade FGTS
    cnda_valid_until = Column(DateTime, nullable=True)  # Certidão Negativa Débitos União
    cnd_estadual_valid_until = Column(DateTime, nullable=True)
    cnd_municipal_valid_until = Column(DateTime, nullable=True)
    
    # Limites e controles
    max_projects_allowed = Column(Integer, default=3)  # Art. 25 - máximo 3 projetos
    active_projects_count = Column(Integer, default=0)
    total_funding_received = Column(Numeric(15, 2), default=0)
    
    # Avaliação e qualidade
    quality_score = Column(Numeric(3, 2), default=0)  # 0-10
    compliance_score = Column(Numeric(3, 2), default=0)  # 0-10
    last_audit_date = Column(DateTime, nullable=True)
    
    # Flags de controle
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text, nullable=True)
    can_submit_projects = Column(Boolean, default=True)
    
    # Relacionamentos
    users = relationship("User", back_populates="institution")
    projects = relationship("Project", back_populates="institution", cascade="all, delete-orphan")
    documents = relationship("InstitutionDocument", back_populates="institution", cascade="all, delete-orphan")
    
    # Timestamps e auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Institution {self.name} ({self.cnpj})>"
    
    def is_credential_valid(self) -> bool:
        """Verifica se credenciamento está válido"""
        if self.credential_status != CredentialStatus.ACTIVE:
            return False
        if self.credential_expiry_date and self.credential_expiry_date < datetime.utcnow():
            return False
        return True
    
    def can_submit_new_project(self) -> bool:
        """Verifica se pode submeter novo projeto"""
        if not self.is_credential_valid():
            return False
        if self.active_projects_count >= self.max_projects_allowed:
            return False
        if self.is_blacklisted:
            return False
        return self.can_submit_projects

class InstitutionDocument(BaseModel):
    """Documentos da instituição para credenciamento"""
    __tablename__ = "institution_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=False)
    
    document_type = Column(String(50), nullable=False)  # estatuto, ata, cnpj, certidao, etc.
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA-256 para integridade
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), nullable=True)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(100), nullable=True)
    
    institution = relationship("Institution", back_populates="documents")