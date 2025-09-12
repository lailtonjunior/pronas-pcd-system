# CRIAR: backend/integrations/comprasnet.py
import httpx
from typing import Dict, Any, Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class ComprasNetIntegration:
    """Integração com API ComprasNet para consulta de preços e licitações"""
    
    BASE_URL = "https://compras.dados.gov.br/api/v1"
    
    async def consultar_preco_referencia(
        self, 
        codigo_item: str,
        uasg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta preço de referência no ComprasNet
        
        Args:
            codigo_item: Código CATMAT/CATSER
            uasg: Código da UASG (opcional)
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "codigo_item": codigo_item,
                    "id_uasg": uasg
                } if uasg else {"codigo_item": codigo_item}
                
                response = await client.get(
                    f"{self.BASE_URL}/materiais.json",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "data": self._processar_precos(data),
                        "fonte": "ComprasNet"
                    }
                else:
                    logger.error(f"Erro ComprasNet: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Status code: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Erro na integração ComprasNet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _processar_precos(self, data: Dict) -> Dict[str, Any]:
        """Processa dados de preços do ComprasNet"""
        items = data.get("_embedded", {}).get("materiais", [])
        
        if not items:
            return {"preco_medio": 0, "quantidade_registros": 0}
        
        precos = [item.get("valor_unitario", 0) for item in items if item.get("valor_unitario")]
        
        return {
            "preco_medio": sum(precos) / len(precos) if precos else 0,
            "preco_minimo": min(precos) if precos else 0,
            "preco_maximo": max(precos) if precos else 0,
            "quantidade_registros": len(precos),
            "items": items[:10]  # Primeiros 10 registros
        }
    
    async def validar_natureza_despesa(self, codigo_natureza: str) -> bool:
        """
        Valida código de natureza de despesa conforme Portaria 448/2002
        """
        codigos_validos = [
            "339030",  # Material de Consumo
            "339036",  # Outros Serviços de Terceiros - Pessoa Física
            "339039",  # Outros Serviços de Terceiros - Pessoa Jurídica
            "449051",  # Obras e Instalações
            "449052",  # Equipamentos e Material Permanente
        ]
        return codigo_natureza in codigos_validos