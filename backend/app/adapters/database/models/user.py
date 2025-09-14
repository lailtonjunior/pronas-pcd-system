"""
User SQLAlchemy Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.user import UserRole, UserStatus


class UserModel(BaseModel):
    """Modelo SQLAlchemy para usuários"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Enum fields
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.OPERADOR)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Institution relationship
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    institution = relationship("InstitutionModel", back_populates="users")
    
    # LGPD fields
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime(timezone=True))
    data_retention_date = Column(DateTime(timezone=True))
    
    # Relationships
    created_projects = relationship("ProjectModel", back_populates="creator")
    uploaded_documents = relationship("DocumentModel", back_populates="uploader")
    audit_logs = relationship("AuditLogModel", back_populates="user")
