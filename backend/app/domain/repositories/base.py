"""
Base Repository Interface
Repositório base com operações CRUD genéricas
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

EntityType = TypeVar("EntityType")
IDType = TypeVar("IDType")


class BaseRepository(ABC, Generic[EntityType, IDType]):
    """Interface base para repositórios"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> EntityType:
        """Criar nova entidade"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: IDType) -> Optional[EntityType]:
        """Buscar entidade por ID"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[EntityType]:
        """Buscar todas as entidades com paginação e filtros"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: IDType, update_data: Dict[str, Any]) -> Optional[EntityType]:
        """Atualizar entidade"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: IDType) -> bool:
        """Excluir entidade"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar entidades com filtros opcionais"""
        pass