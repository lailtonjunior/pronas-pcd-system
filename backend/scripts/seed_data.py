"""
Seed Data Script
Popular banco com dados iniciais para desenvolvimento e testes
"""

import asyncio
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config.settings import get_settings
from app.adapters.database.session import get_async_session
from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.adapters.database.repositories.institution_repository import InstitutionRepositoryImpl
from app.adapters.database.repositories.project_repository import ProjectRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.domain.entities.user import UserRole, UserStatus
from app.domain.entities.institution import InstitutionType, InstitutionStatus
from app.domain.entities.project import ProjectType, ProjectStatus

settings = get_settings()


async def create_admin_user():
    """Criar usuário administrador padrão"""
    async with get_async_session() as session:
        user_repo = UserRepositoryImpl(session)
        
        # Verificar se já existe
        admin_email = "admin@pronas-pcd.gov.br"
        existing_admin = await user_repo.get_by_email(admin_email)
        
        if not existing_admin:
            print("📝 Criando usuário administrador...")
            
            auth_service = AuthService(user_repo, None)
            admin_data = {
                "email": admin_email,
                "full_name": "Administrador do Sistema",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "is_active": True,
                "institution_id": None,
                "hashed_password": auth_service.hash_password("admin123456"),
                "created_at": datetime.utcnow(),
                "consent_given": True,
                "consent_date": datetime.utcnow(),
            }
            
            admin_user = await user_repo.create(admin_data)
            print(f"✅ Administrador criado: {admin_user.email}")
        else:
            print("ℹ️  Usuário administrador já existe")


async def create_sample_institution():
    """Criar instituição de exemplo"""
    async with get_async_session() as session:
        institution_repo = InstitutionRepositoryImpl(session)
        
        # Verificar se já existe
        sample_cnpj = "12345678000195"
        existing = await institution_repo.get_by_cnpj(sample_cnpj)
        
        if not existing:
            print("📝 Criando instituição de exemplo...")
            
            institution_data = {
                "name": "Hospital Exemplo PRONAS/PCD",
                "cnpj": sample_cnpj,
                "type": InstitutionType.HOSPITAL,
                "status": InstitutionStatus.ACTIVE,
                "address": "Rua Exemplo, 123",
                "city": "Brasília",
                "state": "DF",
                "zip_code": "70000000",
                "phone": "61999999999",
                "email": "contato@hospital-exemplo.org.br",
                "website": "https://www.hospital-exemplo.org.br",
                "legal_representative_name": "Dr. João Exemplo",
                "legal_representative_cpf": "12345678901",
                "legal_representative_email": "joao@hospital-exemplo.org.br",
                "pronas_registration_number": "PRONAS2024001",
                "pronas_certification_date": datetime.utcnow(),
                "created_by": 1,  # Admin user
                "created_at": datetime.utcnow(),
                "data_processing_consent": True,
                "consent_date": datetime.utcnow(),
            }
            
            institution = await institution_repo.create(institution_data)
            print(f"✅ Instituição criada: {institution.name}")
            return institution.id
        else:
            print("ℹ️  Instituição de exemplo já existe")
            return existing.id


async def create_sample_users(institution_id: int):
    """Criar usuários de exemplo"""
    async with get_async_session() as session:
        user_repo = UserRepositoryImpl(session)
        auth_service = AuthService(user_repo, None)
        
        sample_users = [
            {
                "email": "gestor@hospital-exemplo.org.br",
                "full_name": "Maria Gestora",
                "role": UserRole.GESTOR,
                "institution_id": institution_id,
            },
            {
                "email": "auditor@pronas-pcd.gov.br",
                "full_name": "Carlos Auditor",
                "role": UserRole.AUDITOR,
                "institution_id": None,
            },
            {
                "email": "operador@hospital-exemplo.org.br",
                "full_name": "Ana Operadora",
                "role": UserRole.OPERADOR,
                "institution_id": institution_id,
            }
        ]
        
        for user_data in sample_users:
            existing = await user_repo.get_by_email(user_data["email"])
            if not existing:
                print(f"📝 Criando usuário: {user_data['full_name']}")
                
                full_user_data = {
                    **user_data,
                    "status": UserStatus.ACTIVE,
                    "is_active": True,
                    "hashed_password": auth_service.hash_password("password123"),
                    "created_at": datetime.utcnow(),
                    "consent_given": True,
                    "consent_date": datetime.utcnow(),
                }
                
                user = await user_repo.create(full_user_data)
                print(f"✅ Usuário criado: {user.email}")
            else:
                print(f"ℹ️  Usuário já existe: {user_data['email']}")


async def create_sample_project(institution_id: int, creator_user_id: int):
    """Criar projeto de exemplo"""
    async with get_async_session() as session:
        project_repo = ProjectRepositoryImpl(session)
        
        # Verificar se já existe projeto
        projects = await project_repo.get_by_institution(institution_id)
        if not projects:
            print("📝 Criando projeto de exemplo...")
            
            project_data = {
                "title": "Projeto de Reabilitação Neurológica Pediátrica",
                "description": "Projeto focado na reabilitação de crianças com deficiências neurológicas através de terapias inovadoras e equipamentos especializados.",
                "type": ProjectType.ASSISTENCIAL,
                "status": ProjectStatus.DRAFT,
                "institution_id": institution_id,
                "start_date": date(2024, 1, 1),
                "end_date": date(2025, 12, 31),
                "total_budget": Decimal("500000.00"),
                "pronas_funding": Decimal("350000.00"),
                "own_funding": Decimal("150000.00"),
                "other_funding": Decimal("0.00"),
                "target_population": "Crianças de 0 a 17 anos com deficiências neurológicas",
                "expected_beneficiaries": 200,
                "objectives": "Melhorar a qualidade de vida e autonomia de crianças com deficiências neurológicas através de tratamentos especializados.",
                "methodology": "Terapias multidisciplinares incluindo fisioterapia, terapia ocupacional, fonoaudiologia e psicologia.",
                "technical_manager_name": "Dra. Patricia Especialista",
                "technical_manager_cpf": "98765432100",
                "technical_manager_email": "patricia@hospital-exemplo.org.br",
                "created_by": creator_user_id,
                "created_at": datetime.utcnow(),
            }
            
            project = await project_repo.create(project_data)
            print(f"✅ Projeto criado: {project.title}")
        else:
            print("ℹ️  Projeto de exemplo já existe")


async def main():
    """Script principal de seed"""
    print("🌱 Iniciando seed do banco de dados...")
    print(f"🔗 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    
    try:
        # 1. Criar admin
        await create_admin_user()
        
        # 2. Criar instituição de exemplo
        institution_id = await create_sample_institution()
        
        # 3. Criar usuários de exemplo
        await create_sample_users(institution_id)
        
        # 4. Criar projeto de exemplo
        await create_sample_project(institution_id, 2)  # Gestor user ID
        
        print("")
        print("🎉 Seed completo!")
        print("=" * 50)
        print("Usuários criados:")
        print("• admin@pronas-pcd.gov.br (senha: admin123456)")
        print("• gestor@hospital-exemplo.org.br (senha: password123)")
        print("• auditor@pronas-pcd.gov.br (senha: password123)")
        print("• operador@hospital-exemplo.org.br (senha: password123)")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro durante seed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
