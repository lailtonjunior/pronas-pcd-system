from sqlalchemy.orm import Session
from . import models, schemas

def create_projeto(db: Session, projeto: schemas.ProjetoCreate):
    db_obj = models.Projeto(**projeto.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_projetos(db: Session, skip=0, limit=10):
    return db.query(models.Projeto).offset(skip).limit(limit).all()
