from typing import List, Optional
from sqlalchemy.orm import Session
from models.institution import Institution
from schemas.institution import InstitutionCreate, InstitutionUpdate
from datetime import datetime
import httpx

class InstitutionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def validate_cnpj(self, cnpj: str) -> dict:
        """Valida CNPJ na Receita Federal"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.receitaws.com.br/v1/cnpj/{cnpj.replace('.','').replace('/','').replace('-','')}"
            )
            return response.json() if response.status_code == 200 else None
    
    def create_institution(self, data: InstitutionCreate) -> Institution:
        """Cria nova instituição"""
        institution = Institution(**data.dict())
        self.db.add(institution)
        self.db.commit()
        self.db.refresh(institution)
        return institution
    
    def request_credential(self, institution_id: int) -> bool:
        """Solicita credenciamento (apenas junho/julho)"""
        current_month = datetime.now().month
        if current_month not in [6, 7]:
            raise ValueError("Credenciamento permitido apenas em junho e julho")
        
        institution = self.db.query(Institution).filter(Institution.id == institution_id).first()
        if institution:
            institution.credential_status = "pending"
            institution.credential_date = datetime.now()
            self.db.commit()
            return True
        return False