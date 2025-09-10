"""
Testes principais da aplicação PRONAS/PCD
Cobertura completa de funcionalidades críticas
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch, AsyncMock

# Import app and dependencies
from main import app
from core.database import get_db, Base
from core.config import Settings
from models.user import User, UserRole
from models.institution import Institution, InstitutionType, CredentialStatus
from models.project import Project, ProjectStatus
from core.security import create_access_token, get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pronas_pcd.db"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependencies
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Create test client"""
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    """Create database session for testing"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    user = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=get_password_hash("test_password123"),
        role=UserRole.ADMIN,
        is_active=True,
        full_name="Test Administrator"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    """Create admin authentication token"""
    return create_access_token(data={"sub": admin_user.username})

@pytest.fixture
def sample_institution(db_session):
    """Create sample institution for testing"""
    institution = Institution(
        cnpj="12.345.678/0001-90",
        name="APAE Teste",
        legal_name="Associação de Pais e Amigos dos Excepcionais de Teste",
        institution_type=InstitutionType.APAE,
        cep="01234-567",
        address="Rua Teste, 123",
        city="São Paulo", 
        state="SP",
        email="contato@apae-teste.org.br",
        phone="(11) 99999-9999",
        legal_representative="João Silva",
        credential_status=CredentialStatus.ACTIVE
    )
    db_session.add(institution)
    db_session.commit()
    db_session.refresh(institution)
    return institution

@pytest.fixture
def sample_project(db_session, sample_institution):
    """Create sample project for testing"""
    project = Project(
        title="Projeto de Reabilitação Teste",
        description="Projeto de teste para reabilitação",
        institution_id=sample_institution.id,
        priority_area_id=1,
        general_objective="Promover reabilitação de pessoas com deficiência",
        specific_objectives=["Atender 100 pessoas", "Capacitar 10 profissionais"],
        justification="Projeto necessário para atender demanda da região conforme diretrizes PRONAS/PCD",
        budget_total=500000.00,
        timeline_months=24,
        status=ProjectStatus.DRAFT
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

class TestSystemEndpoints:
    """Test system core endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns system information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["system"] == "PRONAS/PCD Management Platform"
        assert data["version"] == "2.0.0"
        assert data["features"]["ai_areas"] == 8
        assert data["features"]["legal_compliance"] == "100%"
        assert "endpoints" in data
        assert "legal_framework" in data
        assert len(data["legal_framework"]) >= 4
    
    def test_health_endpoint_healthy(self, client):
        """Test health endpoint when all services are healthy"""
        with patch('core.database.SessionLocal') as mock_db, \
             patch('core.cache.get_redis') as mock_redis:
            
            # Mock database health
            mock_db_instance = Mock()
            mock_db_instance.execute.return_value.scalar.return_value = 5
            mock_db.return_value = mock_db_instance
            
            # Mock Redis health
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "services" in data
            assert "system_info" in data
            assert data["version"] == "2.0.0"
    
    def test_health_endpoint_degraded(self, client):
        """Test health endpoint when some services are degraded"""
        with patch('core.database.SessionLocal') as mock_db, \
             patch('core.cache.get_redis') as mock_redis:
            
            # Mock database healthy
            mock_db_instance = Mock()
            mock_db_instance.execute.return_value.scalar.return_value = 5
            mock_db.return_value = mock_db_instance
            
            # Mock Redis unhealthy
            mock_redis.side_effect = Exception("Redis connection failed")
            
            response = client.get("/health")
            assert response.status_code == 206  # Partial Content
            
            data = response.json()
            assert data["status"] == "degraded"
            assert data["services"]["database"]["status"] == "healthy"
            assert data["services"]["redis"]["status"] == "unhealthy"
    
    def test_version_endpoint(self, client):
        """Test version endpoint returns build information"""
        response = client.get("/version")
        assert response.status_code == 200
        
        data = response.json()
        assert data["version"] == "2.0.0"
        assert "build_date" in data
        assert "environment" in data
        assert "features" in data
        assert "legal_compliance" in data
        assert data["legal_compliance"]["compliance_score"] == "100%"
    
    def test_metrics_endpoint_authenticated(self, client, admin_token):
        """Test metrics endpoint requires authentication"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/metrics", headers=headers)
        assert response.status_code == 200

class TestSecurityFeatures:
    """Test security features and middleware"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/")
        
        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Make multiple requests rapidly
        responses = []
        for i in range(150):  # Exceed rate limit
            response = client.get("/")
            responses.append(response.status_code)
        
        # Should have some rate limited responses
        assert 429 in responses  # Too Many Requests

class TestBusinessRules:
    """Test PRONAS/PCD specific business rules"""
    
    def test_max_projects_per_institution(self, client, admin_token, sample_institution):
        """Test maximum projects per institution rule"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create 3 projects (maximum allowed)
        for i in range(3):
            project_data = {
                "title": f"Projeto Teste {i+1}",
                "description": "Projeto de teste",
                "institution_id": sample_institution.id,
                "priority_area_id": 1,
                "general_objective": "Objetivo geral",
                "specific_objectives": ["Objetivo específico 1"],
                "justification": "Justificativa do projeto conforme PRONAS/PCD" * 10,
                "budget_total": 500000.00,
                "timeline_months": 24
            }
            
            response = client.post("/api/v1/projects/", json=project_data, headers=headers)
            assert response.status_code == 201
        
        # Try to create 4th project (should fail)
        project_data = {
            "title": "Projeto Teste 4",
            "description": "Projeto que deve falhar",
            "institution_id": sample_institution.id,
            "priority_area_id": 1,
            "general_objective": "Objetivo geral",
            "specific_objectives": ["Objetivo específico 1"],
            "justification": "Justificativa do projeto conforme PRONAS/PCD" * 10,
            "budget_total": 500000.00,
            "timeline_months": 24
        }
        
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 400
        assert "máximo de 3 projetos" in response.json()["detail"]
    
    def test_project_timeline_validation(self, client, admin_token, sample_institution):
        """Test project timeline validation (6-48 months)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test timeline too short (< 6 months)
        project_data = {
            "title": "Projeto Timeline Curto",
            "description": "Projeto com timeline inválido",
            "institution_id": sample_institution.id,
            "priority_area_id": 1,
            "general_objective": "Objetivo geral",
            "specific_objectives": ["Objetivo específico 1"],
            "justification": "Justificativa do projeto conforme PRONAS/PCD" * 10,
            "budget_total": 500000.00,
            "timeline_months": 3  # Too short
        }
        
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 422
        
        # Test timeline too long (> 48 months)
        project_data["timeline_months"] = 60  # Too long
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 422
        
        # Test valid timeline
        project_data["timeline_months"] = 24  # Valid
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 201

class TestAIIntegration:
    """Test AI service integration"""
    
    @patch('services.ai_service.PronasAIService')
    def test_ai_project_generation(self, mock_ai_service, client, admin_token, sample_institution):
        """Test AI project generation functionality"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Mock AI service response
        mock_ai_instance = Mock()
        mock_ai_response = {
            "project": {
                "title": "Projeto Gerado por IA",
                "general_objective": "Objetivo gerado automaticamente",
                "specific_objectives": ["Objetivo 1", "Objetivo 2"],
                "justification": "Justificativa gerada pela IA" * 20,
                "budget_total": 750000.00,
                "timeline_months": 36
            },
            "confidence_score": 0.85,
            "compliance_score": 0.92,
            "recommendations": ["Recomendação 1", "Recomendação 2"]
        }
        mock_ai_instance.generate_project_from_guidelines.return_value = mock_ai_response
        mock_ai_service.return_value = mock_ai_instance
        
        generation_request = {
            "institution_id": sample_institution.id,
            "priority_area_code": "RPD",
            "budget_total": 750000.00,
            "timeline_months": 36,
            "target_beneficiaries": 300,
            "local_context": "Contexto local da região"
        }
        
        response = client.post("/api/v1/ai/generate-project", json=generation_request, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "project" in data
        assert "confidence_score" in data
        assert "compliance_score" in data
        assert data["confidence_score"] >= 0.75  # Minimum threshold

class TestComplianceValidation:
    """Test compliance validation with PRONAS/PCD rules"""
    
    def test_project_justification_minimum_length(self, client, admin_token, sample_institution):
        """Test project justification minimum length requirement"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test justification too short
        project_data = {
            "title": "Projeto Teste",
            "description": "Projeto de teste", 
            "institution_id": sample_institution.id,
            "priority_area_id": 1,
            "general_objective": "Objetivo geral",
            "specific_objectives": ["Objetivo específico 1"],
            "justification": "Justificativa muito curta",  # Too short
            "budget_total": 500000.00,
            "timeline_months": 24
        }
        
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 422
        
        # Test justification with adequate length
        project_data["justification"] = "Justificativa adequada conforme PRONAS/PCD " * 20
        response = client.post("/api/v1/projects/", json=project_data, headers=headers)
        assert response.status_code == 201
    
    def test_institution_credentialing_period(self, client, admin_token):
        """Test institution credentialing period validation (June/July only)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        institution_data = {
            "cnpj": "98.765.432/0001-10",
            "name": "Nova APAE Teste",
            "legal_name": "Nova Associação Teste",
            "institution_type": "apae",
            "cep": "12345-678",
            "address": "Rua Nova, 456",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "email": "nova@apae-teste.org.br",
            "legal_representative": "Maria Silva"
        }
        
        # Create institution
        response = client.post("/api/v1/institutions/", json=institution_data, headers=headers)
        assert response.status_code == 201
        
        institution_id = response.json()["data"]["institution_id"]
        
        # Mock current month to test credentialing period
        with patch('datetime.datetime') as mock_datetime:
            # Test outside credentialing period (e.g., January)
            mock_datetime.now.return_value.month = 1
            mock_datetime.utcnow = datetime.utcnow
            
            # Try to request credential outside period
            files = {"documents": ("test.pdf", b"fake pdf content", "application/pdf")}
            response = client.post(f"/api/v1/institutions/{institution_id}/credential", 
                                 files=files, headers=headers)
            assert response.status_code == 400
            assert "junho e julho" in response.json()["detail"]

class TestPerformanceMetrics:
    """Test performance and monitoring metrics"""
    
    def test_response_time_headers(self, client):
        """Test response time headers are added"""
        response = client.get("/")
        assert "x-response-time" in response.headers
    
    def test_prometheus_metrics_collection(self, client):
        """Test Prometheus metrics are collected"""
        # Make several requests to generate metrics
        for _ in range(10):
            client.get("/")
            client.get("/health")
        
        # Check metrics endpoint (would need authentication in production)
        response = client.get("/metrics")
        assert response.status_code == 200
        
        # Check for expected metrics
        metrics_content = response.content.decode()
        assert "pronas_http_requests_total" in metrics_content
        assert "pronas_http_request_duration_seconds" in metrics_content

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
