"""
Project Service
Serviços de negócio para projetos PRONAS/PCD
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app.domain.entities.project import Project, ProjectStatus, ProjectType
from app.domain.entities.user import User, UserRole
from app.domain.repositories.project import ProjectRepository
from app.domain.repositories.audit_log import AuditLogRepository
from app.domain.entities.audit_log import AuditAction, AuditResource


class ProjectService:
    """Serviços de negócio para projetos"""
    
    def __init__(
        self, 
        project_repo: ProjectRepository,
        audit_repo: AuditLogRepository
    ):
        self.project_repo = project_repo
        self.audit_repo = audit_repo
    
    async def create_project(
        self,
        project_data: Dict[str, Any],
        created_by: User,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> Project:
        """Criar novo projeto"""
        # Validações de negócio
        self._validate_project_budget(project_data)
        self._validate_project_dates(project_data)
        
        # Definir valores padrão
        project_data.update({
            "status": ProjectStatus.DRAFT,
            "created_at": datetime.utcnow(),
            "created_by": created_by.id,
        })
        
        # Verificar se usuário pode criar projeto para a instituição
        if created_by.role != UserRole.ADMIN:
            if project_data.get("institution_id") != created_by.institution_id:
                raise ValueError("Usuário não pode criar projeto para outra instituição")
        
        # Criar projeto
        project = await self.project_repo.create(project_data)
        
        # Log da criação
        await self.audit_repo.create_log(
            action=AuditAction.CREATE,
            resource=AuditResource.PROJECT,
            resource_id=project.id,
            user_id=created_by.id,
            user_email=created_by.email,
            user_role=created_by.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Projeto criado: {project.title}",
            new_values={
                "title": project.title,
                "type": project.type,
                "institution_id": project.institution_id,
                "total_budget": float(project.total_budget)
            },
            success=True
        )
        
        return project
    
    async def submit_project(
        self,
        project_id: int,
        submitted_by: User,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> bool:
        """Submeter projeto para análise"""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return False
        
        # Verificar se pode ser submetido
        if not project.can_be_submitted():
            raise ValueError("Projeto não pode ser submetido. Verifique documentação.")
        
        # Verificar permissões
        if not self._can_user_modify_project(submitted_by, project):
            raise ValueError("Usuário não tem permissão para submeter este projeto")
        
        # Atualizar status
        success = await self.project_repo.update_status(
            project_id, 
            ProjectStatus.SUBMITTED
        )
        
        # Log da submissão
        await self.audit_repo.create_log(
            action=AuditAction.UPDATE,
            resource=AuditResource.PROJECT,
            resource_id=project_id,
            user_id=submitted_by.id,
            user_email=submitted_by.email,
            user_role=submitted_by.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Projeto submetido para análise: {project.title}",
            previous_values={"status": project.status},
            new_values={"status": ProjectStatus.SUBMITTED, "submitted_at": datetime.utcnow()},
            success=success
        )
        
        return success
    
    async def review_project(
        self,
        project_id: int,
        reviewer: User,
        decision: ProjectStatus,  # APPROVED ou REJECTED
        review_notes: str,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> bool:
        """Revisar projeto (aprovar ou rejeitar)"""
        if decision not in [ProjectStatus.APPROVED, ProjectStatus.REJECTED]:
            raise ValueError("Decisão deve ser APPROVED ou REJECTED")
        
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return False
        
        # Verificar se está em revisão
        if project.status not in [ProjectStatus.SUBMITTED, ProjectStatus.UNDER_REVIEW]:
            raise ValueError("Projeto não está em status de revisão")
        
        # Verificar permissões (admin ou auditor)
        if reviewer.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
            raise ValueError("Usuário não tem permissão para revisar projetos")
        
        # Atualizar projeto
        success = await self.project_repo.update_status(
            project_id,
            decision,
            reviewer_id=reviewer.id,
            review_notes=review_notes
        )
        
        # Log da revisão
        await self.audit_repo.create_log(
            action=AuditAction.APPROVE if decision == ProjectStatus.APPROVED else AuditAction.REJECT,
            resource=AuditResource.PROJECT,
            resource_id=project_id,
            user_id=reviewer.id,
            user_email=reviewer.email,
            user_role=reviewer.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Projeto {'aprovado' if decision == ProjectStatus.APPROVED else 'rejeitado'}: {project.title}",
            previous_values={"status": project.status},
            new_values={
                "status": decision,
                "reviewer_id": reviewer.id,
                "review_notes": review_notes,
                "reviewed_at": datetime.utcnow()
            },
            success=success
        )
        
        return success
    
    async def get_projects_by_user_access(self, user: User) -> List[Project]:
        """Obter projetos baseado no acesso do usuário"""
        if user.role == UserRole.ADMIN:
            return await self.project_repo.get_all()
        elif user.role == UserRole.AUDITOR:
            return await self.project_repo.get_all()
        elif user.role in [UserRole.GESTOR, UserRole.OPERADOR]:
            if user.institution_id:
                return await self.project_repo.get_by_institution(user.institution_id)
        
        return []
    
    def _validate_project_budget(self, project_data: Dict[str, Any]) -> None:
        """Validar orçamento do projeto"""
        total_budget = Decimal(str(project_data.get("total_budget", 0)))
        pronas_funding = Decimal(str(project_data.get("pronas_funding", 0)))
        own_funding = Decimal(str(project_data.get("own_funding", 0)))
        other_funding = Decimal(str(project_data.get("other_funding", 0)))
        
        calculated_total = pronas_funding + own_funding + other_funding
        
        if abs(calculated_total - total_budget) > Decimal("0.01"):
            raise ValueError("Soma dos financiamentos não confere com orçamento total")
        
        if pronas_funding > total_budget * Decimal("0.8"):  # Max 80% PRONAS
            raise ValueError("Financiamento PRONAS não pode exceder 80% do orçamento total")
    
    def _validate_project_dates(self, project_data: Dict[str, Any]) -> None:
        """Validar datas do projeto"""
        start_date = project_data.get("start_date")
        end_date = project_data.get("end_date")
        
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        
        if start_date and end_date:
            if start_date >= end_date:
                raise ValueError("Data de início deve ser anterior à data de fim")
            
            if start_date < date.today():
                raise ValueError("Data de início não pode ser no passado")
    
    def _can_user_modify_project(self, user: User, project: Project) -> bool:
        """Verificar se usuário pode modificar projeto"""
        if user.role == UserRole.ADMIN:
            return True
        
        if user.role in [UserRole.GESTOR, UserRole.OPERADOR]:
            return user.institution_id == project.institution_id
        
        return False