"""
SQLAlchemy Base Model
Modelo base para todas as tabelas
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()


class BaseModel(Base):
    """Modelo base com campos comuns"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        # Gerar nome da tabela automaticamente
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def dict(self):
        """Converter para dicionário"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
