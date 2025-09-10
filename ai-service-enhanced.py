# ai_service_enhanced.py - Enhanced AI Service for PRONAS/PCD System
# Based on official PRONAS/PCD guidelines and regulations

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import asyncio
import logging
from datetime import datetime, timedelta
import json
import re
from schemas import *

logger = logging.getLogger(__name__)

class PronasAIEngine:
    """
    Sistema de IA especializado em PRONAS/PCD
    Baseado na Portaria de Consolidação nº 05/2017 - Anexo LXXXVI
    """
    
    def __init__(self):
        self.priority_areas = self._load_priority_areas()
        self.budget_templates = self._load_budget_templates()
        self.compliance_rules = self._load_compliance_rules()
        self.similar_projects_db = []  # Cache de projetos similares
        
    def _load_priority_areas(self) -> Dict[str, Dict]:
        """Carrega áreas prioritárias baseadas no Art. 10"""
        return {
            "QSS": {
                "name": "Qualificação de serviços de saúde",
                "description": "Adequação da ambiência de estabelecimentos",
                "typical_actions": [
                    "Adaptação arquitetônica para acessibilidade",
                    "Adequação de espaços terapêuticos", 
                    "Melhorias em infraestrutura assistencial",
                    "Instalação de equipamentos de acessibilidade"
                ],
                "typical_budget_distribution": {
                    "reformas": 0.60,
                    "material_permanente": 0.25,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "RPD": {
                "name": "Reabilitação/habilitação da pessoa com deficiência",
                "description": "Ações de reabilitação e habilitação",
                "typical_actions": [
                    "Atendimentos fisioterapêuticos",
                    "Terapia ocupacional",
                    "Fonoaudiologia",
                    "Atendimento psicológico",
                    "Reabilitação neurológica",
                    "Reabilitação auditiva e visual"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.50,
                    "material_consumo": 0.20,
                    "material_permanente": 0.15,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "DDP": {
                "name": "Diagnóstico diferencial da pessoa com deficiência", 
                "description": "Diagnóstico especializado e diferencial",
                "typical_actions": [
                    "Avaliações neuropsicológicas",
                    "Exames especializados",
                    "Consultas multiprofissionais",
                    "Diagnóstico precoce de deficiências",
                    "Avaliação funcional"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.45,
                    "material_consumo": 0.25,
                    "material_permanente": 0.15,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "EPD": {
                "name": "Identificação e estimulação precoce das deficiências",
                "description": "Detecção e intervenção precoce",
                "typical_actions": [
                    "Triagem neonatal ampliada",
                    "Estimulação precoce",
                    "Intervenção em desenvolvimento infantil",
                    "Acompanhamento de recém-nascidos de risco",
                    "Orientação familiar"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.55,
                    "material_consumo": 0.20,
                    "material_permanente": 0.10,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "ITR": {
                "name": "Adaptação, inserção e reinserção no trabalho",
                "description": "Inclusão e reinclusão no mercado de trabalho",
                "typical_actions": [
                    "Capacitação profissional",
                    "Adaptação de postos de trabalho",
                    "Orientação vocacional",
                    "Desenvolvimento de habilidades",
                    "Suporte à empregabilidade"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.40,
                    "material_consumo": 0.25,
                    "material_permanente": 0.20,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "APE": {
                "name": "Apoio à saúde por meio de práticas esportivas",
                "description": "Atividades esportivas como apoio à saúde", 
                "typical_actions": [
                    "Esporte adaptado",
                    "Atividades aquáticas terapêuticas",
                    "Educação física adaptada",
                    "Esporte paraolímpico",
                    "Recreação terapêutica"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.35,
                    "material_consumo": 0.25,
                    "material_permanente": 0.25,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "TAA": {
                "name": "Terapia assistida por animais",
                "description": "Terapia com animais como complemento",
                "typical_actions": [
                    "Equoterapia",
                    "Terapia com cães",
                    "Atividades assistidas por animais",
                    "Zooterapia",
                    "Cuidados com animais terapêuticos"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.40,
                    "material_consumo": 0.30,
                    "material_permanente": 0.15,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            },
            "APC": {
                "name": "Apoio à saúde por produção artística e cultural",
                "description": "Atividades artísticas e culturais",
                "typical_actions": [
                    "Arteterapia",
                    "Musicoterapia",
                    "Teatro terapêutico",
                    "Dança adaptada",
                    "Oficinas culturais",
                    "Atividades artísticas adaptadas"
                ],
                "typical_budget_distribution": {
                    "pessoal": 0.40,
                    "material_consumo": 0.30,
                    "material_permanente": 0.15,
                    "despesas_administrativas": 0.10,
                    "auditoria": 0.05
                }
            }
        }

    def _load_budget_templates(self) -> Dict[str, Dict]:
        """Templates de orçamento por categoria baseados na Portaria 448/2002"""
        return {
            "pessoal": {
                "coordinator": {"description": "Coordenador do Projeto", "hours": 20, "salary_range": (8000, 15000)},
                "therapist": {"description": "Terapeuta/Especialista", "hours": 40, "salary_range": (4000, 8000)},
                "assistant": {"description": "Auxiliar/Técnico", "hours": 40, "salary_range": (2000, 4000)},
                "administrative": {"description": "Apoio Administrativo", "hours": 20, "salary_range": (1500, 3000)}
            },
            "material_consumo": [
                "Material descartável para atendimentos",
                "Insumos terapêuticos",
                "Material de higiene e segurança",
                "Impressos e papelaria",
                "Material pedagógico adaptado"
            ],
            "material_permanente": [
                "Equipamentos terapêuticos",
                "Móveis adaptados", 
                "Equipamentos de informática",
                "Instrumentos de avaliação",
                "Dispositivos de acessibilidade"
            ],
            "despesas_administrativas": [
                "Energia elétrica (proporcional)",
                "Água e saneamento (proporcional)", 
                "Telefone e internet (proporcional)",
                "Material de limpeza",
                "Serviços de manutenção"
            ]
        }

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Regras de conformidade baseadas na legislação"""
        return {
            "project_submission": {
                "max_projects_per_institution": 3,
                "submission_period_days": 45,
                "required_fields": [
                    "title", "general_objective", "specific_objectives", 
                    "justification", "methodology", "budget_total", "timeline_months"
                ]
            },
            "budget_rules": {
                "min_captacao_percentage": 0.60,
                "max_captacao_percentage": 1.20,
                "max_captacao_absolute": 50000,
                "max_captacao_percentage_of_total": 0.05,
                "audit_required": True
            },
            "validation_rules": {
                "min_justification_chars": 500,
                "min_specific_objectives": 3,
                "min_timeline_months": 6,
                "max_timeline_months": 48,
                "required_team_roles": ["coordinator"]
            }
        }

    async def generate_project_from_guidelines(
        self,
        institution_data: Dict[str, Any],
        project_requirements: Dict[str, Any],
        priority_area_code: str
    ) -> AIProjectResponse:
        """
        Gera um projeto completo baseado nas diretrizes do PRONAS/PCD
        """
        try:
            # Validar área prioritária
            if priority_area_code not in self.priority_areas:
                raise ValueError(f"Área prioritária inválida: {priority_area_code}")
            
            area_info = self.priority_areas[priority_area_code]
            
            # Gerar estrutura básica do projeto
            project_base = await self._generate_project_structure(
                institution_data, project_requirements, area_info, priority_area_code
            )
            
            # Gerar equipe
            team_members = await self._generate_project_team(
                area_info, project_requirements.get('budget_total', 500000)
            )
            
            # Gerar orçamento
            budget_items = await self._generate_project_budget(
                area_info, project_requirements.get('budget_total', 500000)
            )
            
            # Gerar metas e indicadores
            goals = await self._generate_project_goals(area_info, project_requirements)
            
            # Gerar cronograma
            timeline = await self._generate_project_timeline(
                area_info, project_base.get('timeline_months', 24)
            )
            
            # Montar projeto completo
            project_create = ProjectCreate(
                title=project_base['title'],
                description=project_base['description'],
                field_of_action=FieldOfActionEnum.MEDICO_ASSISTENCIAL,
                priority_area_id=self._get_priority_area_id(priority_area_code),
                general_objective=project_base['general_objective'],
                specific_objectives=project_base['specific_objectives'],
                justification=project_base['justification'],
                target_audience=project_base['target_audience'],
                methodology=project_base['methodology'],
                expected_results=project_base['expected_results'],
                budget_total=Decimal(str(project_requirements.get('budget_total', 500000))),
                timeline_months=project_base['timeline_months'],
                team_members=team_members,
                budget_items=budget_items,
                goals=goals,
                timeline=timeline
            )
            
            # Validar projeto
            validation_results = await self._validate_project_compliance(project_create)
            
            # Calcular scores
            compliance_score = await self._calculate_compliance_score(project_create, validation_results)
            confidence_score = await self._calculate_confidence_score(project_create, area_info)
            
            # Gerar recomendações
            recommendations = await self._generate_recommendations(
                project_create, validation_results, area_info
            )
            
            # Buscar projetos similares
            similar_projects = await self._find_similar_projects(project_create)
            
            return AIProjectResponse(
                project=project_create,
                confidence_score=confidence_score,
                compliance_score=compliance_score,
                recommendations=recommendations,
                validation_results=validation_results,
                similar_projects=similar_projects
            )
            
        except Exception as e:
            logger.error(f"Erro na geração do projeto: {str(e)}")
            raise

    async def _generate_project_structure(
        self,
        institution_data: Dict,
        requirements: Dict,
        area_info: Dict,
        priority_area_code: str
    ) -> Dict[str, Any]:
        """Gera a estrutura básica do projeto"""
        
        institution_type = institution_data.get('institution_type', 'apae')
        institution_name = institution_data.get('name', 'Instituição')
        
        # Título personalizado por área
        title_templates = {
            "QSS": f"Qualificação e Adequação dos Serviços de Saúde - {institution_name}",
            "RPD": f"Programa de Reabilitação e Habilitação Integral - {institution_name}",
            "DDP": f"Centro de Diagnóstico Diferencial e Especializado - {institution_name}",
            "EPD": f"Programa de Estimulação e Intervenção Precoce - {institution_name}",
            "ITR": f"Programa de Inclusão e Capacitação Profissional - {institution_name}",
            "APE": f"Programa de Esporte Adaptado e Atividade Física - {institution_name}",
            "TAA": f"Programa de Terapia Assistida por Animais - {institution_name}",
            "APC": f"Programa de Arte e Cultura Terapêuticas - {institution_name}"
        }
        
        # Objetivos gerais por área
        general_objectives = {
            "QSS": f"Qualificar e adequar os serviços de saúde oferecidos pela {institution_name}, promovendo melhorias na ambiência e infraestrutura para garantir atendimento de qualidade às pessoas com deficiência, em conformidade com as normas de acessibilidade e diretrizes do PRONAS/PCD.",
            "RPD": f"Desenvolver e implementar programa abrangente de reabilitação e habilitação para pessoas com deficiência, oferecendo atendimento multiprofissional especializado que promova a funcionalidade, autonomia e qualidade de vida dos beneficiários.",
            "DDP": f"Estabelecer centro de referência para diagnóstico diferencial e especializado de pessoas com deficiência, oferecendo avaliações multiprofissionais precisas e precoces que fundamentem intervenções terapêuticas adequadas.",
            "EPD": f"Implementar programa de identificação, avaliação e estimulação precoce de deficiências, proporcionando intervenção oportuna no desenvolvimento infantil e orientação às famílias para maximizar o potencial de desenvolvimento das crianças.",
            "ITR": f"Desenvolver programa de capacitação profissional e inserção no mercado de trabalho para pessoas com deficiência, promovendo autonomia econômica e inclusão social através de formação especializada e apoio à empregabilidade.",
            "APE": f"Implementar programa de esporte adaptado e atividades físicas terapêuticas, promovendo a saúde, bem-estar e inclusão social de pessoas com deficiência através de práticas esportivas adequadas às suas necessidades específicas.",
            "TAA": f"Desenvolver programa de terapia assistida por animais como complemento terapêutico inovador, utilizando a interação pessoa-animal para promover benefícios físicos, emocionais e sociais aos beneficiários com deficiência.",
            "APC": f"Implementar programa de produção artística e cultural adaptada, utilizando expressões artísticas como ferramenta terapêutica para desenvolvimento pessoal, expressão criativa e inclusão social de pessoas with deficiência."
        }
        
        # Objetivos específicos por área
        specific_objectives = {
            "QSS": [
                "Adequar 100% dos espaços físicos às normas de acessibilidade (NBR 9050)",
                "Implantar sinalizações táteis, visuais e auditivas em todos os ambientes", 
                "Capacitar 100% da equipe em atendimento acessível e humanizado",
                "Estabelecer fluxos de atendimento otimizados para pessoas com deficiência"
            ],
            "RPD": [
                "Oferecer 2.000 atendimentos anuais de fisioterapia especializada",
                "Realizar 1.500 sessões anuais de terapia ocupacional",
                "Proporcionar 1.200 atendimentos anuais de fonoaudiologia",
                "Desenvolver protocolos de reabilitação individualizados para 100% dos usuários"
            ],
            "DDP": [
                "Realizar 800 avaliações diagnósticas especializadas anuais",
                "Estabelecer protocolos de diagnóstico diferencial padronizados",
                "Capacitar equipe multiprofissional em avaliação diagnóstica",
                "Desenvolver sistema de registro e acompanhamento longitudinal"
            ],
            "EPD": [
                "Avaliar 500 crianças anualmente para identificação precoce de deficiências",
                "Ofertas 300 vagas de estimulação precoce",
                "Capacitar 100% das famílias em técnicas de estimulação domiciliar",
                "Estabelecer rede de referência e contrarreferência com atenção básica"
            ],
            "ITR": [
                "Capacitar 200 pessoas com deficiência em atividades profissionais",
                "Estabelecer parcerias com 50 empresas para colocação profissional",
                "Atingir taxa de empregabilidade de 70% dos capacitados",
                "Desenvolver programa de acompanhamento pós-inserção por 12 meses"
            ],
            "APE": [
                "Atender 300 pessoas com deficiência em atividades esportivas adaptadas",
                "Oferecer 8 modalidades esportivas diferentes",
                "Formar e capacitar 20 atletas para competições paradesportivas",
                "Promover 4 eventos esportivos inclusivos anuais"
            ],
            "TAA": [
                "Realizar 1.000 sessões anuais de terapia assistida por animais",
                "Capacitar 10 profissionais em TAA",
                "Desenvolver protocolos específicos para diferentes deficiências",
                "Estabelecer programa de bem-estar animal certificado"
            ],
            "APC": [
                "Atender 250 pessoas em oficinas artísticas e culturais adaptadas",
                "Oferecer 6 modalidades artísticas diferentes",
                "Promover 4 apresentações e exposições anuais",
                "Capacitar familiares em atividades artísticas terapêuticas"
            ]
        }
        
        return {
            "title": title_templates.get(priority_area_code, f"Projeto {area_info['name']} - {institution_name}"),
            "description": f"Projeto desenvolvido pela {institution_name} na área de {area_info['name']}, visando {area_info['description'].lower()} de forma especializada e conforme diretrizes do PRONAS/PCD.",
            "general_objective": general_objectives.get(priority_area_code, area_info['description']),
            "specific_objectives": specific_objectives.get(priority_area_code, [
                "Implementar ações especializadas na área prioritária",
                "Capacitar equipe técnica especializada",
                "Estabelecer indicadores de qualidade e impacto"
            ]),
            "justification": await self._generate_justification(area_info, institution_data, requirements),
            "target_audience": await self._generate_target_audience(area_info, requirements),
            "methodology": await self._generate_methodology(area_info, requirements),
            "expected_results": await self._generate_expected_results(area_info, requirements),
            "timeline_months": requirements.get('timeline_months', 24)
        }

    async def _generate_justification(
        self, area_info: Dict, institution_data: Dict, requirements: Dict
    ) -> str:
        """Gera justificativa detalhada baseada nas diretrizes"""
        
        institution_name = institution_data.get('name', 'Instituição')
        city = institution_data.get('city', 'município')
        state = institution_data.get('state', 'estado')
        
        justification = f"""
Este projeto se justifica pela necessidade urgente de {area_info['description'].lower()} no contexto da {institution_name}, localizada em {city}/{state}.

CONTEXTO EPIDEMIOLÓGICO E SOCIAL:
Segundo dados do IBGE (Censo 2010), aproximadamente 23,9% da população brasileira possui algum tipo de deficiência, representando cerca de 45,6 milhões de pessoas. No contexto local, estima-se que {city} possua aproximadamente [inserir dados locais] pessoas com deficiência que necessitam de atenção especializada na área de {area_info['name'].lower()}.

LACUNA ASSISTENCIAL:
A {institution_name} identificou uma lacuna significativa na oferta de serviços especializados em {area_info['name'].lower()}, evidenciada pela demanda reprimida de [inserir dados] pessoas aguardando atendimento. Esta situação compromete o acesso oportuno aos cuidados necessários, impactando diretamente na qualidade de vida e no desenvolvimento funcional dos usuários.

FUNDAMENTAÇÃO LEGAL:
Este projeto fundamenta-se na Lei nº 13.146/2015 (Lei Brasileira de Inclusão), que assegura o direito à saúde da pessoa com deficiência, e na Portaria de Consolidação nº 5/2017 do Ministério da Saúde, que regulamenta o PRONAS/PCD. Alinha-se também à Convenção Internacional sobre os Direitos das Pessoas com Deficiência, promulgada pelo Decreto nº 6.949/2009.

RELEVÂNCIA TÉCNICA:
As ações propostas seguem evidências científicas consolidadas e boas práticas internacionais em {area_info['name'].lower()}. A implementação deste projeto permitirá:
- Ampliação da capacidade instalada em [inserir percentual]
- Redução do tempo de espera para atendimento especializado
- Melhoria na qualidade dos serviços oferecidos
- Fortalecimento da Rede de Cuidados à Pessoa com Deficiência local

IMPACTO ESPERADO:
O projeto beneficiará diretamente [inserir número] pessoas com deficiência anualmente, com impacto indireto em suas famílias e cuidadores. Os resultados esperados incluem melhoria funcional mensurável em 80% dos casos, aumento da autonomia em 70% dos beneficiários e satisfação superior a 90% entre usuários e familiares.

SUSTENTABILIDADE:
A sustentabilidade do projeto será garantida através de parcerias com o SUS local, capacitação contínua da equipe, integração com a rede de atenção à saúde e busca de fontes alternativas de financiamento após o período de execução do PRONAS/PCD.

ALINHAMENTO COM PRONAS/PCD:
Este projeto alinha-se perfeitamente com os objetivos do PRONAS/PCD de fortalecer as ações de atenção à saúde da pessoa com deficiência, complementando as ações do SUS e promovendo a equidade no acesso aos serviços de saúde especializados.
""".strip()
        
        return justification

    async def _generate_project_team(self, area_info: Dict, budget_total: float) -> List[ProjectTeamCreate]:
        """Gera equipe adequada para o projeto"""
        team_members = []
        
        # Coordenador (obrigatório)
        team_members.append(ProjectTeamCreate(
            role="Coordenador Geral",
            name="[A ser definido]",
            qualification="Profissional de nível superior com especialização na área, experiência mínima de 5 anos em gestão de projetos e conhecimento das diretrizes do PRONAS/PCD",
            weekly_hours=20,
            monthly_salary=Decimal("10000.00")
        ))
        
        # Equipe específica por área prioritária
        area_teams = {
            "QSS": [
                {"role": "Arquiteto Especialista", "qualification": "Arquiteto com especialização em acessibilidade", "hours": 20, "salary": 8000},
                {"role": "Engenheiro", "qualification": "Engenheiro civil com experiência em adaptações", "hours": 20, "salary": 7000}
            ],
            "RPD": [
                {"role": "Fisioterapeuta", "qualification": "Fisioterapeuta com especialização em neurologia", "hours": 40, "salary": 6000},
                {"role": "Terapeuta Ocupacional", "qualification": "TO com experiência em reabilitação", "hours": 40, "salary": 5500},
                {"role": "Fonoaudiólogo", "qualification": "Fonoaudiólogo especialista", "hours": 30, "salary": 5000}
            ],
            "DDP": [
                {"role": "Neuropsicólogo", "qualification": "Psicólogo com especialização em neuropsicologia", "hours": 30, "salary": 7000},
                {"role": "Médico Especialista", "qualification": "Médico com residência em área específica", "hours": 20, "salary": 12000}
            ],
            "EPD": [
                {"role": "Pediatra", "qualification": "Médico pediatra especializado", "hours": 20, "salary": 10000},
                {"role": "Psicólogo Infantil", "qualification": "Psicólogo especializado em desenvolvimento infantil", "hours": 40, "salary": 6000}
            ],
            "ITR": [
                {"role": "Pedagogo", "qualification": "Pedagogo com experiência em educação especial", "hours": 40, "salary": 5000},
                {"role": "Terapeuta Ocupacional", "qualification": "TO especializado em reabilitação profissional", "hours": 30, "salary": 5500}
            ],
            "APE": [
                {"role": "Educador Físico", "qualification": "Professor de Educação Física especializado em esporte adaptado", "hours": 40, "salary": 4500},
                {"role": "Fisioterapeuta", "qualification": "Fisioterapeuta esportivo", "hours": 30, "salary": 6000}
            ],
            "TAA": [
                {"role": "Veterinário", "qualification": "Médico veterinário especializado em TAA", "hours": 20, "salary": 6000},
                {"role": "Psicólogo", "qualification": "Psicólogo com certificação em TAA", "hours": 30, "salary": 5500}
            ],
            "APC": [
                {"role": "Arteterapeuta", "qualification": "Profissional certificado em arteterapia", "hours": 30, "salary": 5000},
                {"role": "Musicoterapeuta", "qualification": "Musicoterapeuta registrado", "hours": 20, "salary": 4500}
            ]
        }
        
        # Adicionar equipe específica da área
        area_code = None
        for code, info in self.priority_areas.items():
            if info == area_info:
                area_code = code
                break
        
        if area_code and area_code in area_teams:
            for member in area_teams[area_code]:
                team_members.append(ProjectTeamCreate(
                    role=member["role"],
                    name="[A ser definido]",
                    qualification=member["qualification"],
                    weekly_hours=member["hours"],
                    monthly_salary=Decimal(str(member["salary"]))
                ))
        
        # Assistente administrativo (sempre incluído)
        team_members.append(ProjectTeamCreate(
            role="Assistente Administrativo",
            name="[A ser definido]",
            qualification="Ensino médio completo, experiência em atividades administrativas e conhecimento básico de informática",
            weekly_hours=40,
            monthly_salary=Decimal("2500.00")
        ))
        
        return team_members

    async def _generate_project_budget(self, area_info: Dict, budget_total: float) -> List[ProjectBudgetCreate]:
        """Gera orçamento detalhado baseado na área prioritária"""
        budget_items = []
        
        # Obter distribuição típica para a área
        area_code = None
        for code, info in self.priority_areas.items():
            if info == area_info:
                area_code = code
                break
        
        distribution = area_info.get('typical_budget_distribution', {
            "pessoal": 0.45,
            "material_consumo": 0.20,
            "material_permanente": 0.15,
            "despesas_administrativas": 0.10,
            "reformas": 0.05,
            "auditoria": 0.05
        })
        
        # Garantir que auditoria está incluída (obrigatória)
        if 'auditoria' not in distribution:
            distribution['auditoria'] = 0.05
            # Reajustar outras categorias
            total = sum(distribution.values())
            for key in distribution:
                if key != 'auditoria':
                    distribution[key] = distribution[key] * 0.95 / (total - 0.05)
        
        # Gerar itens para cada categoria
        for category, percentage in distribution.items():
            category_total = budget_total * percentage
            
            if category == "pessoal":
                # Dividir entre coordenação e equipe técnica
                budget_items.extend([
                    ProjectBudgetCreate(
                        category=BudgetCategoryEnum.PESSOAL,
                        subcategory="Coordenação",
                        description="Coordenador Geral - 20h/semanais",
                        unit="mês",
                        quantity=Decimal("24"),
                        unit_value=Decimal("10000.00"),
                        total_value=Decimal("240000.00")
                    )
                ])
                
                remaining = category_total - 240000
                if remaining > 0:
                    budget_items.append(ProjectBudgetCreate(
                        category=BudgetCategoryEnum.PESSOAL,
                        subcategory="Equipe Técnica",
                        description="Profissionais especializados",
                        unit="mês",
                        quantity=Decimal("24"),
                        unit_value=Decimal(str(remaining / 24)),
                        total_value=Decimal(str(remaining))
                    ))
            
            elif category == "material_consumo":
                budget_items.extend([
                    ProjectBudgetCreate(
                        category=BudgetCategoryEnum.MATERIAL_CONSUMO,
                        description="Material terapêutico e de consumo",
                        unit="mês",
                        quantity=Decimal("24"),
                        unit_value=Decimal(str(category_total / 24)),
                        total_value=Decimal(str(category_total))
                    )
                ])
            
            elif category == "material_permanente":
                budget_items.append(ProjectBudgetCreate(
                    category=BudgetCategoryEnum.MATERIAL_PERMANENTE,
                    description="Equipamentos e materiais permanentes",
                    unit="conjunto",
                    quantity=Decimal("1"),
                    unit_value=Decimal(str(category_total)),
                    total_value=Decimal(str(category_total))
                ))
            
            elif category == "despesas_administrativas":
                budget_items.append(ProjectBudgetCreate(
                    category=BudgetCategoryEnum.DESPESAS_ADMINISTRATIVAS,
                    description="Despesas proporcionais (energia, água, telefone, etc.)",
                    unit="mês",
                    quantity=Decimal("24"),
                    unit_value=Decimal(str(category_total / 24)),
                    total_value=Decimal(str(category_total))
                ))
            
            elif category == "reformas":
                if percentage > 0:
                    budget_items.append(ProjectBudgetCreate(
                        category=BudgetCategoryEnum.REFORMAS,
                        description="Adaptações para ampliação de atendimento",
                        unit="conjunto",
                        quantity=Decimal("1"),
                        unit_value=Decimal(str(category_total)),
                        total_value=Decimal(str(category_total))
                    ))
            
            elif category == "auditoria":
                budget_items.append(ProjectBudgetCreate(
                    category=BudgetCategoryEnum.AUDITORIA,
                    description="Auditoria independente (obrigatória)",
                    unit="projeto",
                    quantity=Decimal("1"),
                    unit_value=Decimal(str(category_total)),
                    total_value=Decimal(str(category_total))
                ))
        
        return budget_items

    async def _generate_project_goals(self, area_info: Dict, requirements: Dict) -> List[ProjectGoalCreate]:
        """Gera metas e indicadores específicos por área"""
        goals = []
        
        # Metas comuns a todos os projetos
        goals.extend([
            ProjectGoalCreate(
                indicator_name="Taxa de satisfação dos usuários",
                target_value=Decimal("90.0"),
                measurement_method="Pesquisa de satisfação aplicada trimestralmente com escala Likert de 5 pontos",
                frequency=MonitoringFrequencyEnum.TRIMESTRAL
            ),
            ProjectGoalCreate(
                indicator_name="Número de beneficiários atendidos",
                target_value=Decimal("500"),
                measurement_method="Contagem de beneficiários únicos atendidos no período, registrados em sistema",
                frequency=MonitoringFrequencyEnum.MENSAL
            )
        ])
        
        # Metas específicas por área prioritária  
        area_specific_goals = {
            "QSS": [
                ProjectGoalCreate(
                    indicator_name="Percentual de adequação às normas de acessibilidade",
                    target_value=Decimal("100.0"),
                    measurement_method="Avaliação técnica baseada na NBR 9050 e lista de verificação padronizada",
                    frequency=MonitoringFrequencyEnum.SEMESTRAL
                )
            ],
            "RPD": [
                ProjectGoalCreate(
                    indicator_name="Taxa de melhoria funcional",
                    target_value=Decimal("80.0"),
                    measurement_method="Aplicação de escalas funcionais padronizadas antes e após intervenção",
                    frequency=MonitoringFrequencyEnum.TRIMESTRAL
                )
            ],
            "DDP": [
                ProjectGoalCreate(
                    indicator_name="Tempo médio para diagnóstico",
                    target_value=Decimal("30.0"),
                    measurement_method="Cálculo do tempo em dias entre primeira consulta e conclusão diagnóstica",
                    frequency=MonitoringFrequencyEnum.MENSAL
                )
            ]
        }
        
        # Adicionar metas específicas se existirem
        area_code = None
        for code, info in self.priority_areas.items():
            if info == area_info:
                area_code = code
                break
        
        if area_code in area_specific_goals:
            goals.extend(area_specific_goals[area_code])
        
        return goals

    async def _generate_project_timeline(self, area_info: Dict, timeline_months: int) -> List[ProjectTimelineCreate]:
        """Gera cronograma baseado na área e duração"""
        timeline = []
        
        # Fases padrão para todos os projetos
        phases = [
            {
                "name": "Planejamento e Preparação",
                "start": 1,
                "duration": max(2, timeline_months // 8),
                "deliverables": [
                    "Plano detalhado de execução",
                    "Contratação da equipe",
                    "Aquisição inicial de materiais",
                    "Estabelecimento de parcerias"
                ]
            },
            {
                "name": "Implementação - Fase I",
                "duration": timeline_months // 3,
                "deliverables": [
                    "Início dos atendimentos",
                    "Capacitação da equipe",
                    "Implementação de protocolos",
                    "Relatório de implantação"
                ]
            },
            {
                "name": "Desenvolvimento - Fase II", 
                "duration": timeline_months // 3,
                "deliverables": [
                    "Expansão dos atendimentos",
                    "Avaliação de resultados parciais",
                    "Ajustes metodológicos",
                    "Relatório de progresso"
                ]
            },
            {
                "name": "Consolidação - Fase III",
                "duration": timeline_months // 4,
                "deliverables": [
                    "Atingimento das metas",
                    "Avaliação de impacto",
                    "Preparação para sustentabilidade",
                    "Relatório final"
                ]
            }
        ]
        
        current_month = 1
        for phase in phases:
            if "start" not in phase:
                phase["start"] = current_month
            
            end_month = phase["start"] + phase["duration"] - 1
            
            timeline.append(ProjectTimelineCreate(
                phase_name=phase["name"],
                start_month=phase["start"],
                end_month=min(end_month, timeline_months),
                deliverables=phase["deliverables"]
            ))
            
            current_month = end_month + 1
            if current_month > timeline_months:
                break
        
        return timeline

    async def _validate_project_compliance(self, project: ProjectCreate) -> Dict[str, Any]:
        """Valida conformidade com as regras do PRONAS/PCD"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "compliance_checks": {}
        }
        
        rules = self.compliance_rules
        
        # Validar justificativa mínima
        if len(project.justification) < rules["validation_rules"]["min_justification_chars"]:
            validation_results["errors"].append(
                f"Justificativa deve ter pelo menos {rules['validation_rules']['min_justification_chars']} caracteres"
            )
        
        # Validar objetivos específicos mínimos
        if len(project.specific_objectives) < rules["validation_rules"]["min_specific_objectives"]:
            validation_results["errors"].append(
                f"Mínimo de {rules['validation_rules']['min_specific_objectives']} objetivos específicos"
            )
        
        # Validar cronograma
        if project.timeline_months < rules["validation_rules"]["min_timeline_months"]:
            validation_results["errors"].append(
                f"Cronograma deve ter pelo menos {rules['validation_rules']['min_timeline_months']} meses"
            )
        
        if project.timeline_months > rules["validation_rules"]["max_timeline_months"]:
            validation_results["errors"].append(
                f"Cronograma não pode exceder {rules['validation_rules']['max_timeline_months']} meses"
            )
        
        # Validar orçamento
        if project.budget_items:
            total_budget = sum(item.total_value for item in project.budget_items)
            if abs(total_budget - project.budget_total) > 0.01:
                validation_results["errors"].append("Soma dos itens não confere com total do orçamento")
            
            # Verificar auditoria obrigatória
            has_audit = any(item.category == BudgetCategoryEnum.AUDITORIA for item in project.budget_items)
            if not has_audit:
                validation_results["errors"].append("Auditoria independente é obrigatória")
        
        # Validar equipe
        if project.team_members:
            coordinator_roles = [member for member in project.team_members 
                               if "coordenador" in member.role.lower()]
            if not coordinator_roles:
                validation_results["errors"].append("Projeto deve ter um coordenador")
        
        validation_results["is_valid"] = len(validation_results["errors"]) == 0
        
        return validation_results

    async def _calculate_compliance_score(self, project: ProjectCreate, validation_results: Dict) -> float:
        """Calcula score de conformidade (0-1)"""
        total_checks = 10
        passed_checks = 0
        
        # Verificações de conformidade
        if len(project.justification) >= 500:
            passed_checks += 1
        if len(project.specific_objectives) >= 3:
            passed_checks += 1
        if 6 <= project.timeline_months <= 48:
            passed_checks += 1
        if project.budget_items and any(item.category == BudgetCategoryEnum.AUDITORIA for item in project.budget_items):
            passed_checks += 1
        if project.team_members and any("coordenador" in member.role.lower() for member in project.team_members):
            passed_checks += 1
        if project.goals and len(project.goals) >= 2:
            passed_checks += 1
        if project.timeline and len(project.timeline) >= 3:
            passed_checks += 1
        if validation_results.get("is_valid", False):
            passed_checks += 1
        if project.budget_total > 0:
            passed_checks += 1
        if project.general_objective and len(project.general_objective) >= 50:
            passed_checks += 1
        
        return passed_checks / total_checks

    async def _calculate_confidence_score(self, project: ProjectCreate, area_info: Dict) -> float:
        """Calcula score de confiança na geração (0-1)"""
        confidence = 0.8  # Base
        
        # Ajustar baseado na completude
        if project.team_members and len(project.team_members) >= 3:
            confidence += 0.05
        if project.budget_items and len(project.budget_items) >= 5:
            confidence += 0.05
        if project.goals and len(project.goals) >= 2:
            confidence += 0.05
        if project.timeline and len(project.timeline) >= 4:
            confidence += 0.05
        
        return min(confidence, 1.0)

    async def _generate_recommendations(
        self, project: ProjectCreate, validation_results: Dict, area_info: Dict
    ) -> List[str]:
        """Gera recomendações para melhorar o projeto"""
        recommendations = []
        
        # Recomendações baseadas na validação
        if validation_results.get("errors"):
            recommendations.extend([
                f"Corrija os seguintes erros: {', '.join(validation_results['errors'])}"
            ])
        
        # Recomendações específicas
        if len(project.justification) < 1000:
            recommendations.append("Considere expandir a justificativa com mais dados epidemiológicos locais")
        
        if not project.target_audience:
            recommendations.append("Detalhe melhor o público-alvo e critérios de inclusão/exclusão")
        
        if project.budget_items:
            captacao_items = [item for item in project.budget_items 
                            if item.category == BudgetCategoryEnum.CAPTACAO_RECURSOS]
            if not captacao_items:
                recommendations.append("Considere incluir recursos para captação (até 5% do total)")
        
        # Recomendações por área
        area_recommendations = {
            "QSS": ["Inclua cronograma de adequações baseado na NBR 9050"],
            "RPD": ["Considere parcerias com universidades para estágios"],
            "DDP": ["Estabeleça protocolos de diagnóstico padronizados"]
        }
        
        area_code = None
        for code, info in self.priority_areas.items():
            if info == area_info:
                area_code = code
                break
        
        if area_code in area_recommendations:
            recommendations.extend(area_recommendations[area_code])
        
        return recommendations

    async def _find_similar_projects(self, project: ProjectCreate) -> List[Dict[str, Any]]:
        """Busca projetos similares para referência"""
        # Simulação de busca em base de dados
        similar_projects = [
            {
                "id": "proj_001",
                "title": "Projeto similar na mesma área",
                "institution": "Instituição de referência",
                "similarity_score": 0.85,
                "budget_total": float(project.budget_total) * 1.1,
                "success_rate": 0.90
            }
        ]
        
        return similar_projects

    def _get_priority_area_id(self, code: str) -> int:
        """Retorna ID da área prioritária (simulado)"""
        area_ids = {
            "QSS": 1, "RPD": 2, "DDP": 3, "EPD": 4,
            "ITR": 5, "APE": 6, "TAA": 7, "APC": 8
        }
        return area_ids.get(code, 1)

    async def _generate_target_audience(self, area_info: Dict, requirements: Dict) -> str:
        """Gera descrição detalhada do público-alvo"""
        return f"""
PÚBLICO-ALVO PRIORITÁRIO:
Pessoas com deficiência física, intelectual, auditiva, visual, múltipla, com ostomia e/ou transtorno do espectro autista, na faixa etária específica para {area_info['name'].lower()}.

CRITÉRIOS DE INCLUSÃO:
- Residir na área de abrangência do projeto
- Possuir diagnóstico confirmado de deficiência
- Apresentar demanda específica para a área de atuação
- Aceitar participar do projeto e assinar termo de consentimento
- Ter acompanhante/cuidador quando necessário

CRITÉRIOS DE EXCLUSÃO:
- Condições clínicas que impeçam a participação nas atividades
- Não residir na área de abrangência
- Não aceitar os termos do projeto

BENEFICIÁRIOS INDIRETOS:
Familiares, cuidadores e comunidade em geral, estimando-se 3 pessoas indiretamente beneficiadas para cada beneficiário direto.
""".strip()

    async def _generate_methodology(self, area_info: Dict, requirements: Dict) -> str:
        """Gera metodologia específica por área"""
        return f"""
ABORDAGEM METODOLÓGICA:
Este projeto utilizará abordagem multidisciplinar e centrada na pessoa, seguindo as melhores práticas em {area_info['name'].lower()} e evidências científicas atuais.

FASES DE IMPLEMENTAÇÃO:
1. ACOLHIMENTO E AVALIAÇÃO INICIAL
   - Recepção e acolhimento humanizado
   - Avaliação multidisciplinar padronizada
   - Estabelecimento de plano terapêutico individualizado

2. INTERVENÇÃO ESPECIALIZADA
   - Atendimentos individuais e/ou grupais
   - Utilização de protocolos baseados em evidências
   - Monitoramento contínuo da evolução

3. ACOMPANHAMENTO E AVALIAÇÃO
   - Reavaliações periódicas
   - Ajustes no plano terapêutico
   - Medição de resultados e impactos

INSTRUMENTOS E FERRAMENTAS:
- Protocolos de avaliação padronizados
- Escalas de medição validadas
- Sistema de registro e monitoramento
- Indicadores de processo e resultado

ARTICULAÇÃO COM A REDE:
- Integração com SUS local
- Parcerias com outras instituições
- Sistema de referência e contrarreferência
- Trabalho intersetorial quando necessário
""".strip()

    async def _generate_expected_results(self, area_info: Dict, requirements: Dict) -> str:
        """Gera resultados esperados específicos"""
        return f"""
RESULTADOS ESPERADOS:

QUANTITATIVOS:
- [X] beneficiários diretos atendidos anualmente
- [Y] atendimentos/sessões realizados
- [Z]% de taxa de satisfação dos usuários
- Redução de [W]% no tempo de espera para atendimento

QUALITATIVOS:
- Melhoria mensurável na funcionalidade dos beneficiários
- Aumento da autonomia e qualidade de vida
- Satisfação de familiares e cuidadores
- Capacitação de profissionais especializados

IMPACTOS DE MÉDIO E LONGO PRAZO:
- Fortalecimento da rede de atenção à pessoa com deficiência
- Modelo replicável para outras instituições
- Contribuição para políticas públicas locais
- Melhoria dos indicadores epidemiológicos locais

PRODUTOS E ENTREGAS:
- Protocolos padronizados de atendimento
- Material didático e instrucional
- Relatórios técnicos e científicos
- Sistema de monitoramento e avaliação

SUSTENTABILIDADE:
- Equipe capacitada para continuidade
- Parcerias estabelecidas com rede local
- Protocolos implantados na rotina institucional
- Busca de novos financiamentos
""".strip()