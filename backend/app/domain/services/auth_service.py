"""
Authentication Service
Serviço de autenticação e autorização
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import get_settings
from app.domain.entities.user import User, UserRole, UserStatus
from app.domain.repositories.user import UserRepository
from app.domain.repositories.audit_log import AuditLogRepository
from app.domain.entities.audit_log import AuditAction, AuditResource

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Serviço de autenticação"""
    
    def __init__(
        self, 
        user_repo: UserRepository,
        audit_repo: AuditLogRepository
    ):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
    
    def hash_password(self, password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Criar token JWT de acesso"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Criar token JWT de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(
            to_encode, 
            settings.jwt_refresh_secret_key, 
            algorithm=settings.jwt_algorithm
        )
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verificar e decodificar token JWT"""
        try:
            secret_key = (
                settings.jwt_secret_key 
                if token_type == "access" 
                else settings.jwt_refresh_secret_key
            )
            
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            # Verificar se é o tipo correto de token
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> Optional[User]:
        """Autenticar usuário"""
        user = await self.user_repo.get_by_email(email)
        
        # Log de tentativa de login
        await self.audit_repo.create_log(
            action=AuditAction.LOGIN,
            resource=AuditResource.SYSTEM,
            user_id=user.id if user else 0,
            user_email=email,
            user_role=user.role if user else "unknown",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Tentativa de login para {email}",
            success=False  # Será atualizado se sucesso
        )
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        
        if user.status != UserStatus.ACTIVE or not user.is_active:
            return None
        
        # Atualizar último login
        await self.user_repo.update_last_login(user.id)
        
        # Log de login bem-sucedido
        await self.audit_repo.create_log(
            action=AuditAction.LOGIN,
            resource=AuditResource.SYSTEM,
            user_id=user.id,
            user_email=user.email,
            user_role=user.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Login realizado com sucesso",
            success=True
        )
        
        return user
    
    async def create_user(
        self, 
        user_data: Dict[str, Any],
        created_by_user: User,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> User:
        """Criar novo usuário"""
        # Hash da senha
        if "password" in user_data:
            user_data["hashed_password"] = self.hash_password(user_data.pop("password"))
        
        # Definir valores padrão
        user_data.update({
            "created_at": datetime.utcnow(),
            "is_active": True,
            "status": UserStatus.PENDING if user_data.get("role") != UserRole.ADMIN else UserStatus.ACTIVE,
            "consent_given": user_data.get("consent_given", False),
            "consent_date": datetime.utcnow() if user_data.get("consent_given") else None,
        })
        
        # Criar usuário
        new_user = await self.user_repo.create(user_data)
        
        # Log de criação
        await self.audit_repo.create_log(
            action=AuditAction.CREATE,
            resource=AuditResource.USER,
            resource_id=new_user.id,
            user_id=created_by_user.id,
            user_email=created_by_user.email,
            user_role=created_by_user.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Usuário criado: {new_user.email}",
            new_values={"email": new_user.email, "role": new_user.role},
            success=True,
            data_sensitivity="confidential"
        )
        
        return new_user
    
    async def change_password(
        self, 
        user_id: int, 
        old_password: str, 
        new_password: str,
        requesting_user: User,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> bool:
        """Alterar senha do usuário"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # Verificar senha atual (exceto para admin)
        if requesting_user.id != user_id and requesting_user.role != UserRole.ADMIN:
            if not self.verify_password(old_password, user.hashed_password):
                return False
        
        # Gerar nova senha hash
        new_hashed_password = self.hash_password(new_password)
        
        # Atualizar no banco
        success = await self.user_repo.change_password(user_id, new_hashed_password)
        
        # Log da operação
        await self.audit_repo.create_log(
            action=AuditAction.UPDATE,
            resource=AuditResource.USER,
            resource_id=user_id,
            user_id=requesting_user.id,
            user_email=requesting_user.email,
            user_role=requesting_user.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Senha alterada para usuário {user.email}",
            success=success,
            data_sensitivity="restricted"
        )
        
        return success