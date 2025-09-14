"""
Project SQLAlchemy Model
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum, Numeric, Date
from sqlalchemy.orm import relationship
from app.adapters.database.models.base import BaseModel
from app.domain.entities.project import ProjectStatus, ProjectType


class ProjectModel(BaseModel):
    """Modelo SQLAlchemy para projetos"""
    __tablename__ = "projects"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Enum fields
    type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    
    # Relationships
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    institution = relationship("InstitutionModel", back_populates="projects")
    
    # Schedule
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Budget
    total_budget = Column(Numeric(15, 2), nullable=False)
    pronas_funding = Column(Numeric(15, 2), nullable=False)
    own_funding = Column(Numeric(15, 2), nullable=False)
    other_funding = Column(Numeric(15, 2), nullable=True)
    
    # Technical details
    target_population = Column(String(500), nullable=False)
    expected_beneficiaries = Column(Integer, nullable=False)
    objectives = Column(Text, nullable=False)
    methodology = Column(Text, nullable=False)
    
    # Documentation URLs
    technical_proposal_url = Column(String(500), nullable=True)
    budget_detailed_url = Column(String(500), nullable=True)
    
    # Technical manager
    technical_manager_name = Column(String(255), nullable=False)
    technical_manager_cpf = Column(String(11), nullable=False)
    technical_manager_email = Column(String(255), nullable=False)
    
    # Workflow
    submitted_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("UserModel", back_populates="created_projects", foreign_keys=[created_by])
    reviewer = relationship("UserModel", foreign_keys=[reviewer_id])
    documents = relationship("DocumentModel", back_populates="project")
