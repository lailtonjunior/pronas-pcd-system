"""
Document Entity - Documentos do Sistema
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class DocumentType(str, Enum):
    """Tipos de documento"""
    TECHNICAL_PROPOSAL = "technical_proposal"
    DETAILED_BUDGET = "detailed_budget"
    PROGRESS_REPORT = "progress_report"
    FINAL_REPORT = "final_report"
    CERTIFICATION = "certification"
    CONTRACT = "contract"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Status do documento"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class Document:
    """Entidade de documento do domínio"""
    id: Optional[int]
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    file_path: str
    
    # Classificação
    document_type: DocumentType
    status: DocumentStatus
    
    # Relacionamentos
    project_id: Optional[int]
    institution_id: Optional[int]
    
    # Metadados
    description: Optional[str]
    version: int
    
    # Hash para integridade
    file_hash: str
    
    # Auditoria
    uploaded_by: int
    uploaded_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    
    # LGPD - Dados sensíveis
    contains_personal_data: bool
    data_classification: str  # "public", "internal", "confidential", "restricted"
    retention_period_months: Optional[int]
    
    def get_display_size(self) -> str:
        """Obter tamanho formatado para exibição"""
        size = self.size_bytes
        
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.1f} MB"
        else:
            return f"{size / (1024 ** 3):.1f} GB"
    
    def is_editable_by_user(self, user_id: int, user_role: str) -> bool:
        """Verificar se documento pode ser editado pelo usuário"""
        # Admin pode editar todos
        if user_role == "admin":
            return True
        
        # Usuário que fez upload pode editar se status permite
        if self.uploaded_by == user_id and self.status in ["uploaded", "rejected"]:
            return True
        
        return False