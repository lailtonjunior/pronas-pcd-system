"""
Project Entity - Projetos PRONAS/PCD
"""

from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class ProjectStatus(str, Enum):
    """Status do projeto"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, Enum):
    """Tipos de projeto PRONAS/PCD"""
    ASSISTENCIAL = "assistencial"
    PESQUISA = "pesquisa"
    DESENVOLVIMENTO_TECNOLOGICO = "desenvolvimento_tecnologico"
    CAPACITACAO = "capacitacao"
    INFRAESTRUTURA = "infraestrutura"


@dataclass
class Project:
    """Entidade de projeto do domínio"""
    id: Optional[int]
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
    other_funding: Optional[Decimal]
    
    # Técnico
    target_population: str
    expected_beneficiaries: int
    objectives: str
    methodology: str
    
    # Documentação
    technical_proposal_url: Optional[str]
    budget_detailed_url: Optional[str]
    
    # Responsável técnico
    technical_manager_name: str
    technical_manager_cpf: str
    technical_manager_email: str
    
    # Workflow
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    reviewer_id: Optional[int]
    review_notes: Optional[str]
    
    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    
    def calculate_funding_percentage(self) -> dict:
        """Calcular percentual de financiamentos"""
        total = float(self.total_budget)
        if total == 0:
            return {"pronas": 0, "own": 0, "other": 0}
        
        return {
            "pronas": (float(self.pronas_funding) / total) * 100,
            "own": (float(self.own_funding) / total) * 100,
            "other": (float(self.other_funding or 0) / total) * 100,
        }
    
    def is_editable(self) -> bool:
        """Verificar se projeto pode ser editado"""
        return self.status in [ProjectStatus.DRAFT, ProjectStatus.REJECTED]
    
    def can_be_submitted(self) -> bool:
        """Verificar se pode ser submetido"""
        return (
            self.status == ProjectStatus.DRAFT
            and self.technical_proposal_url is not None
            and self.budget_detailed_url is not None
        )
