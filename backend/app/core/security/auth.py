"""
Authentication and JWT Security
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any]) -> str:
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


def create_refresh_token(data: Dict[str, Any]) -> str:
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


def verify_jwt_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
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


def hash_password(password: str) -> str:
    """Hash da senha"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return pwd_context.verify(plain_password, hashed_password)
