"""
Project Repository Interface
"""

from abc import abstractmethod
from typing import Optional, List
from datetime import date
from decimal import Decimal
from app.domain.repositories.base import BaseRepository
from app.domain.entities.project import Project, ProjectStatus, ProjectType


class ProjectRepository(BaseRepository[Project, int]):
    """Interface do repositório de projetos"""
    
    @abstractmethod
    async def get_by_institution(self, institution_id: int) -> List[Project]:
        """Buscar projetos de uma instituição"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """Buscar projetos por status"""
        pass
    
    @abstractmethod
    async def get_by_type(self, project_type: ProjectType) -> List[Project]:
        """Buscar projetos por tipo"""
        pass
    
    @abstractmethod
    async def get_by_reviewer(self, reviewer_id: int) -> List[Project]:
        """Buscar projetos por revisor"""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Project]:
        """Buscar projetos por período"""
        pass
    
    @abstractmethod
    async def get_pending_review(self) -> List[Project]:
        """Buscar projetos pendentes de revisão"""
        pass
    
    @abstractmethod
    async def get_approved_projects(self) -> List[Project]:
        """Buscar projetos aprovados"""
        pass
    
    @abstractmethod
    async def search_by_title(self, title_query: str) -> List[Project]:
        """Buscar projetos por título (busca parcial)"""
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        project_id: int, 
        status: ProjectStatus,
        reviewer_id: Optional[int] = None,
        review_notes: Optional[str] = None
    ) -> bool:
        """Atualizar status do projeto"""
        pass
    
    @abstractmethod
    async def get_budget_summary_by_institution(self, institution_id: int) -> Dict[str, Decimal]:
        """Obter resumo orçamentário por instituição"""
        pass
    
    @abstractmethod
    async def get_projects_expiring_soon(self, days: int = 30) -> List[Project]:
        """Buscar projetos que expiram em X dias"""
        pass