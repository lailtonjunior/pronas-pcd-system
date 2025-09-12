"""
Service de Autenticação - Sistema PRONAS/PCD
Implementa autenticação JWT, 2FA e controle de sessão
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pyotp
import qrcode
import io
import base64

from models.user import User, UserRole, UserSession
from schemas.auth import UserCreate, UserLogin, PasswordReset, TwoFactorSetup
from core.security import security
from core.config import settings
from services.notification_service import NotificationService
from services.audit_service import AuditService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentica usuário com username/email e senha
        Implementa proteção contra brute force
        """
        # Buscar usuário por username ou email
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        # Verificar se conta está bloqueada
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Conta bloqueada até {user.locked_until.strftime('%d/%m/%Y %H:%M')}"
            )
        
        # Verificar senha
        if not security.verify_password(password, user.hashed_password):
            # Incrementar contador de tentativas falhas
            user.failed_login_count += 1
            
            # Bloquear após 5 tentativas
            if user.failed_login_count >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                self.audit_service.log_security_event(
                    user_id=user.id,
                    event="account_locked",
                    details=f"Conta bloqueada após {user.failed_login_count} tentativas falhas"
                )
            
            self.db.commit()
            return None
        
        # Login bem-sucedido - resetar contadores
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.login_count += 1
        self.db.commit()
        
        # Log de auditoria
        self.audit_service.log_action(
            user_id=user.id,
            action="login",
            resource="auth",
            details={"method": "password"}
        )
        
        return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Cria novo usuário com validações PRONAS/PCD
        """
        # Verificar se email já existe
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Verificar se username já existe
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já em uso"
            )
        
        # Verificar se CPF já existe (se fornecido)
        if user_data.cpf and self.get_user_by_cpf(user_data.cpf):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        # Validar força da senha
        password_validation = security.validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=password_validation["issues"]
            )
        
        # Criar usuário
        user = User(
            username=user_data.username,
            email=user_data.email,
            cpf=user_data.cpf,
            full_name=user_data.full_name,
            phone=user_data.phone,
            hashed_password=security.get_password_hash(user_data.password),
            role=user_data.role or UserRole.USUARIO,
            institution_id=user_data.institution_id,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Enviar email de verificação
        self.send_verification_email(user)
        
        # Log de auditoria
        self.audit_service.log_action(
            user_id=user.id,
            action="create",
            resource="user",
            details={"username": user.username, "email": user.email}
        )
        
        return user
    
    def create_session(self, user: User, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Cria sessão de usuário com tokens JWT
        """
        # Criar access token
        access_token = security.create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Criar refresh token
        refresh_token = security.create_refresh_token(user.id)
        
        # Salvar sessão no banco
        session = UserSession(
            user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        self.db.add(session)
        self.db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "institution_id": user.institution_id,
                "two_factor_enabled": user.two_factor_enabled
            }
        }
    
    def setup_two_factor(self, user: User) -> Dict[str, Any]:
        """
        Configura autenticação de dois fatores
        """
        # Gerar secret único
        secret = pyotp.random_base32()
        
        # Criar URI para QR Code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name='PRONAS/PCD System'
        )
        
        # Gerar QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_code_base64 = base64.b64encode(buf.getvalue()).decode()
        
        # Salvar secret temporariamente (usuário precisa confirmar)
        user.two_factor_secret = secret
        self.db.commit()
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code_base64}",
            "backup_codes": self.generate_backup_codes(user)
        }
    
    def verify_two_factor(self, user: User, code: str) -> bool:
        """
        Verifica código 2FA
        """
        if not user.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code, valid_window=1)
    
    def request_password_reset(self, email: str) -> bool:
        """
        Solicita reset de senha
        """
        user = self.get_user_by_email(email)
        if not user:
            # Não revelar se email existe
            return True
        
        # Gerar token de reset
        reset_token = security.generate_secure_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(
            minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
        )
        self.db.commit()
        
        # Enviar email
        self.notification_service.send_password_reset_email(user, reset_token)
        
        # Log de auditoria
        self.audit_service.log_security_event(
            user_id=user.id,
            event="password_reset_requested",
            details={"email": email}
        )
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reseta senha com token
        """
        user = self.db.query(User).filter(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )
        
        # Validar nova senha
        password_validation = security.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=password_validation["issues"]
            )
        
        # Atualizar senha
        user.hashed_password = security.get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        self.db.commit()
        
        # Notificar usuário
        self.notification_service.send_password_changed_notification(user)
        
        # Log de auditoria
        self.audit_service.log_security_event(
            user_id=user.id,
            event="password_reset_completed",
            details={"method": "token"}
        )
        
        return True
    
    def revoke_session(self, token: str) -> bool:
        """
        Revoga sessão (logout)
        """
        session = self.db.query(UserSession).filter(
            UserSession.token == token
        ).first()
        
        if session:
            session.revoked_at = datetime.utcnow()
            self.db.commit()
            
            # Log de auditoria
            self.audit_service.log_action(
                user_id=session.user_id,
                action="logout",
                resource="auth",
                details={"session_id": session.id}
            )
            
            return True
        
        return False
    
    def send_verification_email(self, user: User):
        """
        Envia email de verificação
        """
        verification_token = security.generate_secure_token()
        
        # Salvar token temporariamente (implementar tabela de tokens se necessário)
        # Por simplicidade, usando o campo password_reset_token temporariamente
        
        self.notification_service.send_email(
            to=user.email,
            subject="Verificação de Email - PRONAS/PCD",
            template="email_verification",
            context={
                "user_name": user.full_name,
                "verification_link": f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            }
        )
    
    def generate_backup_codes(self, user: User, count: int = 10) -> list:
        """
        Gera códigos de backup para 2FA
        """
        codes = []
        for _ in range(count):
            code = security.generate_secure_token(length=8)
            codes.append(code)
        
        # Salvar hash dos códigos no banco (implementar tabela se necessário)
        # Por ora, retornando apenas os códigos
        
        return codes
    
    # Métodos auxiliares
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_cpf(self, cpf: str) -> Optional[User]:
        return self.db.query(User).filter(User.cpf == cpf).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()