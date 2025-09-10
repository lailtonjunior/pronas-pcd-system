"""
Test Configuration - Professional Testing Setup
"""

import asyncio
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import tempfile
import os

# Import app and dependencies
from main import app
from core.database import get_db, Base
from core.config import Settings
from models.user import User, UserRole
from core.security import security

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_pronas_pcd.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Test settings
test_settings = Settings()
test_settings.DEBUG = True
test_settings.DATABASE_URL = TEST_DATABASE_URL

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create test database session"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=test_engine)

def override_get_db(db: Session = None):
    """Override database dependency for testing"""
    def _override():
        try:
            yield db
        finally:
            pass
    return _override

@pytest.fixture
def client(db: Session) -> TestClient:
    """Create test client with database override"""
    app.dependency_overrides[get_db] = override_get_db(db)
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db: Session) -> User:
    """Create admin user for testing"""
    admin = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=security.get_password_hash("test_password"),
        role=UserRole.ADMIN,
        is_active=True,
        full_name="Test Admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def manager_user(db: Session) -> User:
    """Create manager user for testing"""
    manager = User(
        username="test_manager",
        email="manager@test.com", 
        hashed_password=security.get_password_hash("test_password"),
        role=UserRole.MANAGER,
        is_active=True,
        full_name="Test Manager"
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager

@pytest.fixture
def regular_user(db: Session) -> User:
    """Create regular user for testing"""
    user = User(
        username="test_user",
        email="user@test.com",
        hashed_password=security.get_password_hash("test_password"),
        role=UserRole.USER,
        is_active=True,
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Get admin authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": admin_user.username,
            "password": "test_password"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def manager_token(client: TestClient, manager_user: User) -> str:
    """Get manager authentication token"""
    response = client.post(
        "/api/v1/auth/login", 
        data={
            "username": manager_user.username,
            "password": "test_password"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def user_token(client: TestClient, regular_user: User) -> str:
    """Get user authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": regular_user.username,
            "password": "test_password"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Get authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def sample_institution_data() -> dict:
    """Sample institution data for testing"""
    return {
        "cnpj": "12.345.678/0001-90",
        "name": "APAE Teste",
        "legal_name": "Associação de Pais e Amigos dos Excepcionais de Teste",
        "institution_type": "apae",
        "cep": "01234-567",
        "address": "Rua Teste, 123",
        "city": "São Paulo",
        "state": "SP",
        "email": "contato@apae-teste.org.br",
        "phone": "(11) 99999-9999",
        "legal_representative": "João Silva",
        "legal_representative_cpf": "123.456.789-00"
    }

@pytest.fixture
def sample_project_data() -> dict:
    """Sample project data for testing"""
    return {
        "title": "Projeto de Reabilitação Teste",
        "description": "Projeto de teste para reabilitação de pessoas com deficiência",
        "institution_id": 1,
        "priority_area_code": "RPD",
        "general_objective": "Promover a reabilitação de pessoas com deficiência na região",
        "specific_objectives": [
            "Realizar 100 atendimentos de fisioterapia",
            "Capacitar 10 profissionais da área",
            "Adquirir 5 equipamentos especializados"
        ],
        "justification": """
        Este projeto é fundamental para atender a demanda reprimida de reabilitação na região, 
        considerando que existe uma carência significativa de serviços especializados para pessoas 
        com deficiência. A iniciativa visa preencher esta lacuna oferecendo atendimento de qualidade 
        e capacitação profissional adequada, seguindo todas as diretrizes do PRONAS/PCD estabelecidas 
        pela Portaria de Consolidação nº 5/2017. O projeto contribuirá diretamente para a melhoria 
        da qualidade de vida das pessoas com deficiência e suas famílias.
        """,
        "budget_total": 500000.00,
        "timeline_months": 24,
        "target_audience": "Pessoas com deficiência física e intelectual",
        "expected_results": "Melhoria na qualidade de vida dos beneficiários"
    }

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def create_test_file(content: str = "test content", filename: str = "test.txt") -> str:
        """Create temporary test file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{filename}")
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def cleanup_test_file(filepath: str):
        """Clean up test file"""
        try:
            os.unlink(filepath)
        except FileNotFoundError:
            pass

@pytest.fixture
def test_utils():
    """Test utilities fixture"""
    return TestUtils
