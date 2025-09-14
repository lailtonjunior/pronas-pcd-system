"""
Base Pydantic Schemas
Schemas base para requests e responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Schema base com configuração padrão"""
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseSchema):
    """Response base com campos de auditoria"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaginationParams(BaseSchema):
    """Parâmetros de paginação"""
    skip: int = 0
    limit: int = 100
    
    def validate_limit(self):
        if self.limit > 100:
            self.limit = 100
        return self


class PaginatedResponse(BaseSchema):
    """Response paginado"""
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(cls, items: list, total: int, skip: int, limit: int):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total
        )
