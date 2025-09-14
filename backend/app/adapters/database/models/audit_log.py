"""
Audit Log SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.audit_log import AuditAction, AuditResource


class AuditLogModel(BaseModel):
    """Modelo SQLAlchemy para logs de auditoria - IMUTÁVEL"""
    __tablename__ = "audit_logs"
    
    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource = Column(SQLEnum(AuditResource), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # User details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(50), nullable=False)
    
    # Request context
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    user_agent = Column(Text, nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Operation details
    description = Column(Text, nullable=False)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Result
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # LGPD
    data_sensitivity = Column(String(20), default="internal", nullable=False, index=True)
    
    # Immutable timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="audit_logs")
    
    # Override created_at/updated_at behavior for immutability
    def __init__(self, **kwargs):
        # Remove created_at and updated_at from kwargs to prevent override
        kwargs.pop('created_at', None)
        kwargs.pop('updated_at', None)
        super().__init__(**kwargs)
