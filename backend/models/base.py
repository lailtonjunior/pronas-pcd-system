"""
Base Model - Common Fields and Behaviors
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AuditMixin:
    """Mixin for audit fields"""
    
    created_by = Column(String(100), nullable=True, index=True)
    updated_by = Column(String(100), nullable=True, index=True)

class BaseModel(Base, TimestampMixin, AuditMixin):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: dict, exclude: list = None):
        """Update model from dictionary"""
        exclude = exclude or ['id', 'created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_by_id(cls, db: Session, id: int):
        """Get instance by ID"""
        return db.query(cls).filter(cls.id == id).first()
    
    def save(self, db: Session):
        """Save instance to database"""
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    def delete(self, db: Session):
        """Delete instance from database"""
        db.delete(self)
        db.commit()
