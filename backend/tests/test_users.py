"""
Users Tests
Testes para endpoints de usuários
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """Criar usuário admin de teste"""
    user_repo = UserRepositoryImpl(db_session)
    auth_service = AuthService(user_repo, None)
    
    user_data = {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE,
        "is_active": True,
        "institution_id": None,
        "hashed_password": auth_service.hash_password("admin123"),
        "consent_given": True,
    }
    
    return await user_repo.create(user_data)


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user):
    """Obter token do admin"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_user_as_admin(client: AsyncClient, admin_token):
    """Teste de criação de usuário pelo admin"""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "operador",
            "password": "Password123!",
            "consent_given": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "operador"


@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, admin_token):
    """Teste de listagem de usuários pelo admin"""
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_create_user_invalid_password(client: AsyncClient, admin_token):
    """Teste de criação com senha inválida"""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "invalid@example.com",
            "full_name": "Invalid User",
            "role": "operador",
            "password": "weak",  # Senha muito fraca
            "consent_given": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 422  # Validation error
