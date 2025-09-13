"""
User Repository Interface
"""

from abc import abstractmethod
from typing import Optional, List
from app.domain.repositories.base import BaseRepository
from app.domain.entities.user import User, UserRole, UserStatus


class UserRepository(BaseRepository[User, int]):
    """Interface do repositório de usuários"""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        pass
    
    @abstractmethod
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuários por papel/role"""
        pass
    
    @abstractmethod
    async def get_by_institution(self, institution_id: int) -> List[User]:
        """Buscar usuários de uma instituição"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int) -> None:
        """Atualizar último login do usuário"""
        pass
    
    @abstractmethod
    async def change_password(self, user_id: int, new_hashed_password: str) -> bool:
        """Alterar senha do usuário"""
        pass
    
    @abstractmethod
    async def update_status(self, user_id: int, status: UserStatus) -> bool:
        """Atualizar status do usuário"""
        pass
    
    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """Buscar apenas usuários ativos"""
        pass