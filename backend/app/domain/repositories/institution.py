"""
Institution Repository Interface
"""

from abc import abstractmethod
from typing import Optional, List
from app.domain.repositories.base import BaseRepository
from app.domain.entities.institution import Institution, InstitutionType, InstitutionStatus


class InstitutionRepository(BaseRepository[Institution, int]):
    """Interface do repositório de instituições"""
    
    @abstractmethod
    async def get_by_cnpj(self, cnpj: str) -> Optional[Institution]:
        """Buscar instituição por CNPJ"""
        pass
    
    @abstractmethod
    async def get_by_type(self, institution_type: InstitutionType) -> List[Institution]:
        """Buscar instituições por tipo"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: InstitutionStatus) -> List[Institution]:
        """Buscar instituições por status"""
        pass
    
    @abstractmethod
    async def get_by_pronas_number(self, pronas_number: str) -> Optional[Institution]:
        """Buscar por número de registro PRONAS"""
        pass
    
    @abstractmethod
    async def search_by_name(self, name_query: str) -> List[Institution]:
        """Buscar instituições por nome (busca parcial)"""
        pass
    
    @abstractmethod
    async def get_by_city_state(self, city: str, state: str) -> List[Institution]:
        """Buscar instituições por cidade e estado"""
        pass
    
    @abstractmethod
    async def update_status(self, institution_id: int, status: InstitutionStatus) -> bool:
        """Atualizar status da instituição"""
        pass
