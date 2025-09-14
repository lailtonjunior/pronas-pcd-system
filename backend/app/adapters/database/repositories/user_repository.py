"""
User Repository Implementation
Implementação do repositório de usuários com SQLAlchemy
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.domain.repositories.user import UserRepository
from app.domain.entities.user import User, UserRole, UserStatus
from app.adapters.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """Implementação do repositório de usuários"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Converter SQLAlchemy model para domain entity"""
        if not model:
            return None
        
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            role=model.role,
            status=model.status,
            is_active=model.is_active,
            institution_id=model.institution_id,
            hashed_password=model.hashed_password,
            last_login=model.last_login,
            created_at=model.created_at,
            updated_at=model.updated_at,
            consent_given=model.consent_given,
            consent_date=model.consent_date,
            data_retention_date=model.data_retention_date,
        )
    
    async def create(self, entity_data: Dict[str, Any]) -> User:
        """Criar novo usuário"""
        model = UserModel(**entity_data)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Buscar usuário por ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Buscar usuários por papel/role"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.role == role)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_institution(self, institution_id: int) -> List[User]:
        """Buscar usuários de uma instituição"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.institution_id == institution_id)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_active_users(self) -> List[User]:
        """Buscar apenas usuários ativos"""
        result = await self.session.execute(
            select(UserModel).where(
                and_(UserModel.is_active == True, UserModel.status == UserStatus.ACTIVE)
            )
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update_last_login(self, user_id: int) -> None:
        """Atualizar último login do usuário"""
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.session.commit()
    
    async def change_password(self, user_id: int, new_hashed_password: str) -> bool:
        """Alterar senha do usuário"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_status(self, user_id: int, status: UserStatus) -> bool:
        """Atualizar status do usuário"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(status=status)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Buscar todos os usuários com paginação"""
        query = select(UserModel).offset(skip).limit(limit)
        
        if filters:
            if "role" in filters:
                query = query.where(UserModel.role == filters["role"])
            if "status" in filters:
                query = query.where(UserModel.status == filters["status"])
            if "is_active" in filters:
                query = query.where(UserModel.is_active == filters["is_active"])
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Atualizar usuário"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
            .returning(UserModel)
        )
        await self.session.commit()
        
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def delete(self, user_id: int) -> bool:
        """Excluir usuário (soft delete - marcar como inativo)"""
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=False, status=UserStatus.INACTIVE)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar usuários com filtros opcionais"""
        from sqlalchemy import func
        
        query = select(func.count(UserModel.id))
        
        if filters:
            if "role" in filters:
                query = query.where(UserModel.role == filters["role"])
            if "status" in filters:
                query = query.where(UserModel.status == filters["status"])
            if "is_active" in filters:
                query = query.where(UserModel.is_active == filters["is_active"])
        
        result = await self.session.execute(query)
        return result.scalar()
