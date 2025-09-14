"""
Institution SQLAlchemy Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.institution import InstitutionType, InstitutionStatus


class InstitutionModel(BaseModel):
    """Modelo SQLAlchemy para instituições"""
    __tablename__ = "institutions"
    
    name = Column(String(255), nullable=False, index=True)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    
    # Enum fields
    type = Column(SQLEnum(InstitutionType), nullable=False)
    status = Column(SQLEnum(InstitutionStatus), nullable=False, default=InstitutionStatus.PENDING_APPROVAL)
    
    # Address
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    
    # Contact
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    
    # Legal representative
    legal_representative_name = Column(String(255), nullable=False)
    legal_representative_cpf = Column(String(11), nullable=False)
    legal_representative_email = Column(String(255), nullable=False)
    
    # PRONAS/PCD data
    pronas_registration_number = Column(String(50), nullable=True, unique=True)
    pronas_certification_date = Column(DateTime(timezone=True))
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # LGPD
    data_processing_consent = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True))
    
    # Relationships
    users = relationship("UserModel", back_populates="institution")
    projects = relationship("ProjectModel", back_populates="institution")
    documents = relationship("DocumentModel", back_populates="institution")
