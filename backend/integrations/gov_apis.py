"""
Integração com APIs Governamentais
ComprasNet, ViaCEP, ReceitaWS, SICONV
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import hmac
import base64
import logging

from core.config import settings

logger = logging.getLogger(__name__)

class GovAPIsIntegration:
    """Classe unificada para integração com APIs governamentais"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "User-Agent": "Sistema PRONAS/PCD v2.0",
            "Accept": "application/json"
        }
    
    # ==================== ComprasNet ====================
    
    async def consultar_preco_comprasnet(
        self,
        codigo_item: str,
        descricao: Optional[str] = None,
        uasg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta preços de referência no ComprasNet
        API: https://compras.dados.gov.br/docs/home.html
        """
        base_url = "https://compras.dados.gov.br/api/v1"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Buscar materiais
                params = {"codigo": codigo_item}
                if descricao:
                    params["descricao"] = descricao
                
                response = await client.get(
                    f"{base_url}/materiais.json",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    materiais = data.get("_embedded", {}).get("materiais", [])
                    
                    if materiais:
                        # Buscar preços praticados
                        precos = []
                        for material in materiais[:5]:  # Limitar a 5 items
                            preco_response = await client.get(
                                f"{base_url}/contratos_item_contrato.json",
                                params={"id_item_material": material["id"]},
                                headers=self.headers
                            )
                            
                            if preco_response.status_code == 200:
                                preco_data = preco_response.json()
                                itens = preco_data.get("_embedded", {}).get("contratos", [])
                                
                                for item in itens:
                                    precos.append({
                                        "valor_unitario": item.get("vl_unitario", 0),
                                        "quantidade": item.get("qt_contratada", 0),
                                        "data_contrato": item.get("data_assinatura"),
                                        "uasg": item.get("uasg", {}).get("nome"),
                                        "fornecedor": item.get("fornecedor", {}).get("nome")
                                    })
                        
                        # Calcular estatísticas
                        valores = [p["valor_unitario"] for p in precos if p["valor_unitario"] > 0]
                        
                        return {
                            "success": True,
                            "codigo_item": codigo_item,
                            "descricao": materiais[0].get("descricao"),
                            "preco_medio": sum(valores) / len(valores) if valores else 0,
                            "preco_minimo": min(valores) if valores else 0,
                            "preco_maximo": max(valores) if valores else 0,
                            "quantidade_registros": len(precos),
                            "precos_detalhados": precos[:10],
                            "fonte": "ComprasNet",
                            "data_consulta": datetime.utcnow().isoformat()
                        }
                    
                return {
                    "success": False,
                    "error": "Item não encontrado no ComprasNet"
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar ComprasNet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== ViaCEP ====================
    
    async def consultar_cep(self, cep: str) -> Dict[str, Any]:
        """
        Consulta endereço via CEP
        API: https://viacep.com.br/
        """
        # Limpar CEP
        cep_clean = cep.replace("-", "").replace(".", "").strip()
        
        if len(cep_clean) != 8:
            return {
                "success": False,
                "error": "CEP deve conter 8 dígitos"
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"https://viacep.com.br/ws/{cep_clean}/json/",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("erro"):
                        return {
                            "success": False,
                            "error": "CEP não encontrado"
                        }
                    
                    return {
                        "success": True,
                        "cep": data.get("cep"),
                        "logradouro": data.get("logradouro"),
                        "complemento": data.get("complemento"),
                        "bairro": data.get("bairro"),
                        "localidade": data.get("localidade"),
                        "uf": data.get("uf"),
                        "ibge": data.get("ibge"),
                        "gia": data.get("gia"),
                        "ddd": data.get("ddd"),
                        "siafi": data.get("siafi")
                    }
                
                return {
                    "success": False,
                    "error": f"Erro na consulta: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar ViaCEP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== ReceitaWS ====================
    
    async def consultar_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Consulta dados de CNPJ
        API: https://www.receitaws.com.br/
        Nota: API gratuita tem limite de consultas
        """
        # Limpar CNPJ
        cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        
        if len(cnpj_clean) != 14:
            return {
                "success": False,
                "error": "CNPJ deve conter 14 dígitos"
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"https://www.receitaws.com.br/v1/cnpj/{cnpj_clean}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "ERROR":
                        return {
                            "success": False,
                            "error": data.get("message", "CNPJ inválido")
                        }
                    
                    return {
                        "success": True,
                        "cnpj": data.get("cnpj"),
                        "tipo": data.get("tipo"),
                        "abertura": data.get("abertura"),
                        "nome": data.get("nome"),
                        "fantasia": data.get("fantasia"),
                        "porte": data.get("porte"),
                        "natureza_juridica": data.get("natureza_juridica"),
                        "atividade_principal": data.get("atividade_principal"),
                        "atividades_secundarias": data.get("atividades_secundarias"),
                        "logradouro": data.get("logradouro"),
                        "numero": data.get("numero"),
                        "complemento": data.get("complemento"),
                        "bairro": data.get("bairro"),
                        "municipio": data.get("municipio"),
                        "uf": data.get("uf"),
                        "cep": data.get("cep"),
                        "email": data.get("email"),
                        "telefone": data.get("telefone"),
                        "situacao": data.get("situacao"),
                        "data_situacao": data.get("data_situacao"),
                        "motivo_situacao": data.get("motivo_situacao"),
                        "situacao_especial": data.get("situacao_especial"),
                        "data_situacao_especial": data.get("data_situacao_especial"),
                        "capital_social": data.get("capital_social"),
                        "qsa": data.get("qsa"),  # Quadro societário
                        "ultima_atualizacao": data.get("ultima_atualizacao")
                    }
                
                elif response.status_code == 429:
                    return {
                        "success": False,
                        "error": "Limite de consultas excedido. Tente novamente mais tarde."
                    }
                
                return {
                    "success": False,
                    "error": f"Erro na consulta: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar ReceitaWS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== SICONV ====================
    
    async def consultar_convenios_siconv(
        self,
        cnpj_proponente: Optional[str] = None,
        uf: Optional[str] = None,
        ano: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Consulta convênios no SICONV
        API: http://api.convenios.gov.br/siconv/doc/
        """
        base_url = "http://api.convenios.gov.br/siconv/v1"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {}
                if cnpj_proponente:
                    params["cnpj_proponente"] = cnpj_proponente.replace(".", "").replace("/", "").replace("-", "")
                if uf:
                    params["uf_proponente"] = uf.upper()
                if ano:
                    params["ano_convenio"] = ano
                
                response = await client.get(
                    f"{base_url}/consulta/convenios.json",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    convenios = data.get("convenios", [])
                    
                    return {
                        "success": True,
                        "total_convenios": len(convenios),
                        "convenios": [
                            {
                                "numero": c.get("numero_convenio"),
                                "objeto": c.get("objeto_convenio"),
                                "orgao": c.get("nome_orgao"),
                                "proponente": c.get("nome_proponente"),
                                "valor_global": c.get("valor_global"),
                                "valor_repasse": c.get("valor_repasse"),
                                "valor_contrapartida": c.get("valor_contrapartida"),
                                "data_inicio": c.get("data_inicio_vigencia"),
                                "data_fim": c.get("data_fim_vigencia"),
                                "situacao": c.get("situacao_convenio")
                            }
                            for c in convenios[:20]  # Limitar a 20 resultados
                        ],
                        "fonte": "SICONV",
                        "data_consulta": datetime.utcnow().isoformat()
                    }
                
                return {
                    "success": False,
                    "error": f"Erro na consulta: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar SICONV: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== Validação de Certidões ====================
    
    async def validar_certidao_federal(self, cnpj: str, codigo_certidao: str) -> Dict[str, Any]:
        """
        Valida Certidão de Débitos Relativos a Créditos Tributários Federais
        Site: http://servicos.receita.fazenda.gov.br/
        """
        # Esta é uma simulação - em produção, seria necessário integração real
        # com os sistemas da RFB usando certificado digital
        
        return {
            "success": True,
            "valida": True,
            "cnpj": cnpj,
            "razao_social": "Nome da Empresa",
            "emissao": datetime.utcnow().isoformat(),
            "validade": (datetime.utcnow().replace(day=1).replace(month=datetime.utcnow().month + 6)).isoformat(),
            "codigo_controle": codigo_certidao,
            "observacao": "Certidão válida para o CNPJ da matriz e suas filiais"
        }
    
    async def validar_certidao_fgts(self, cnpj: str, codigo_crf: str) -> Dict[str, Any]:
        """
        Valida Certificado de Regularidade do FGTS
        Site: https://consulta-crf.caixa.gov.br/
        """
        # Simulação - implementar integração real em produção
        
        return {
            "success": True,
            "valida": True,
            "cnpj": cnpj,
            "razao_social": "Nome da Empresa",
            "emissao": datetime.utcnow().isoformat(),
            "validade": (datetime.utcnow().replace(day=datetime.utcnow().day + 30)).isoformat(),
            "numero_crf": codigo_crf,
            "situacao": "Regular"
        }
    
    async def validar_certidao_trabalhista(self, cnpj: str, codigo_cndt: str) -> Dict[str, Any]:
        """
        Valida Certidão Negativa de Débitos Trabalhistas
        Site: http://www.tst.jus.br/certidao
        """
        # Simulação - implementar integração real em produção
        
        return {
            "success": True,
            "valida": True,
            "cnpj": cnpj,
            "razao_social": "Nome da Empresa",
            "emissao": datetime.utcnow().isoformat(),
            "validade": (datetime.utcnow().replace(day=1).replace(month=datetime.utcnow().month + 6)).isoformat(),
            "numero_certidao": codigo_cndt,
            "situacao": "Negativa"
        }
    
    # ==================== Tabela de Naturezas de Despesa ====================
    def get_naturezas_despesa(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retorna tabela de naturezas de despesa conforme Portaria 448/2002
        """
        return {
            "despesas_correntes": [
                {"codigo": "3.1.90.04", "descricao": "Contratação por Tempo Determinado"},
                {"codigo": "3.1.90.11", "descricao": "Vencimentos e Vantagens Fixas - Pessoal Civil"},
                {"codigo": "3.3.90.14", "descricao": "Diárias - Pessoal Civil"},
                {"codigo": "3.3.90.30", "descricao": "Material de Consumo"},
                {"codigo": "3.3.90.33", "descricao": "Passagens e Despesas com Locomoção"},
                {"codigo": "3.3.90.36", "descricao": "Outros Serviços de Terceiros - Pessoa Física"},
                {"codigo": "3.3.90.39", "descricao": "Outros Serviços de Terceiros - Pessoa Jurídica"},
                {"codigo": "3.3.90.47", "descricao": "Obrigações Tributárias e Contributivas"},
                {"codigo": "3.3.90.48", "descricao": "Outros Auxílios Financeiros a Pessoas Físicas"},
            ],
            "despesas_capital": [
                {"codigo": "4.4.90.51", "descricao": "Obras e Instalações"},
                {"codigo": "4.4.90.52", "descricao": "Equipamentos e Material Permanente"},
                {"codigo": "4.4.90.61", "descricao": "Aquisição de Imóveis"},
            ],
            "pronas_pcd_especificas": [
                {"codigo": "3.3.50.41", "descricao": "Contribuições - PRONAS/PCD"},
                {"codigo": "3.3.50.43", "descricao": "Subvenções Sociais - PRONAS/PCD"},
                {"codigo": "3.3.90.39.99", "descricao": "Auditoria Independente (obrigatória)"},
                {"codigo": "3.3.90.39.98", "descricao": "Captação de Recursos (máx 5% ou R$ 50.000)"},
            ]
        }
    
    async def validar_natureza_despesa(self, codigo: str) -> bool:
        """
        Valida se código de natureza de despesa é válido para PRONAS/PCD
        """
        naturezas = self.get_naturezas_despesa()
        todos_codigos = []
        
        for categoria in naturezas.values():
            todos_codigos.extend([item["codigo"] for item in categoria])
        
        # Aceitar código com ou sem pontos
        codigo_limpo = codigo.replace(".", "")
        
        for codigo_valido in todos_codigos:
            if codigo_valido.replace(".", "") == codigo_limpo:
                return True
        
        return False