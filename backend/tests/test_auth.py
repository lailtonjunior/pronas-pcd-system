"""
Authentication Tests
Testes para endpoints de autenticação
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Criar usuário de teste"""
    user_repo = UserRepositoryImpl(db_session)
    auth_service = AuthService(user_repo, None)
    
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": UserRole.OPERADOR,
        "status": UserStatus.ACTIVE,
        "is_active": True,
        "institution_id": None,
        "hashed_password": auth_service.hash_password("password123"),
        "consent_given": True,
    }
    
    return await user_repo.create(user_data)


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Teste de login bem-sucedido"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Teste de login com credenciais inválidas"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Email ou senha incorretos" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Teste de login com usuário inexistente"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Teste para obter usuário atual"""
    # Primeiro fazer login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Obter usuário atual
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Teste com token inválido"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
