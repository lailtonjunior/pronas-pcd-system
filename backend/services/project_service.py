"""
Service de Projetos - Sistema PRONAS/PCD
Implementa toda lógica de negócio para gestão de projetos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from models.project import (
    Project, ProjectStatus, FieldOfAction,
    ProjectTeam, ProjectBudget, ProjectGoal,
    ProjectTimeline, ProjectDocument, ProjectMonitoring
)
from models.institution import Institution, CredentialStatus
from models.priority_area import PriorityArea
from schemas.project import ProjectCreate, ProjectUpdate, ProjectSubmit
from services.notification_service import NotificationService
from services.audit_service import AuditService
from services.validation_service import ValidationService
from integrations.comprasnet import ComprasNetIntegration

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)
        self.validation_service = ValidationService(db)
        self.comprasnet = ComprasNetIntegration()
    
    def create_project(self, project_data: ProjectCreate, user_id: int) -> Project:
        """
        Cria novo projeto com todas as validações PRONAS/PCD
        """
        # 1. Validar instituição
        institution = self.db.query(Institution).filter(
            Institution.id == project_data.institution_id
        ).first()
        
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instituição não encontrada"
            )
        
        # 2. Verificar credenciamento válido
        if not institution.is_credential_valid():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instituição sem credenciamento válido"
            )
        
        # 3. Verificar limite de projetos (máximo 3)
        active_projects = self.db.query(Project).filter(
            Project.institution_id == institution.id,
            Project.status.in_([
                ProjectStatus.SUBMITTED,
                ProjectStatus.UNDER_REVIEW,
                ProjectStatus.APPROVED,
                ProjectStatus.IN_EXECUTION
            ])
        ).count()
        
        if active_projects >= institution.max_projects_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Instituição já possui {active_projects} projetos ativos (máximo: {institution.max_projects_allowed})"
            )
        
        # 4. Validar área prioritária
        priority_area = self.db.query(PriorityArea).filter(
            PriorityArea.id == project_data.priority_area_id,
            PriorityArea.active == True
        ).first()
        
        if not priority_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Área prioritária inválida ou inativa"
            )
        
        # 5. Validar regras de negócio PRONAS/PCD
        validation_result = self.validation_service.validate_project_rules(project_data)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["errors"]
            )
        
        # 6. Criar projeto
        project = Project(
            institution_id=institution.id,
            priority_area_id=priority_area.id,
            title=project_data.title,
            description=project_data.description,
            field_of_action=project_data.field_of_action,
            general_objective=project_data.general_objective,
            specific_objectives=project_data.specific_objectives,
            justification=project_data.justification,
            target_audience=project_data.target_audience,
            methodology=project_data.methodology,
            expected_results=project_data.expected_results,
            sustainability_plan=project_data.sustainability_plan,
            budget_total=project_data.budget_total,
            timeline_months=project_data.timeline_months,
            estimated_beneficiaries=project_data.estimated_beneficiaries,
            execution_city=project_data.execution_city or institution.city,
            execution_state=project_data.execution_state or institution.state,
            status=ProjectStatus.DRAFT,
            created_by=str(user_id)
        )
        
        self.db.add(project)
        self.db.flush()  # Para obter o ID
        
        # 7. Adicionar equipe técnica
        if project_data.team_members:
            for member_data in project_data.team_members:
                team_member = ProjectTeam(
                    project_id=project.id,
                    **member_data.dict()
                )
                self.db.add(team_member)
        
        # 8. Adicionar orçamento detalhado
        if project_data.budget_items:
            total_budget = Decimal(0)
            
            for budget_data in project_data.budget_items:
                # Validar natureza de despesa
                if budget_data.nature_expense_code:
                    is_valid = await self.comprasnet.validar_natureza_despesa(
                        budget_data.nature_expense_code
                    )
                    if not is_valid:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Código de natureza de despesa inválido: {budget_data.nature_expense_code}"
                        )
                
                budget_item = ProjectBudget(
                    project_id=project.id,
                    **budget_data.dict()
                )
                self.db.add(budget_item)
                total_budget += budget_item.total_value
            
            # Validar consistência do orçamento
            if abs(total_budget - project.budget_total) > Decimal(0.01):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Soma dos itens do orçamento diferente do total declarado"
                )
        
        # 9. Adicionar metas e indicadores
        if project_data.goals:
            for goal_data in project_data.goals:
                goal = ProjectGoal(
                    project_id=project.id,
                    **goal_data.dict()
                )
                self.db.add(goal)
        
        # 10. Adicionar cronograma
        if project_data.timeline:
            for phase_data in project_data.timeline:
                phase = ProjectTimeline(
                    project_id=project.id,
                    **phase_data.dict()
                )
                self.db.add(phase)
        
        # 11. Incrementar contador da instituição
        institution.active_projects_count += 1
        
        # Commit final
        self.db.commit()
        self.db.refresh(project)
        
        # 12. Notificações
        self.notification_service.notify_project_created(project)
        
        # 13. Auditoria
        self.audit_service.log_action(
            user_id=user_id,
            action="create",
            resource="project",
            resource_id=project.id,
            details={
                "title": project.title,
                "institution_id": institution.id,
                "budget": str(project.budget_total)
            }
        )
        
        return project
    
    def submit_project(self, project_id: int, user_id: int) -> Project:
        """
        Submete projeto para análise do Ministério da Saúde
        """
        project = self.get_project_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # Verificar se pode ser submetido
        if project.status != ProjectStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Projeto não pode ser submetido no status {project.status.value}"
            )
        
        # Validar completude do projeto
        validation = self.validate_project_completeness(project)
        if not validation["is_complete"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation["missing_items"]
            )
        
        # Gerar protocolo
        protocol = self.generate_protocol_number(project)
        
        # Atualizar status
        project.protocol_number = protocol
        project.status = ProjectStatus.SUBMITTED
        project.submission_date = datetime.utcnow()
        
        self.db.commit()
        
        # Notificações
        self.notification_service.notify_project_submitted(project)
        
        # Auditoria
        self.audit_service.log_action(
            user_id=user_id,
            action="submit",
            resource="project",
            resource_id=project.id,
            details={"protocol": protocol}
        )
        
        return project
    
    def validate_project_completeness(self, project: Project) -> Dict[str, Any]:
        """
        Valida se projeto está completo para submissão
        """
        missing_items = []
        
        # Verificar campos obrigatórios
        if len(project.justification or "") < 500:
            missing_items.append("Justificativa deve ter pelo menos 500 caracteres")
        
        if len(project.specific_objectives or []) < 3:
            missing_items.append("Mínimo de 3 objetivos específicos")
        
        # Verificar equipe
        team_count = self.db.query(ProjectTeam).filter(
            ProjectTeam.project_id == project.id
        ).count()
        if team_count < 2:
            missing_items.append("Equipe deve ter pelo menos 2 profissionais")
        
        # Verificar orçamento
        budget_items = self.db.query(ProjectBudget).filter(
            ProjectBudget.project_id == project.id
        ).all()
        
        if not budget_items:
            missing_items.append("Orçamento detalhado é obrigatório")
        else:
            # Verificar auditoria obrigatória
            has_audit = any(item.category == "auditoria" for item in budget_items)
            if not has_audit:
                missing_items.append("Auditoria independente é obrigatória (Art. 92)")
        
        # Verificar metas
        goals_count = self.db.query(ProjectGoal).filter(
            ProjectGoal.project_id == project.id
        ).count()
        if goals_count < 2:
            missing_items.append("Mínimo de 2 metas/indicadores")
        
        # Verificar cronograma
        timeline_count = self.db.query(ProjectTimeline).filter(
            ProjectTimeline.project_id == project.id
        ).count()
        if timeline_count < 3:
            missing_items.append("Cronograma deve ter pelo menos 3 fases")
        
        return {
            "is_complete": len(missing_items) == 0,
            "missing_items": missing_items
        }
    
    def generate_protocol_number(self, project: Project) -> str:
        """
        Gera número de protocolo único
        """
        year = datetime.now().year
        count = self.db.query(Project).filter(
            Project.submission_date >= datetime(year, 1, 1)
        ).count() + 1
        
        return f"PRONAS/{year}/{count:06d}"
    
    def approve_project(self, project_id: int, user_id: int, comments: str = None) -> Project:
        """
        Aprova projeto (apenas gestor MS)
        """
        project = self.get_project_by_id(project_id)
        
        if project.status != ProjectStatus.UNDER_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projeto não está em análise"
            )
        
        project.status = ProjectStatus.APPROVED
        project.approval_date = datetime.utcnow()
        project.technical_opinion = comments
        project.technical_opinion_by = str(user_id)
        project.technical_opinion_date = datetime.utcnow()
        
        self.db.commit()
        
        # Notificações
        self.notification_service.notify_project_approved(project)
        
        # Auditoria
        self.audit_service.log_action(
            user_id=user_id,
            action="approve",
            resource="project",
            resource_id=project.id,
            details={"comments": comments}
        )
        
        return project
    
    def reject_project(self, project_id: int, user_id: int, reason: str) -> Project:
        """
        Rejeita projeto
        """
        project = self.get_project_by_id(project_id)
        
        if project.status != ProjectStatus.UNDER_REVIEW:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projeto não está em análise"
            )
        
        project.status = ProjectStatus.REJECTED
        project.rejection_date = datetime.utcnow()
        project.rejection_reason = reason
        project.technical_opinion = reason
        project.technical_opinion_by = str(user_id)
        project.technical_opinion_date = datetime.utcnow()
        
        # Decrementar contador da instituição
        institution = project.institution
        institution.active_projects_count = max(0, institution.active_projects_count - 1)
        
        self.db.commit()
        
        # Notificações
        self.notification_service.notify_project_rejected(project, reason)
        
        # Auditoria
        self.audit_service.log_action(
            user_id=user_id,
            action="reject",
            resource="project",
            resource_id=project.id,
            details={"reason": reason}
        )
        
        return project
    
    def add_monitoring_report(
        self,
        project_id: int,
        report_data: Dict[str, Any],
        user_id: int
    ) -> ProjectMonitoring:
        """
        Adiciona relatório de monitoramento
        """
        project = self.get_project_by_id(project_id)
        
        if project.status not in [ProjectStatus.IN_EXECUTION, ProjectStatus.MONITORING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projeto não está em execução"
            )
        
        report = ProjectMonitoring(
            project_id=project_id,
            report_type=report_data["report_type"],
            report_period=report_data["report_period"],
            report_date=datetime.utcnow(),
            activities_performed=report_data.get("activities_performed"),
            results_achieved=report_data.get("results_achieved"),
            difficulties_encountered=report_data.get("difficulties_encountered"),
            corrective_actions=report_data.get("corrective_actions"),
            beneficiaries_attended=report_data.get("beneficiaries_attended", 0),
            budget_executed=report_data.get("budget_executed", 0)
        )
        
        self.db.add(report)
        
        # Atualizar métricas do projeto
        project.budget_executed += Decimal(report.budget_executed)
        project.direct_beneficiaries += report.beneficiaries_attended
        
        # Atualizar flag de relatórios pendentes
        project.has_pending_reports = False
        
        self.db.commit()
        
        # Auditoria
        self.audit_service.log_action(
            user_id=user_id,
            action="add_monitoring",
            resource="project",
            resource_id=project_id,
            details={
                "report_type": report.report_type,
                "period": report.report_period
            }
        )
        
        return report
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Busca projeto por ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_projects_by_institution(
        self,
        institution_id: int,
        status_filter: Optional[ProjectStatus] = None
    ) -> List[Project]:
        """Busca projetos de uma instituição"""
        query = self.db.query(Project).filter(
            Project.institution_id == institution_id
        )
        
        if status_filter:
            query = query.filter(Project.status == status_filter)
        
        return query.order_by(Project.created_at.desc()).all()
    
    def search_projects(
        self,
        search_term: str = None,
        status: Optional[ProjectStatus] = None,
        priority_area_id: Optional[int] = None,
        institution_id: Optional[int] = None,
        field_of_action: Optional[FieldOfAction] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Busca avançada de projetos
        """
        query = self.db.query(Project)
        
        if search_term:
            query = query.filter(
                or_(
                    Project.title.ilike(f"%{search_term}%"),
                    Project.description.ilike(f"%{search_term}%"),
                    Project.protocol_number.ilike(f"%{search_term}%")
                )
            )
        
        if status:
            query = query.filter(Project.status == status)
        
        if priority_area_id:
            query = query.filter(Project.priority_area_id == priority_area_id)
        
        if institution_id:
            query = query.filter(Project.institution_id == institution_id)
        
        if field_of_action:
            query = query.filter(Project.field_of_action == field_of_action)
        
        return query.offset(skip).limit(limit).all()