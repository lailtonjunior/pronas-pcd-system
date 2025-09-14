"""
Document SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.document import DocumentType, DocumentStatus


class DocumentModel(BaseModel):
    """Modelo SQLAlchemy para documentos"""
    __tablename__ = "documents"
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Classification
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("ProjectModel", back_populates="documents")
    
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    institution = relationship("InstitutionModel", back_populates="documents")
    
    # Metadata
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    
    # File integrity
    file_hash = Column(String(64), nullable=False, index=True)
    
    # Audit
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text, nullable=True)
    
    # LGPD - Personal data
    contains_personal_data = Column(Boolean, default=False, nullable=False)
    data_classification = Column(String(20), default="internal", nullable=False)
    retention_period_months = Column(Integer, nullable=True)
    
    # Relationships
    uploader = relationship("UserModel", back_populates="uploaded_documents", foreign_keys=[uploaded_by])
    reviewer = relationship("UserModel", foreign_keys=[reviewed_by])
