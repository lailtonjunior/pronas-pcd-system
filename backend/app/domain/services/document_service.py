"""
Document Service
Serviços de negócio para documentos
"""

import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.domain.entities.document import Document, DocumentType, DocumentStatus
from app.domain.entities.user import User, UserRole
from app.domain.repositories.document import DocumentRepository
from app.domain.repositories.audit_log import AuditLogRepository
from app.domain.entities.audit_log import AuditAction, AuditResource


class DocumentService:
    """Serviços de negócio para documentos"""
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        audit_repo: AuditLogRepository
    ):
        self.document_repo = document_repo
        self.audit_repo = audit_repo
    
    async def upload_document(
        self,
        file_content: bytes,
        original_filename: str,
        document_type: DocumentType,
        project_id: Optional[int],
        institution_id: Optional[int],
        uploaded_by: User,
        description: Optional[str],
        contains_personal_data: bool,
        data_classification: str,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> Document:
        """Fazer upload de documento"""
        
        # Gerar hash do arquivo para verificar duplicatas
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Verificar se arquivo já existe
        existing_doc = await self.document_repo.get_by_file_hash(file_hash)
        if existing_doc:
            raise ValueError("Documento já existe no sistema")
        
        # Gerar nome único para o arquivo
        file_extension = Path(original_filename).suffix
        unique_filename = f"{datetime.utcnow().timestamp()}_{file_hash[:8]}{file_extension}"
        
        # Dados do documento
        document_data = {
            "filename": unique_filename,
            "original_filename": original_filename,
            "content_type": self._get_content_type(file_extension),
            "size_bytes": len(file_content),
            "file_path": f"documents/{unique_filename}",
            "document_type": document_type,
            "status": DocumentStatus.UPLOADED,
            "project_id": project_id,
            "institution_id": institution_id,
            "description": description,
            "version": 1,
            "file_hash": file_hash,
            "uploaded_by": uploaded_by.id,
            "uploaded_at": datetime.utcnow(),
            "contains_personal_data": contains_personal_data,
            "data_classification": data_classification,
            "retention_period_months": self._get_retention_period(document_type, contains_personal_data)
        }
        
        # Verificar permissões
        self._validate_upload_permissions(uploaded_by, project_id, institution_id)
        
        # Criar documento no banco
        document = await self.document_repo.create(document_data)
        
        # Log do upload
        await self.audit_repo.create_log(
            action=AuditAction.UPLOAD,
            resource=AuditResource.DOCUMENT,
            resource_id=document.id,
            user_id=uploaded_by.id,
            user_email=uploaded_by.email,
            user_role=uploaded_by.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Documento enviado: {original_filename}",
            new_values={
                "filename": original_filename,
                "type": document_type,
                "size_bytes": len(file_content),
                "contains_personal_data": contains_personal_data
            },
            success=True,
            data_sensitivity=data_classification
        )
        
        return document
    
    async def review_document(
        self,
        document_id: int,
        reviewer: User,
        decision: DocumentStatus,  # APPROVED ou REJECTED
        review_notes: str,
        ip_address: str,
        user_agent: str,
        session_id: str
    ) -> bool:
        """Revisar documento"""
        if decision not in [DocumentStatus.APPROVED, DocumentStatus.REJECTED]:
            raise ValueError("Decisão deve ser APPROVED ou REJECTED")
        
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            return False
        
        # Verificar permissões
        if reviewer.role not in [UserRole.ADMIN, UserRole.AUDITOR]:
            raise ValueError("Usuário não tem permissão para revisar documentos")
        
        # Atualizar status
        success = await self.document_repo.update_status(
            document_id,
            decision,
            reviewer_id=reviewer.id,
            review_notes=review_notes
        )
        
        # Log da revisão
        await self.audit_repo.create_log(
            action=AuditAction.APPROVE if decision == DocumentStatus.APPROVED else AuditAction.REJECT,
            resource=AuditResource.DOCUMENT,
            resource_id=document_id,
            user_id=reviewer.id,
            user_email=reviewer.email,
            user_role=reviewer.role,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            description=f"Documento {'aprovado' if decision == DocumentStatus.APPROVED else 'rejeitado'}: {document.original_filename}",
            previous_values={"status": document.status},
            new_values={
                "status": decision,
                "reviewer_id": reviewer.id,
                "review_notes": review_notes,
                "reviewed_at": datetime.utcnow()
            },
            success=success,
            data_sensitivity=document.data_classification
        )
        
        return success
    
    async def get_documents_by_user_access(self, user: User) -> List[Document]:
        """Obter documentos baseado no acesso do usuário"""
        if user.role == UserRole.ADMIN:
            return await self.document_repo.get_all()
        elif user.role == UserRole.AUDITOR:
            return await self.document_repo.get_all()
        elif user.role in [UserRole.GESTOR, UserRole.OPERADOR]:
            if user.institution_id:
                return await self.document_repo.get_by_institution(user.institution_id)
        
        return []
    
    def _validate_upload_permissions(
        self, 
        user: User, 
        project_id: Optional[int], 
        institution_id: Optional[int]
    ) -> None:
        """Validar permissões de upload"""
        if user.role == UserRole.ADMIN:
            return  # Admin pode fazer upload para qualquer lugar
        
        if user.role in [UserRole.GESTOR, UserRole.OPERADOR]:
            if institution_id and institution_id != user.institution_id:
                raise ValueError("Usuário não pode fazer upload para outra instituição")
            if not institution_id and not project_id:
                raise ValueError("Documento deve estar associado a uma instituição ou projeto")
        
        if user.role == UserRole.AUDITOR:
            raise ValueError("Auditores não podem fazer upload de documentos")
    
    def _get_content_type(self, file_extension: str) -> str:
        """Obter content type baseado na extensão"""
        content_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain",
        }
        return content_types.get(file_extension.lower(), "application/octet-stream")
    
    def _get_retention_period(self, document_type: DocumentType, contains_personal_data: bool) -> Optional[int]:
        """Definir período de retenção baseado no tipo e dados pessoais (LGPD)"""
        # Períodos em meses
        if contains_personal_data:
            # Dados pessoais - períodos mais restritivos
            retention_periods = {
                DocumentType.TECHNICAL_PROPOSAL: 60,  # 5 anos
                DocumentType.DETAILED_BUDGET: 60,
                DocumentType.PROGRESS_REPORT: 84,    # 7 anos
                DocumentType.FINAL_REPORT: 120,      # 10 anos
                DocumentType.CERTIFICATION: 120,
                DocumentType.CONTRACT: 120,
                DocumentType.OTHER: 36               # 3 anos
            }
        else:
            # Documentos sem dados pessoais
            retention_periods = {
                DocumentType.TECHNICAL_PROPOSAL: 84,   # 7 anos
                DocumentType.DETAILED_BUDGET: 84,
                DocumentType.PROGRESS_REPORT: 120,    # 10 anos
                DocumentType.FINAL_REPORT: 180,       # 15 anos
                DocumentType.CERTIFICATION: 180,
                DocumentType.CONTRACT: 180,
                DocumentType.OTHER: 60                # 5 anos
            }
        
        return retention_periods.get(document_type, 36)  # Default 3 anos