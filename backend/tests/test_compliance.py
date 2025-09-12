"""
Testes de Conformidade PRONAS/PCD
Valida todas as regras de negócio conforme legislação
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from models.institution import Institution, CredentialStatus
from models.project import Project, ProjectStatus
from services.project_service import ProjectService
from services.validation_service import ValidationService

class TestPronasCompliance:
    """Testes de conformidade com regras PRONAS/PCD"""
    
    def test_max_projects_per_institution(self, db: Session, sample_institution):
        """
        Testa limite de 3 projetos por instituição
        Art. 25 da Portaria de Consolidação nº 5/2017
        """
        service = ProjectService(db)
        
        # Criar 3 projetos (máximo permitido)
        for i in range(3):
            project_data = self.get_valid_project_data()
            project_data["institution_id"] = sample_institution.id
            project_data["title"] = f"Projeto {i+1}"
            
            project = service.create_project(project_data, user_id=1)
            assert project is not None
        
        # Tentar criar 4º projeto (deve falhar)
        project_data = self.get_valid_project_data()
        project_data["institution_id"] = sample_institution.id
        project_data["title"] = "Projeto 4"
        
        with pytest.raises(Exception) as exc_info:
            service.create_project(project_data, user_id=1)
        
        assert "máximo" in str(exc_info.value).lower()
        assert "3 projetos" in str(exc_info.value).lower()
    
    def test_credentialing_period_restriction(self, db: Session):
        """
        Testa restrição de credenciamento apenas em junho/julho
        Art. 14 da Portaria de Consolidação nº 5/2017
        """
        from services.institution_service import InstitutionService
        service = InstitutionService(db)
        
        institution = Institution(
            cnpj="12.345.678/0001-90",
            name="Instituição Teste",
            credential_status=CredentialStatus.PENDING
        )
        db.add(institution)
        db.commit()
        
        # Simular mês fora do período (janeiro)
        with pytest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15)
            mock_datetime.utcnow = datetime.utcnow
            
            with pytest.raises(Exception) as exc_info:
                service.request_credential(institution.id)
            
            assert "junho" in str(exc_info.value).lower()
            assert "julho" in str(exc_info.value).lower()
        
        # Simular mês dentro do período (junho)
        with pytest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 6, 15)
            mock_datetime.utcnow = datetime.utcnow
            
            result = service.request_credential(institution.id)
            assert result is True
    
    def test_project_timeline_validation(self, db: Session):
        """
        Testa validação de prazo do projeto (6-48 meses)
        Art. 21 da Portaria de Consolidação nº 5/2017
        """
        validation_service = ValidationService(db)
        
        # Prazo muito curto (< 6 meses)
        project_data = self.get_valid_project_data()
        project_data["timeline_months"] = 3
        
        result = validation_service.validate_project_rules(project_data)
        assert result["is_valid"] is False
        assert any("6 meses" in error for error in result["errors"])
        
        # Prazo muito longo (> 48 meses)
        project_data["timeline_months"] = 60
        
        result = validation_service.validate_project_rules(project_data)
        assert result["is_valid"] is False
        assert any("48 meses" in error for error in result["errors"])
        
        # Prazo válido
        project_data["timeline_months"] = 24
        
        result = validation_service.validate_project_rules(project_data)
        assert result["is_valid"] is True
    
    def test_mandatory_audit_in_budget(self, db: Session):
        """
        Testa obrigatoriedade de auditoria independente no orçamento
        Art. 92 da Portaria de Consolidação nº 5/2017
        """
        validation_service = ValidationService(db)
        
        project_data = self.get_valid_project_data()
        
        # Orçamento sem auditoria
        project_data["budget_items"] = [
            {
                "category": "pessoal",
                "description": "Equipe técnica",
                "total_value": 100000
            },
            {
                "category": "material_consumo",
                "description": "Materiais",
                "total_value": 50000
            }
        ]
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["is_valid"] is False
        assert any("auditoria" in error.lower() for error in result["errors"])
        
        # Adicionar auditoria
        project_data["budget_items"].append({
            "category": "auditoria",
            "description": "Auditoria independente",
            "total_value": 5000
        })
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["has_mandatory_audit"] is True
    
    def test_fundraising_limits(self, db: Session):
        """
        Testa limites de captação de recursos (5% ou R$ 50.000)
        Art. 30 da Portaria de Consolidação nº 5/2017
        """
        validation_service = ValidationService(db)
        
        # Teste com orçamento de R$ 500.000
        project_data = self.get_valid_project_data()
        project_data["budget_total"] = 500000
        
        # Captação dentro do limite (5% = R$ 25.000)
        project_data["budget_items"] = [
            {
                "category": "captacao_recursos",
                "description": "Captação de recursos",
                "total_value": 25000
            }
        ]
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["fundraising_within_limits"] is True
        
        # Captação acima do limite percentual
        project_data["budget_items"][0]["total_value"] = 30000
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["fundraising_within_limits"] is False
        assert any("5%" in error or "50.000" in error for error in result["errors"])
        
        # Teste com orçamento de R$ 2.000.000
        project_data["budget_total"] = 2000000
        
        # Captação no limite absoluto (R$ 50.000)
        project_data["budget_items"][0]["total_value"] = 50000
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["fundraising_within_limits"] is True
        
        # Captação acima do limite absoluto
        project_data["budget_items"][0]["total_value"] = 60000
        
        result = validation_service.validate_budget_compliance(project_data)
        assert result["fundraising_within_limits"] is False
    
    def test_justification_minimum_length(self, db: Session):
        """
        Testa comprimento mínimo da justificativa (500 caracteres)
        """
        validation_service = ValidationService(db)
        
        project_data = self.get_valid_project_data()
        
        # Justificativa muito curta
        project_data["justification"] = "Justificativa curta"
        
        result = validation_service.validate_project_rules(project_data)
        assert result["is_valid"] is False
        assert any("500 caracteres" in error for error in result["errors"])
        
        # Justificativa adequada
        project_data["justification"] = "a" * 500
        
        result = validation_service.validate_project_rules(project_data)
        # Deve passar esta validação específica
        assert not any("500 caracteres" in error for error in result.get("errors", []))
    
    def test_specific_objectives_minimum(self, db: Session):
        """
        Testa mínimo de 3 objetivos específicos
        """
        validation_service = ValidationService(db)
        
        project_data = self.get_valid_project_data()
        
        # Menos de 3 objetivos
        project_data["specific_objectives"] = ["Objetivo 1", "Objetivo 2"]
        
        result = validation_service.validate_project_rules(project_data)
        assert result["is_valid"] is False
        assert any("3 objetivos" in error for error in result["errors"])
        
        # Exatamente 3 objetivos
        project_data["specific_objectives"] = [
            "Objetivo específico 1",
            "Objetivo específico 2",
            "Objetivo específico 3"
        ]
        
        result = validation_service.validate_project_rules(project_data)
        # Deve passar esta validação específica
        assert not any("3 objetivos" in error for error in result.get("errors", []))
    
    def test_nature_expense_code_validation(self, db: Session):
        """
        Testa validação de códigos de natureza de despesa
        Portaria nº 448/2002
        """
        from integrations.comprasnet import ComprasNetIntegration
        integration = ComprasNetIntegration()
        
        # Códigos válidos
        valid_codes = [
            "3.3.90.30",  # Material de Consumo
            "3.3.90.36",  # Pessoa Física
            "3.3.90.39",  # Pessoa Jurídica
            "4.4.90.52"   # Equipamentos
        ]
        
        for code in valid_codes:
            is_valid = await integration.validar_natureza_despesa(code)
            assert is_valid is True
        
        # Códigos inválidos
        invalid_codes = [
            "1.2.34.56",
            "9.9.99.99",
            "ABC123"
        ]
        
        for code in invalid_codes:
            is_valid = await integration.validar_natureza_despesa(code)
            assert is_valid is False
    
    def test_priority_areas_validation(self, db: Session):
        """
        Testa validação das 8 áreas prioritárias
        Art. 10 da Portaria de Consolidação nº 5/2017
        """
        from models.priority_area import PriorityArea
        
        # Verificar se todas as 8 áreas estão cadastradas
        areas = db.query(PriorityArea).filter(PriorityArea.active == True).all()
        
        expected_codes = ["QSS", "RPD", "DDP", "EPD", "ITR", "APE", "TAA", "APC"]
        actual_codes = [area.code for area in areas]
        
        for code in expected_codes:
            assert code in actual_codes, f"Área {code} não encontrada"
        
        assert len(areas) == 8, "Devem existir exatamente 8 áreas prioritárias"
    
    @staticmethod
    def get_valid_project_data():
        """Retorna dados válidos de projeto para testes"""
        return {
            "institution_id": 1,
            "priority_area_id": 1,
            "title": "Projeto de Teste PRONAS/PCD",
            "description": "Descrição detalhada do projeto de teste",
            "field_of_action": "medico_assistencial",
            "general_objective": "Objetivo geral do projeto de teste com detalhamento",
            "specific_objectives": [
                "Objetivo específico 1 detalhado",
                "Objetivo específico 2 detalhado",
                "Objetivo específico 3 detalhado"
            ],
            "justification": "a" * 500,  # 500 caracteres
            "target_audience": "Pessoas com deficiência da região",
            "methodology": "Metodologia detalhada do projeto",
            "expected_results": "Resultados esperados detalhados",
            "budget_total": 500000.00,
            "timeline_months": 24,
            "estimated_beneficiaries": 200,
            "budget_items": [
                {
                    "category": "pessoal",
                    "description": "Equipe técnica",
                    "total_value": 300000
                },
                {
                    "category": "material_consumo",
                    "description": "Materiais",
                    "total_value": 100000
                },
                {
                    "category": "auditoria",
                    "description": "Auditoria independente",
                    "total_value": 15000
                },
                {
                    "category": "captacao_recursos",
                    "description": "Captação",
                    "total_value": 20000
                }
            ],
            "team_members": [
                {
                    "role": "Coordenador",
                    "name": "João Silva",
                    "qualification": "Médico especialista",
                    "weekly_hours": 20
                },
                {
                    "role": "Fisioterapeuta",
                    "name": "Maria Santos",
                    "qualification": "Fisioterapeuta especializada",
                    "weekly_hours": 30
                }
            ],
            "goals": [
                {
                    "indicator_name": "Atendimentos realizados",
                    "target_value": 1000,
                    "measurement_method": "Registro em prontuário",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Satisfação dos usuários",
                    "target_value": 85,
                    "measurement_method": "Pesquisa de satisfação",
                    "frequency": "trimestral"
                }
            ],
            "timeline": [
                {
                    "phase_name": "Planejamento",
                    "start_month": 1,
                    "end_month": 3,
                    "deliverables": ["Plano de trabalho", "Contratações"]
                },
                {
                    "phase_name": "Execução",
                    "start_month": 4,
                    "end_month": 21,
                    "deliverables": ["Atendimentos", "Relatórios mensais"]
                },
                {
                    "phase_name": "Finalização",
                    "start_month": 22,
                    "end_month": 24,
                    "deliverables": ["Relatório final", "Prestação de contas"]
                }
            ]
        }