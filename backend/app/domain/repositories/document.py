"""
Document Repository Interface
"""

from abc import abstractmethod
from typing import Optional, List
from app.domain.repositories.base import BaseRepository
from app.domain.entities.document import Document, DocumentType, DocumentStatus


class DocumentRepository(BaseRepository[Document, int]):
    """Interface do repositório de documentos"""
    
    @abstractmethod
    async def get_by_project(self, project_id: int) -> List[Document]:
        """Buscar documentos de um projeto"""
        pass
    
    @abstractmethod
    async def get_by_institution(self, institution_id: int) -> List[Document]:
        """Buscar documentos de uma instituição"""
        pass
    
    @abstractmethod
    async def get_by_type(self, document_type: DocumentType) -> List[Document]:
        """Buscar documentos por tipo"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: DocumentStatus) -> List[Document]:
        """Buscar documentos por status"""
        pass
    
    @abstractmethod
    async def get_by_uploader(self, user_id: int) -> List[Document]:
        """Buscar documentos por usuário que fez upload"""
        pass
    
    @abstractmethod
    async def get_by_file_hash(self, file_hash: str) -> Optional[Document]:
        """Buscar documento por hash (verificar duplicatas)"""
        pass
    
    @abstractmethod
    async def get_pending_review(self) -> List[Document]:
        """Buscar documentos pendentes de revisão"""
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        document_id: int, 
        status: DocumentStatus,
        reviewer_id: Optional[int] = None,
        review_notes: Optional[str] = None
    ) -> bool:
        """Atualizar status do documento"""
        pass
    
    @abstractmethod
    async def get_documents_for_retention(self) -> List[Document]:
        """Buscar documentos para aplicar política de retenção (LGPD)"""
        pass
    
    @abstractmethod
    async def search_by_filename(self, filename_query: str) -> List[Document]:
        """Buscar documentos por nome do arquivo"""
        pass
    
    @abstractmethod
    async def get_total_size_by_institution(self, institution_id: int) -> int:
        """Obter tamanho total de documentos por instituição"""
        pass