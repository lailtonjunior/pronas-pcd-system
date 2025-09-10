"""
Motor de IA especializada para geração de projetos PRONAS/PCD
Baseado nas 8 áreas prioritárias da Portaria de Consolidação nº 5/2017 - Art. 10
"""

import asyncio
import json
import logging
import random
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
import os

# Configurar logging
logger = logging.getLogger(__name__)

class PronasAIEngine:
    """
    Motor de Inteligência Artificial especializada em PRONAS/PCD
    
    Implementa conhecimento completo sobre:
    - 8 áreas prioritárias (Art. 10)
    - Regras de orçamento (Portaria 448/2002)
    - Equipes técnicas adequadas
    - Metodologias baseadas em evidências
    - Validação automática de conformidade
    """
    
    def __init__(self):
        """Inicializar motor de IA com conhecimento especializado"""
        self.confidence_threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.7'))
        self.model_name = os.getenv('AI_MODEL_NAME', 'gpt-4-turbo')
        
        # Inicializar base de conhecimento das áreas prioritárias
        self._initialize_priority_areas_knowledge()
        
        # Inicializar templates de orçamento
        self._initialize_budget_templates()
        
        # Inicializar guidelines de equipe
        self._initialize_team_guidelines()
        
        # Inicializar validadores de conformidade
        self._initialize_compliance_validators()
        
        logger.info(f"PronasAIEngine inicializado com {len(self.priority_areas)} áreas prioritárias")
    
    def _initialize_priority_areas_knowledge(self):
        """
        Inicializar base de conhecimento das 8 áreas prioritárias
        Baseado no Art. 10 da Portaria de Consolidação nº 5/2017
        """
        self.priority_areas = {
            "QSS": {
                "name": "Qualificação de serviços de saúde",
                "description": "Adequação da ambiência de estabelecimentos de saúde que prestam atendimento à pessoa com deficiência",
                "typical_actions": [
                    "Adequação de acessibilidade arquitetônica",
                    "Aquisição de equipamentos especializados",
                    "Adaptação de sanitários e vestiários",
                    "Sinalização tátil e visual",
                    "Mobiliário adaptado",
                    "Sistemas de comunicação alternativa"
                ],
                "target_beneficiaries": "Pessoas com deficiência atendidas no estabelecimento",
                "typical_methodologies": [
                    "Avaliação de barreiras arquitetônicas",
                    "Projeto de adequação baseado na NBR 9050",
                    "Implementação faseada das adequações",
                    "Treinamento da equipe para atendimento acessível"
                ],
                "expected_results": [
                    "Melhoria da acessibilidade física",
                    "Aumento da satisfação dos usuários",
                    "Qualificação do atendimento",
                    "Conformidade com normas de acessibilidade"
                ],
                "typical_budget_distribution": {
                    "material_permanente": 45,  # Equipamentos e mobiliário
                    "reformas": 30,             # Obras de adequação
                    "material_consumo": 10,     # Materiais diversos
                    "pessoal": 10,             # Consultoria especializada
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador do projeto",
                    "Arquiteto especialista em acessibilidade",
                    "Engenheiro civil",
                    "Terapeuta ocupacional"
                ]
            },
            
            "RPD": {
                "name": "Reabilitação/habilitação da pessoa com deficiência",
                "description": "Ações de reabilitação e habilitação da pessoa com deficiência",
                "typical_actions": [
                    "Atendimento fisioterapêutico especializado",
                    "Terapia ocupacional",
                    "Fonoaudiologia para reabilitação",
                    "Psicologia em reabilitação",
                    "Prescrição e adaptação de tecnologia assistiva",
                    "Orientação e mobilidade para pessoas cegas",
                    "Reabilitação cognitiva"
                ],
                "target_beneficiaries": "Pessoas com deficiência física, intelectual, auditiva ou visual",
                "typical_methodologies": [
                    "Avaliação multidisciplinar",
                    "Plano terapêutico individualizado",
                    "Atendimento individual e em grupo",
                    "Reavaliações periódicas",
                    "Orientação familiar"
                ],
                "expected_results": [
                    "Melhoria da funcionalidade",
                    "Maior independência nas atividades de vida diária",
                    "Redução de limitações funcionais",
                    "Melhoria da qualidade de vida"
                ],
                "typical_budget_distribution": {
                    "pessoal": 60,              # Equipe multidisciplinar
                    "material_permanente": 20,  # Equipamentos terapêuticos
                    "material_consumo": 10,     # Materiais de terapia
                    "despesas_administrativas": 5, # Telefone, internet
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador (médico fisiatra ou neurologista)",
                    "Fisioterapeuta",
                    "Terapeuta ocupacional",
                    "Fonoaudiólogo",
                    "Psicólogo",
                    "Assistente social"
                ]
            },
            
            "DDP": {
                "name": "Diagnóstico diferencial da pessoa com deficiência",
                "description": "Diagnóstico diferencial da pessoa com deficiência",
                "typical_actions": [
                    "Avaliação médica especializada",
                    "Avaliação neuropsicológica",
                    "Testes genéticos quando indicados",
                    "Avaliação multidisciplinar",
                    "Elaboração de laudos especializados",
                    "Orientação diagnóstica para famílias"
                ],
                "target_beneficiaries": "Pessoas com suspeita de deficiência ou deficiência não diagnosticada",
                "typical_methodologies": [
                    "Protocolo de avaliação multidisciplinar",
                    "Aplicação de instrumentos padronizados",
                    "Análise de exames complementares",
                    "Discussão de casos em equipe",
                    "Elaboração de relatório diagnóstico"
                ],
                "expected_results": [
                    "Diagnóstico preciso e precoce",
                    "Encaminhamento adequado para tratamento",
                    "Orientação familiar qualificada",
                    "Redução do tempo para diagnóstico"
                ],
                "typical_budget_distribution": {
                    "pessoal": 50,              # Equipe especializada
                    "material_permanente": 25,  # Equipamentos diagnósticos
                    "material_consumo": 15,     # Testes e materiais
                    "despesas_administrativas": 5, # Administrativo
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador médico especialista",
                    "Neuropsicólogo",
                    "Psicólogo",
                    "Fonoaudiólogo",
                    "Terapeuta ocupacional"
                ]
            },
            
            "EPD": {
                "name": "Identificação e estimulação precoce das deficiências",
                "description": "Identificação e estimulação precoce de deficiências em crianças de 0 a 3 anos",
                "typical_actions": [
                    "Triagem neonatal expandida",
                    "Avaliação do desenvolvimento infantil",
                    "Estimulação precoce individualizada",
                    "Orientação às famílias",
                    "Intervenção precoce especializada",
                    "Acompanhamento longitudinal"
                ],
                "target_beneficiaries": "Crianças de 0 a 3 anos com risco ou sinais de deficiência",
                "typical_methodologies": [
                    "Protocolo de triagem e avaliação",
                    "Programa de estimulação precoce",
                    "Atendimento domiciliar quando necessário",
                    "Grupos de orientação parental",
                    "Rede de referência e contrarreferência"
                ],
                "expected_results": [
                    "Identificação precoce de deficiências",
                    "Melhoria do desenvolvimento infantil",
                    "Capacitação das famílias",
                    "Prevenção de deficiências secundárias"
                ],
                "typical_budget_distribution": {
                    "pessoal": 55,              # Equipe especializada
                    "material_permanente": 20,  # Brinquedos e equipamentos
                    "material_consumo": 15,     # Materiais de estimulação
                    "despesas_administrativas": 5, # Administrativo
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador médico pediatra/neuropediatra",
                    "Fisioterapeuta pediátrico",
                    "Terapeuta ocupacional pediátrico",
                    "Fonoaudiólogo pediátrico",
                    "Psicólogo infantil",
                    "Enfermeiro especializado"
                ]
            },
            
            "ITR": {
                "name": "Inserção e reinserção no trabalho",
                "description": "Adaptação, inserção e reinserção da pessoa com deficiência no mercado de trabalho",
                "typical_actions": [
                    "Avaliação de capacidade laboral",
                    "Treinamento de habilidades profissionais",
                    "Adaptação de postos de trabalho",
                    "Tecnologia assistiva para trabalho",
                    "Oficinas profissionalizantes",
                    "Intermediação com empregadores",
                    "Acompanhamento pós-inserção"
                ],
                "target_beneficiaries": "Pessoas com deficiência em idade produtiva",
                "typical_methodologies": [
                    "Avaliação funcional para o trabalho",
                    "Plano individualizado de inserção",
                    "Capacitação profissional adaptada",
                    "Parcerias com empresas",
                    "Seguimento longitudinal"
                ],
                "expected_results": [
                    "Inserção no mercado de trabalho",
                    "Melhoria da renda familiar",
                    "Autonomia e inclusão social",
                    "Conscientização empresarial"
                ],
                "typical_budget_distribution": {
                    "pessoal": 45,              # Equipe multidisciplinar
                    "material_permanente": 25,  # Equipamentos e tecnologia assistiva
                    "material_consumo": 15,     # Materiais de capacitação
                    "despesas_administrativas": 10, # Transporte, comunicação
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador (médico do trabalho ou terapeuta ocupacional)",
                    "Terapeuta ocupacional",
                    "Psicólogo organizacional",
                    "Assistente social",
                    "Instrutor profissionalizante"
                ]
            },
            
            "APE": {
                "name": "Apoio à saúde por meio de práticas esportivas",
                "description": "Atividades físicas e esportivas adaptadas para pessoas com deficiência",
                "typical_actions": [
                    "Avaliação funcional para esporte",
                    "Prescrição de atividade física adaptada",
                    "Treinamento esportivo especializado",
                    "Modalidades paradesportivas",
                    "Adaptação de equipamentos esportivos",
                    "Competições e eventos inclusivos"
                ],
                "target_beneficiaries": "Pessoas com deficiência de todas as idades interessadas em atividade física",
                "typical_methodologies": [
                    "Avaliação médica e funcional",
                    "Classificação funcional esportiva",
                    "Programa de condicionamento físico",
                    "Treinamento técnico especializado",
                    "Acompanhamento multidisciplinar"
                ],
                "expected_results": [
                    "Melhoria do condicionamento físico",
                    "Desenvolvimento de habilidades esportivas",
                    "Socialização e inclusão",
                    "Melhoria da autoestima e qualidade de vida"
                ],
                "typical_budget_distribution": {
                    "pessoal": 40,              # Professores e técnicos
                    "material_permanente": 35,  # Equipamentos esportivos
                    "material_consumo": 15,     # Materiais de apoio
                    "despesas_administrativas": 5, # Administrativo
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador (médico do esporte ou educador físico)",
                    "Educador físico especializado",
                    "Fisioterapeuta esportivo",
                    "Classificador funcional",
                    "Psicólogo do esporte"
                ]
            },
            
            "TAA": {
                "name": "Terapia assistida por animais",
                "description": "Terapia assistida por animais (TAA) como complemento terapêutico",
                "typical_actions": [
                    "Avaliação para indicação de TAA",
                    "Sessões de terapia com animais",
                    "Atividades assistidas por animais",
                    "Treinamento de animais terapeutas",
                    "Capacitação de condutores",
                    "Protocolos de higiene e segurança"
                ],
                "target_beneficiaries": "Pessoas com deficiência que se beneficiem da TAA",
                "typical_methodologies": [
                    "Protocolo de seleção e avaliação",
                    "Sessões individuais e grupais",
                    "Objetivos terapêuticos específicos",
                    "Registro sistemático de progressos",
                    "Cuidados veterinários especializados"
                ],
                "expected_results": [
                    "Melhoria da comunicação",
                    "Redução de ansiedade e depressão",
                    "Desenvolvimento de habilidades sociais",
                    "Melhoria da autoestima"
                ],
                "typical_budget_distribution": {
                    "pessoal": 50,              # Terapeutas e condutores
                    "material_consumo": 25,     # Cuidados com animais
                    "material_permanente": 15,  # Equipamentos especializados
                    "despesas_administrativas": 5, # Administrativo
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador (psicólogo ou terapeuta ocupacional)",
                    "Terapeuta especializado em TAA",
                    "Condutor de animais certificado",
                    "Veterinário",
                    "Auxiliar de atividades"
                ]
            },
            
            "APC": {
                "name": "Apoio à saúde por produção artística e cultural",
                "description": "Atividades artísticas e culturais como apoio à saúde da pessoa com deficiência",
                "typical_actions": [
                    "Oficinas de artes visuais adaptadas",
                    "Musicoterapia",
                    "Teatro inclusivo",
                    "Dança para pessoas com deficiência",
                    "Literatura e contação de histórias",
                    "Produção cultural inclusiva"
                ],
                "target_beneficiaries": "Pessoas com deficiência interessadas em atividades artísticas e culturais",
                "typical_methodologies": [
                    "Avaliação de interesses e habilidades",
                    "Oficinas especializadas e adaptadas",
                    "Produção e apresentação de trabalhos",
                    "Eventos culturais inclusivos",
                    "Registro e documentação das atividades"
                ],
                "expected_results": [
                    "Desenvolvimento de habilidades artísticas",
                    "Expressão criativa e emocional",
                    "Socialização e inclusão cultural",
                    "Melhoria da autoestima e qualidade de vida"
                ],
                "typical_budget_distribution": {
                    "pessoal": 45,              # Artistas e terapeutas
                    "material_consumo": 30,     # Materiais artísticos
                    "material_permanente": 15,  # Instrumentos e equipamentos
                    "despesas_administrativas": 5, # Administrativo
                    "auditoria": 3,            # Auditoria obrigatória
                    "captacao_recursos": 2     # Captação
                },
                "required_team_roles": [
                    "Coordenador (arte-terapeuta ou educador artístico)",
                    "Musicoterapeuta",
                    "Arte-terapeuta",
                    "Instrutor de dança adaptada",
                    "Produtor cultural"
                ]
            }
        }
    
    def _initialize_budget_templates(self):
        """
        Inicializar templates de orçamento baseados na Portaria 448/2002
        """
        self.expense_nature_codes = {
            "pessoal": {
                "codes": ["339036", "339037"],
                "descriptions": ["Outros Serviços de Terceiros - Pessoa Física", "Locação de Mão-de-Obra"]
            },
            "material_consumo": {
                "codes": ["339030"],
                "descriptions": ["Material de Consumo"]
            },
            "material_permanente": {
                "codes": ["449052"],
                "descriptions": ["Equipamentos e Material Permanente"]
            },
            "reformas": {
                "codes": ["449051"],
                "descriptions": ["Obras e Instalações"]
            },
            "despesas_administrativas": {
                "codes": ["339039"],
                "descriptions": ["Outros Serviços de Terceiros - Pessoa Jurídica"]
            },
            "captacao_recursos": {
                "max_percentage": 5,
                "max_absolute": 50000,
                "codes": ["339039"]
            },
            "auditoria": {
                "mandatory": True,
                "codes": ["339039"],
                "min_percentage": 2
            }
        }
    
    def _initialize_team_guidelines(self):
        """
        Inicializar diretrizes para composição de equipe por área
        """
        self.team_salary_ranges = {
            "coordenador": {"min": 8000, "max": 15000, "hours_week": 20},
            "medico": {"min": 10000, "max": 20000, "hours_week": 20},
            "fisioterapeuta": {"min": 4000, "max": 8000, "hours_week": 30},
            "terapeuta_ocupacional": {"min": 4000, "max": 8000, "hours_week": 30},
            "fonoaudiologo": {"min": 4000, "max": 8000, "hours_week": 30},
            "psicologo": {"min": 4000, "max": 8000, "hours_week": 30},
            "assistente_social": {"min": 3500, "max": 7000, "hours_week": 30},
            "enfermeiro": {"min": 4000, "max": 8000, "hours_week": 30},
            "educador_fisico": {"min": 3000, "max": 6000, "hours_week": 30},
            "arte_terapeuta": {"min": 3500, "max": 7000, "hours_week": 20},
            "musicoterapeuta": {"min": 3500, "max": 7000, "hours_week": 20},
            "instrutor": {"min": 2500, "max": 5000, "hours_week": 30},
            "auxiliar": {"min": 1800, "max": 3500, "hours_week": 40}
        }
    
    def _initialize_compliance_validators(self):
        """
        Inicializar validadores de conformidade com regras PRONAS/PCD
        """
        self.compliance_rules = {
            "min_justification_length": 500,
            "min_specific_objectives": 3,
            "min_timeline_months": 6,
            "max_timeline_months": 48,
            "min_captacao_percentage": 60,
            "max_captacao_percentage": 120,
            "max_captacao_absolute": 50000,
            "max_captacao_percentage_of_total": 5,
            "mandatory_audit": True,
            "max_projects_per_institution": 3,
            "credentialing_months": [6, 7]
        }
    
    async def generate_project_from_guidelines(
        self,
        institution_data: Dict[str, Any],
        project_requirements: Dict[str, Any],
        priority_area_code: str
    ) -> Dict[str, Any]:
        """
        Gerar projeto completo baseado nas diretrizes do PRONAS/PCD
        
        Args:
            institution_data: Dados da instituição
            project_requirements: Requisitos do projeto
            priority_area_code: Código da área prioritária (QSS, RPD, etc.)
        
        Returns:
            Resposta completa da IA com projeto gerado
        """
        try:
            start_time = datetime.now()
            
            # Validar área prioritária
            if priority_area_code not in self.priority_areas:
                raise ValueError(f"Código de área prioritária inválido: {priority_area_code}")
            
            area_info = self.priority_areas[priority_area_code]
            
            logger.info(f"Iniciando geração de projeto para área {priority_area_code}")
            
            # 1. Gerar estrutura básica do projeto
            project_structure = await self._generate_project_structure(
                area_info, institution_data, project_requirements
            )
            
            # 2. Gerar equipe técnica especializada
            team_members = await self._generate_specialized_team(
                area_info, project_requirements['budget_total']
            )
            
            # 3. Gerar orçamento detalhado
            budget_items = await self._generate_detailed_budget(
                area_info, project_requirements['budget_total'], team_members
            )
            
            # 4. Gerar cronograma
            timeline = await self._generate_project_timeline(
                area_info, project_requirements['timeline_months']
            )
            
            # 5. Gerar metas e indicadores
            goals = await self._generate_project_goals(
                area_info, project_requirements.get('target_beneficiaries', 200)
            )
            
            # 6. Montar projeto completo
            complete_project = {
                **project_structure,
                "team_members": team_members,
                "budget_items": budget_items,
                "timeline": timeline,
                "goals": goals
            }
            
            # 7. Validar conformidade
            validation_results = await self._validate_project_compliance(complete_project)
            
            # 8. Calcular scores
            compliance_score = await self._calculate_compliance_score(complete_project, validation_results)
            confidence_score = await self._calculate_confidence_score(complete_project, area_info)
            
            # 9. Gerar recomendações
            recommendations = await self._generate_recommendations(
                complete_project, validation_results, area_info
            )
            
            # 10. Buscar projetos similares (simulado)
            similar_projects = await self._find_similar_projects(priority_area_code)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Projeto gerado com sucesso em {generation_time:.2f}s")
            
            return {
                "project": complete_project,
                "confidence_score": confidence_score,
                "compliance_score": compliance_score,
                "recommendations": recommendations,
                "validation_results": validation_results,
                "similar_projects": similar_projects,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do projeto: {str(e)}")
            raise e
    
    async def _generate_project_structure(
        self,
        area_info: Dict[str, Any],
        institution_data: Dict[str, Any],
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gerar estrutura básica do projeto"""
        
        # Gerar título personalizado
        title = await self._generate_project_title(area_info, institution_data)
        
        # Gerar objetivo geral
        general_objective = await self._generate_general_objective(area_info, institution_data)
        
        # Gerar objetivos específicos (mínimo 3)
        specific_objectives = await self._generate_specific_objectives(area_info)
        
        # Gerar justificativa detalhada
        justification = await self._generate_justification(
            area_info, institution_data, project_requirements
        )
        
        # Gerar metodologia
        methodology = await self._generate_methodology(area_info)
        
        # Gerar resultados esperados
        expected_results = await self._generate_expected_results(area_info)
        
        # Gerar público-alvo
        target_audience = await self._generate_target_audience(area_info)
        
        # Gerar plano de sustentabilidade
        sustainability_plan = await self._generate_sustainability_plan(area_info, institution_data)
        
        return {
            "title": title,
            "description": f"Projeto de {area_info['name']} desenvolvido para {institution_data['name']}",
            "field_of_action": "medico_assistencial",  # Padrão para PRONAS/PCD
            "general_objective": general_objective,
            "specific_objectives": specific_objectives,
            "justification": justification,
            "target_audience": target_audience,
            "methodology": methodology,
            "expected_results": expected_results,
            "sustainability_plan": sustainability_plan,
            "budget_total": project_requirements['budget_total'],
            "timeline_months": project_requirements['timeline_months']
        }
    
    async def _generate_project_title(
        self, area_info: Dict[str, Any], institution_data: Dict[str, Any]
    ) -> str:
        """Gerar título personalizado do projeto"""
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        title_templates = {
            "QSS": [
                f"Qualificação e Adequação de Serviços de Saúde para Pessoas com Deficiência - {institution_data['name']}",
                f"Projeto de Acessibilidade e Qualificação de Serviços - {institution_data['city']}/{institution_data['state']}",
                f"Adequação Arquitetônica e Tecnológica para Atendimento Inclusivo"
            ],
            "RPD": [
                f"Centro de Reabilitação e Habilitação Integral da Pessoa com Deficiência",
                f"Programa de Reabilitação Multidisciplinar - {institution_data['name']}",
                f"Serviços Especializados em Reabilitação da Pessoa com Deficiência"
            ],
            "DDP": [
                f"Centro de Diagnóstico Diferencial e Avaliação Especializada",
                f"Programa de Diagnóstico Precoce e Diferencial - {institution_data['city']}",
                f"Serviço de Avaliação Diagnóstica Multidisciplinar"
            ],
            "EPD": [
                f"Programa de Estimulação Precoce e Desenvolvimento Infantil",
                f"Centro de Intervenção Precoce - {institution_data['name']}",
                f"Identificação e Estimulação Precoce de Deficiências - 0 a 3 anos"
            ],
            "ITR": [
                f"Programa de Inserção Profissional da Pessoa com Deficiência",
                f"Centro de Habilitação e Reabilitação Profissional",
                f"Inclusão no Trabalho: Capacitação e Inserção Profissional"
            ],
            "APE": [
                f"Programa de Atividades Físicas e Esportivas Adaptadas",
                f"Centro de Esportes Paralímpicos - {institution_data['city']}",
                f"Saúde através do Esporte Adaptado"
            ],
            "TAA": [
                f"Programa de Terapia Assistida por Animais",
                f"Centro de TAA - Terapia e Atividades com Animais",
                f"Projeto Cão-Guia e Terapia Assistida"
            ],
            "APC": [
                f"Programa de Arte, Cultura e Saúde da Pessoa com Deficiência",
                f"Centro Cultural Inclusivo - {institution_data['name']}",
                f"Expressão Artística e Cultural como Terapia"
            ]
        }
        
        templates = title_templates.get(area_code, [f"Projeto {area_info['name']}"])
        return random.choice(templates)
    
    async def _generate_general_objective(
        self, area_info: Dict[str, Any], institution_data: Dict[str, Any]
    ) -> str:
        """Gerar objetivo geral baseado na área prioritária"""
        
        objectives = {
            "QSS": f"Qualificar os serviços de saúde da {institution_data['name']} através da adequação da ambiência e acessibilidade, proporcionando atendimento inclusivo e de qualidade às pessoas com deficiência da região de {institution_data['city']}/{institution_data['state']}, em conformidade com as normas técnicas vigentes e diretrizes do SUS.",
            
            "RPD": f"Desenvolver ações especializadas de reabilitação e habilitação para pessoas com deficiência física, intelectual, auditiva e visual, promovendo a máxima funcionalidade, independência e qualidade de vida dos usuários atendidos pela {institution_data['name']}, através de abordagem multidisciplinar e baseada em evidências científicas.",
            
            "DDP": f"Estabelecer serviço especializado de diagnóstico diferencial para pessoas com deficiência, oferecendo avaliação multidisciplinar abrangente e precisa que permita o diagnóstico precoce, a orientação adequada às famílias e o encaminhamento apropriado para serviços de habilitação e reabilitação na região de {institution_data['city']}/{institution_data['state']}.",
            
            "EPD": f"Implementar programa de identificação e estimulação precoce para crianças de 0 a 3 anos com risco ou sinais de deficiência, promovendo o desenvolvimento integral através de intervenção especializada, orientação familiar e articulação com a rede de cuidados, visando prevenir ou minimizar limitações funcionais futuras.",
            
            "ITR": f"Promover a inserção, reinserção e adaptação de pessoas com deficiência no mercado de trabalho, através de avaliação funcional, capacitação profissional, adaptação de postos de trabalho e tecnologia assistiva, contribuindo para a autonomia econômica e inclusão social dos usuários da {institution_data['name']}.",
            
            "APE": f"Desenvolver programa de atividades físicas e esportivas adaptadas para pessoas com deficiência, promovendo saúde, bem-estar, condicionamento físico e habilidades esportivas, através de modalidades paradesportivas e atividades recreativas inclusivas, contribuindo para a melhoria da qualidade de vida e inclusão social.",
            
            "TAA": f"Implementar programa de Terapia Assistida por Animais como recurso terapêutico complementar para pessoas com deficiência, promovendo benefícios físicos, emocionais, cognitivos e sociais através da interação estruturada e supervisionada com animais devidamente treinados e acompanhados por equipe multidisciplinar especializada.",
            
            "APC": f"Desenvolver atividades artísticas e culturais adaptadas como estratégia de apoio à saúde da pessoa com deficiência, promovendo expressão criativa, desenvolvimento de habilidades, socialização e melhoria da autoestima através de oficinas de arte, música, teatro, dança e produção cultural inclusiva."
        }
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        return objectives.get(area_code, f"Desenvolver ações de {area_info['name']} para pessoas com deficiência.")
    
    async def _generate_specific_objectives(self, area_info: Dict[str, Any]) -> List[str]:
        """Gerar objetivos específicos (mínimo 3)"""
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        objectives_bank = {
            "QSS": [
                "Adequar a infraestrutura física do estabelecimento de saúde conforme normas de acessibilidade NBR 9050",
                "Adquirir equipamentos e tecnologias assistivas para qualificar o atendimento à pessoa com deficiência",
                "Implementar sistema de sinalização visual e tátil adequado para orientação de pessoas com deficiência sensorial",
                "Capacitar a equipe multidisciplinar para atendimento inclusivo e humanizado",
                "Desenvolver protocolos de atendimento específicos para cada tipo de deficiência",
                "Criar ambiente acolhedor e adaptado para familiares e acompanhantes"
            ],
            "RPD": [
                "Realizar avaliação funcional multidisciplinar para elaboração de planos terapêuticos individualizados",
                "Desenvolver programa de fisioterapia especializada com técnicas avançadas de reabilitação",
                "Implementar serviço de terapia ocupacional para desenvolvimento de habilidades de vida diária",
                "Oferecer atendimento fonoaudiológico para reabilitação da comunicação e deglutição",
                "Prescrever e adaptar tecnologias assistivas conforme necessidades individuais",
                "Promover orientação familiar para continuidade do tratamento no domicílio",
                "Estabelecer programa de reintegração social e comunitária"
            ],
            "DDP": [
                "Realizar avaliação médica especializada com protocolos diagnósticos padronizados",
                "Implementar avaliação neuropsicológica e cognitiva abrangente",
                "Desenvolver protocolo de avaliação multidisciplinar para diagnóstico diferencial",
                "Oferecer orientação genética quando indicada e solicitação de exames complementares",
                "Elaborar laudos diagnósticos detalhados e relatórios técnicos especializados",
                "Promover discussão de casos complexos em equipe multidisciplinar",
                "Orientar famílias sobre diagnóstico, prognóstico e encaminhamentos necessários"
            ],
            "EPD": [
                "Implementar protocolo de triagem e identificação precoce de sinais de risco para deficiência",
                "Desenvolver programa de estimulação precoce individualizada para crianças de 0 a 3 anos",
                "Oferecer atendimento multidisciplinar especializado em desenvolvimento infantil",
                "Capacitar famílias e cuidadores em técnicas de estimulação no domicílio",
                "Estabelecer rede de referência e contrarreferência com serviços de saúde materno-infantil",
                "Realizar acompanhamento longitudinal do desenvolvimento das crianças atendidas",
                "Promover ações de prevenção de deficiências secundárias e complicações"
            ],
            "ITR": [
                "Realizar avaliação funcional para capacidade laboral e potencial profissional",
                "Desenvolver programa de capacitação profissional adaptado às habilidades individuais",
                "Implementar serviço de adaptação de postos de trabalho e prescrição de tecnologia assistiva",
                "Estabelecer parcerias com empresas para colocação profissional inclusiva",
                "Oferecer acompanhamento psicológico e social durante processo de inserção",
                "Promover conscientização empresarial sobre inclusão da pessoa com deficiência",
                "Realizar seguimento pós-inserção para garantir adaptação no trabalho"
            ],
            "APE": [
                "Realizar avaliação funcional e médica para prescrição segura de atividade física",
                "Desenvolver programa de condicionamento físico adaptado às necessidades individuais",
                "Implementar modalidades paradesportivas com treinamento técnico especializado",
                "Oferecer classificação funcional esportiva conforme regulamentações internacionais",
                "Promover eventos esportivos inclusivos e competições adaptadas",
                "Capacitar profissionais em educação física adaptada e esporte paralímpico",
                "Desenvolver programa de esporte recreativo para diferentes faixas etárias"
            ],
            "TAA": [
                "Implementar protocolo de avaliação para indicação e contraindicação de TAA",
                "Desenvolver programa de sessões terapêuticas estruturadas com animais treinados",
                "Capacitar equipe multidisciplinar em técnicas de terapia assistida por animais",
                "Estabelecer protocolos de higiene, segurança e bem-estar animal",
                "Oferecer atividades grupais e individuais conforme objetivos terapêuticos",
                "Realizar registro sistemático de progressos e evolução terapêutica",
                "Promover integração da TAA com outras modalidades terapêuticas"
            ],
            "APC": [
                "Implementar oficinas de artes visuais adaptadas às diferentes deficiências",
                "Desenvolver programa de musicoterapia com instrumentos adaptados",
                "Oferecer atividades de teatro e expressão corporal inclusivas",
                "Promover oficinas de literatura e contação de histórias acessíveis",
                "Realizar eventos culturais inclusivos e mostras artísticas",
                "Capacitar arte-terapeutas e educadores em técnicas adaptadas",
                "Desenvolver produção cultural com participação ativa das pessoas com deficiência"
            ]
        }
        
        available_objectives = objectives_bank.get(area_code, [])
        # Selecionar aleatoriamente entre 3 e 5 objetivos
        num_objectives = random.randint(3, min(5, len(available_objectives)))
        selected = random.sample(available_objectives, num_objectives)
        
        return selected
    
    async def _generate_justification(
        self,
        area_info: Dict[str, Any],
        institution_data: Dict[str, Any],
        project_requirements: Dict[str, Any]
    ) -> str:
        """Gerar justificativa detalhada (mínimo 500 caracteres)"""
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        base_context = f"""
        A {institution_data['name']}, localizada em {institution_data['city']}/{institution_data['state']}, 
        atua há anos no atendimento às pessoas com deficiência, reconhecendo as necessidades específicas 
        desta população e as lacunas existentes nos serviços especializados da região.
        
        Segundo dados do IBGE (Censo 2010), aproximadamente 23,9% da população brasileira possui algum tipo de deficiência, 
        representando cerca de 45,6 milhões de pessoas. Esta parcela significativa da população necessita de serviços 
        especializados que atendam às suas especificidades, promovendo inclusão, autonomia e qualidade de vida.
        """
        
        specific_justifications = {
            "QSS": f"""
            {base_context}
            
            A qualificação de serviços de saúde para pessoas com deficiência é fundamental para garantir 
            o acesso universal e integral preconizado pelo SUS. Barreiras arquitetônicas, falta de equipamentos 
            adaptados e despreparo profissional constituem obstáculos significativos ao atendimento adequado.
            
            Este projeto visa eliminar essas barreiras através da adequação da ambiência conforme NBR 9050, 
            aquisição de equipamentos especializados e capacitação da equipe. A implementação beneficiará 
            diretamente cerca de {project_requirements.get('target_beneficiaries', 500)} pessoas com deficiência 
            mensalmente, melhorando a acessibilidade e qualidade do atendimento oferecido pela instituição.
            
            A relevância do projeto está alinhada com a Política Nacional de Saúde da Pessoa com Deficiência 
            e a Lei Brasileira de Inclusão (13.146/2015), promovendo a eliminação de barreiras e a garantia 
            de direitos fundamentais desta população.
            """,
            
            "RPD": f"""
            {base_context}
            
            A reabilitação e habilitação da pessoa com deficiência constitui processo complexo que exige 
            abordagem multidisciplinar especializada. Dados epidemiológicos indicam que aproximadamente 
            6,2% da população possui deficiência motora, necessitando de serviços de reabilitação específicos.
            
            A escassez de serviços especializados na região resulta em longas filas de espera e 
            deslocamentos custosos para outras cidades, comprometendo a continuidade do tratamento. 
            Este projeto propõe a implementação de centro de reabilitação multidisciplinar que atenderá 
            cerca de {project_requirements.get('target_beneficiaries', 300)} pessoas anualmente.
            
            A metodologia baseada em evidências científicas e a utilização de tecnologias assistivas 
            modernas garantirão resultados efetivos na recuperação funcional e melhoria da qualidade de vida. 
            O investimento de R$ {project_requirements['budget_total']:,.2f} proporcionará retorno social 
            significativo através da autonomia conquistada pelos usuários.
            """,
            
            "DDP": f"""
            {base_context}
            
            O diagnóstico precoce e preciso da deficiência é fundamental para o desenvolvimento de 
            estratégias terapêuticas eficazes e prevenção de limitações secundárias. Estudos demonstram 
            que a intervenção precoce pode reduzir em até 70% as limitações funcionais futuras.
            
            A ausência de serviços diagnósticos especializados na região resulta em diagnósticos tardios 
            ou imprecisos, comprometendo o prognóstico e o desenvolvimento pleno das pessoas com deficiência. 
            Este projeto estabelecerá centro diagnóstico multidisciplinar capaz de atender 
            {project_requirements.get('target_beneficiaries', 200)} casos anuais.
            
            A equipe especializada utilizará protocolos padronizados e instrumentos validados para 
            garantir a precisão diagnóstica. O diagnóstico adequado permitirá encaminhamentos específicos 
            e elaboração de planos terapêuticos individualizados, otimizando os resultados das intervenções.
            """,
            
            "EPD": f"""
            {base_context}
            
            Os primeiros anos de vida são cruciais para o desenvolvimento neurológico e funcional. 
            A identificação e estimulação precoce de deficiências em crianças de 0 a 3 anos pode 
            prevenir ou minimizar limitações futuras, proporcionando melhores oportunidades de desenvolvimento.
            
            Dados da literatura científica indicam que cada real investido em estimulação precoce 
            resulta em economia de sete reais em custos futuros com reabilitação e educação especial. 
            O projeto atenderá aproximadamente {project_requirements.get('target_beneficiaries', 150)} 
            crianças anualmente, beneficiando também suas famílias.
            
            A metodologia baseada em neuroplasticidade cerebral e desenvolvimento infantil utilizará 
            técnicas lúdicas e atrativas para estimular habilidades cognitivas, motoras, sensoriais 
            e sociais. O acompanhamento longitudinal garantirá continuidade no desenvolvimento.
            """,
            
            "ITR": f"""
            {base_context}
            
            A inserção da pessoa com deficiência no mercado de trabalho constitui direito fundamental 
            e estratégia essencial para inclusão social e autonomia econômica. Dados do Ministério do 
            Trabalho indicam que apenas 1,8% das vagas formais são ocupadas por pessoas com deficiência, 
            evidenciando a necessidade de programas específicos.
            
            As principais barreiras incluem falta de qualificação profissional, ausência de tecnologia 
            assistiva adequada e preconceito empresarial. Este projeto visa capacitar profissionalmente 
            {project_requirements.get('target_beneficiaries', 100)} pessoas com deficiência anualmente, 
            promovendo sua inserção no mercado de trabalho.
            
            A metodologia incluirá avaliação funcional, capacitação profissional, adaptação de postos 
            de trabalho e acompanhamento pós-inserção. Parcerias com empresas locais garantirão 
            oportunidades reais de emprego, contribuindo para o desenvolvimento econômico regional.
            """,
            
            "APE": f"""
            {base_context}
            
            A prática de atividades físicas e esportivas por pessoas com deficiência promove benefícios 
            físicos, psicológicos e sociais significativos. Estudos demonstram redução de 40% nos custos 
            com saúde entre praticantes regulares de atividade física adaptada.
            
            A falta de programas esportivos adaptados e profissionais especializados limita o acesso 
            desta população aos benefícios do exercício físico. Este projeto implementará centro de 
            atividades físicas e esportivas que atenderá {project_requirements.get('target_beneficiaries', 250)} 
            pessoas anualmente em diversas modalidades.
            
            A metodologia incluirá avaliação funcional, prescrição individualizada de exercícios, 
            treinamento técnico especializado e preparação para competições. Os benefícios incluem 
            melhoria do condicionamento físico, desenvolvimento de habilidades esportivas, socialização 
            e elevação da autoestima.
            """,
            
            "TAA": f"""
            {base_context}
            
            A Terapia Assistida por Animais (TAA) constitui intervenção terapêutica complementar com 
            evidências científicas robustas de eficácia. Estudos demonstram melhoria significativa na 
            comunicação, redução da ansiedade e desenvolvimento de habilidades sociais em pessoas com deficiência.
            
            A ausência deste recurso terapêutico na região priva as pessoas com deficiência de uma 
            modalidade terapêutica inovadora e eficaz. O projeto implementará programa estruturado de TAA 
            que beneficiará aproximadamente {project_requirements.get('target_beneficiaries', 120)} pessoas anualmente.
            
            A metodologia seguirá protocolos internacionais de TAA, utilizando animais devidamente 
            treinados e supervisionados por equipe multidisciplinar. Os objetivos terapêuticos serão 
            individualizados conforme necessidades específicas de cada usuário, garantindo resultados efetivos.
            """,
            
            "APC": f"""
            {base_context}
            
            A arte e a cultura constituem direitos fundamentais e ferramentas poderosas de expressão, 
            comunicação e desenvolvimento humano. Para pessoas com deficiência, as atividades artísticas 
            promovem benefícios terapêuticos, educacionais e sociais únicos.
            
            A escassez de programas culturais inclusivos limita as oportunidades de expressão criativa 
            e participação cultural desta população. Este projeto desenvolverá programa abrangente de 
            atividades artísticas e culturais que atenderá {project_requirements.get('target_beneficiaries', 180)} 
            pessoas anualmente em diversas modalidades.
            
            A metodologia incluirá oficinas de artes visuais, musicoterapia, teatro inclusivo, dança adaptada 
            e produção cultural. Os benefícios incluem desenvolvimento de habilidades artísticas, expressão 
            emocional, socialização e melhoria da autoestima, contribuindo para inclusão social e cultural.
            """
        }
        
        justification = specific_justifications.get(area_code, base_context)
        
        # Garantir mínimo de 500 caracteres
        if len(justification) < 500:
            justification += f"""
            
            A implementação deste projeto está fundamentada nas melhores práticas nacionais e internacionais, 
            seguindo diretrizes do Ministério da Saúde e organizações especializadas. A equipe técnica 
            qualificada e a infraestrutura adequada garantem a execução com qualidade e segurança.
            
            O impacto social esperado transcende os beneficiários diretos, promovendo mudança de paradigma 
            na comunidade local sobre inclusão e direitos da pessoa com deficiência, contribuindo para 
            uma sociedade mais justa e igualitária.
            """
        
        return justification.strip()
    
    async def _generate_methodology(self, area_info: Dict[str, Any]) -> str:
        """Gerar metodologia baseada na área prioritária"""
        return f"""
        A metodologia proposta baseia-se nas melhores práticas científicas para {area_info['name']}, 
        seguindo protocolos validados e diretrizes técnicas do Ministério da Saúde.
        
        Principais etapas metodológicas:
        
        {chr(10).join(f"• {action}" for action in area_info['typical_methodologies'])}
        
        A abordagem multidisciplinar garantirá atendimento integral e humanizado, com foco nos 
        resultados funcionais e na satisfação dos usuários. Registros sistemáticos permitirão 
        acompanhamento da evolução e ajustes nos protocolos quando necessário.
        
        A metodologia será continuamente aprimorada através de capacitações da equipe, 
        atualização científica e incorporação de novas tecnologias e evidências.
        """
    
    async def _generate_expected_results(self, area_info: Dict[str, Any]) -> str:
        """Gerar resultados esperados"""
        return f"""
        Os resultados esperados com a implementação do projeto incluem:
        
        {chr(10).join(f"• {result}" for result in area_info['expected_results'])}
        
        Adicionalmente, espera-se:
        • Melhoria dos indicadores de qualidade dos serviços
        • Aumento da satisfação dos usuários e familiares
        • Fortalecimento da rede de atenção à pessoa com deficiência
        • Contribuição para o desenvolvimento social e econômico local
        • Formação de profissionais especializados na área
        
        Os resultados serão mensurados através de indicadores específicos e acompanhamento 
        longitudinal dos beneficiários, permitindo avaliação contínua da efetividade das intervenções.
        """
    
    async def _generate_target_audience(self, area_info: Dict[str, Any]) -> str:
        """Gerar descrição do público-alvo"""
        return f"""
        Público-alvo: {area_info['target_beneficiaries']}
        
        Critérios de inclusão:
        • Residir na região de abrangência do projeto
        • Possuir indicação técnica para o serviço oferecido
        • Estar em condições clínicas estáveis para participação
        • Concordar com os termos de atendimento
        
        Critérios de exclusão:
        • Condições clínicas que impeçam a participação segura
        • Impossibilidade de adesão ao programa proposto
        • Residir fora da área de cobertura sem possibilidade de deslocamento
        
        O atendimento seguirá princípios de equidade, priorizando casos de maior vulnerabilidade 
        social e aqueles com menor acesso a serviços especializados.
        """
    
    async def _generate_sustainability_plan(
        self, area_info: Dict[str, Any], institution_data: Dict[str, Any]
    ) -> str:
        """Gerar plano de sustentabilidade"""
        return f"""
        Plano de Sustentabilidade do Projeto:
        
        1. SUSTENTABILIDADE FINANCEIRA:
        • Busca de financiamento público através de convênios municipais e estaduais
        • Parcerias com empresas locais para apoio contínuo
        • Captação de recursos através de projetos de responsabilidade social
        • Desenvolvimento de serviços autofinanciáveis quando aplicável
        
        2. SUSTENTABILIDADE TÉCNICA:
        • Formação e capacitação contínua da equipe técnica
        • Estabelecimento de protocolos e rotinas estruturadas
        • Criação de banco de dados para acompanhamento dos resultados
        • Parcerias acadêmicas para atualização científica
        
        3. SUSTENTABILIDADE INSTITUCIONAL:
        • Incorporação do projeto ao planejamento estratégico da {institution_data['name']}
        • Fortalecimento da governança e gestão do projeto
        • Estabelecimento de parcerias estratégicas duradouras
        • Advocacy para políticas públicas favoráveis
        
        4. SUSTENTABILIDADE SOCIAL:
        • Engajamento da comunidade local
        • Formação de grupos de apoio e voluntários
        • Desenvolvimento de lideranças entre os usuários
        • Articulação com movimentos sociais da área da deficiência
        
        A sustentabilidade será monitorada através de indicadores específicos e revisão 
        periódica das estratégias implementadas.
        """
    
    async def _generate_specialized_team(
        self, area_info: Dict[str, Any], total_budget: float
    ) -> List[Dict[str, Any]]:
        """Gerar equipe técnica especializada por área prioritária"""
        
        team_members = []
        personnel_budget = total_budget * (area_info['typical_budget_distribution']['pessoal'] / 100)
        
        # Mapear funções requeridas para cargos específicos
        role_mapping = {
            "Coordenador do projeto": "coordenador",
            "Coordenador (médico fisiatra ou neurologista)": "medico",
            "Coordenador médico especialista": "medico",
            "Coordenador médico pediatra/neuropediatra": "medico",
            "Coordenador (médico do trabalho ou terapeuta ocupacional)": "medico",
            "Coordenador (médico do esporte ou educador físico)": "medico",
            "Coordenador (psicólogo ou terapeuta ocupacional)": "psicologo",
            "Coordenador (arte-terapeuta ou educador artístico)": "arte_terapeuta",
            "Arquiteto especialista em acessibilidade": "instrutor",
            "Engenheiro civil": "instrutor",
            "Fisioterapeuta": "fisioterapeuta",
            "Fisioterapeuta pediátrico": "fisioterapeuta",
            "Fisioterapeuta esportivo": "fisioterapeuta",
            "Terapeuta ocupacional": "terapeuta_ocupacional",
            "Terapeuta ocupacional pediátrico": "terapeuta_ocupacional",
            "Fonoaudiólogo": "fonoaudiologo",
            "Fonoaudiólogo pediátrico": "fonoaudiologo",
            "Psicólogo": "psicologo",
            "Psicólogo infantil": "psicologo",
            "Psicólogo organizacional": "psicologo",
            "Psicólogo do esporte": "psicologo",
            "Assistente social": "assistente_social",
            "Enfermeiro especializado": "enfermeiro",
            "Educador físico especializado": "educador_fisico",
            "Classificador funcional": "instrutor",
            "Terapeuta especializado em TAA": "arte_terapeuta",
            "Condutor de animais certificado": "instrutor",
            "Veterinário": "medico",
            "Musicoterapeuta": "musicoterapeuta",
            "Arte-terapeuta": "arte_terapeuta",
            "Instrutor de dança adaptada": "instrutor",
            "Produtor cultural": "instrutor",
            "Instrutor profissionalizante": "instrutor",
            "Auxiliar de atividades": "auxiliar"
        }
        
        remaining_budget = personnel_budget
        
        for role_description in area_info['required_team_roles']:
            # Mapear para categoria salarial
            role_category = role_mapping.get(role_description, "instrutor")
            salary_info = self.team_salary_ranges[role_category]
            
            # Calcular salário baseado no orçamento disponível
            monthly_salary = min(
                random.uniform(salary_info['min'], salary_info['max']),
                remaining_budget / 24  # 24 meses de projeto
            )
            
            if monthly_salary < salary_info['min'] * 0.5:  # Salário muito baixo
                continue
            
            team_member = {
                "role": role_description,
                "name": f"Profissional {role_description.split()[0]}",
                "qualification": await self._generate_qualification(role_description),
                "weekly_hours": salary_info['hours_week'],
                "monthly_salary": round(monthly_salary, 2)
            }
            
            team_members.append(team_member)
            remaining_budget -= monthly_salary * 24
            
            if remaining_budget <= 0:
                break
        
        return team_members
    
    async def _generate_qualification(self, role: str) -> str:
        """Gerar qualificação profissional baseada na função"""
        qualifications = {
            "Coordenador": "Graduação em área da saúde, especialização em gestão, experiência mínima de 5 anos em coordenação de projetos",
            "médico": "Graduação em Medicina, especialização na área específica, registro no CRM ativo",
            "Fisioterapeuta": "Graduação em Fisioterapia, especialização em reabilitação, registro no CREFITO ativo",
            "Terapeuta ocupacional": "Graduação em Terapia Ocupacional, especialização em reabilitação, registro no CREFITO ativo",
            "Fonoaudiólogo": "Graduação em Fonoaudiologia, especialização em área específica, registro no CRFa ativo",
            "Psicólogo": "Graduação em Psicologia, especialização em área específica, registro no CRP ativo",
            "Assistente social": "Graduação em Serviço Social, registro no CRESS ativo, experiência com pessoa com deficiência",
            "Enfermeiro": "Graduação em Enfermagem, especialização em área específica, registro no COREN ativo",
            "Educador físico": "Graduação em Educação Física, especialização em atividade física adaptada, registro no CREF ativo",
            "Arte-terapeuta": "Graduação em área específica, formação em arte-terapia, experiência com pessoa com deficiência",
            "Instrutor": "Formação técnica ou superior em área específica, experiência comprovada, certificações técnicas"
        }
        
        for key, qual in qualifications.items():
            if key.lower() in role.lower():
                return qual
        
        return "Formação superior em área correlata, experiência comprovada, certificações específicas"
    
    async def _generate_detailed_budget(
        self, area_info: Dict[str, Any], total_budget: float, team_members: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Gerar orçamento detalhado baseado na área prioritária"""
        
        budget_items = []
        budget_dist = area_info['typical_budget_distribution']
        
        # 1. PESSOAL
        personnel_total = 0
        for member in team_members:
            annual_cost = member['monthly_salary'] * 24  # 24 meses
            budget_items.append({
                "category": "pessoal",
                "subcategory": member['role'],
                "description": f"{member['role']} - {member['weekly_hours']}h/semana por 24 meses",
                "unit": "mês",
                "quantity": 24,
                "unit_value": member['monthly_salary'],
                "total_value": annual_cost,
                "nature_expense_code": "339036",
                "justification": f"Contratação de {member['role']} conforme carga horária e qualificação exigida"
            })
            personnel_total += annual_cost
        
        # 2. MATERIAL PERMANENTE
        if budget_dist.get('material_permanente', 0) > 0:
            equipment_budget = total_budget * (budget_dist['material_permanente'] / 100)
            equipment_items = await self._generate_equipment_items(area_info, equipment_budget)
            budget_items.extend(equipment_items)
        
        # 3. MATERIAL DE CONSUMO
        if budget_dist.get('material_consumo', 0) > 0:
            consumable_budget = total_budget * (budget_dist['material_consumo'] / 100)
            consumable_items = await self._generate_consumable_items(area_info, consumable_budget)
            budget_items.extend(consumable_items)
        
        # 4. REFORMAS (se aplicável)
        if budget_dist.get('reformas', 0) > 0:
            reform_budget = total_budget * (budget_dist['reformas'] / 100)
            reform_items = await self._generate_reform_items(area_info, reform_budget)
            budget_items.extend(reform_items)
        
        # 5. DESPESAS ADMINISTRATIVAS
        if budget_dist.get('despesas_administrativas', 0) > 0:
            admin_budget = total_budget * (budget_dist['despesas_administrativas'] / 100)
            admin_items = await self._generate_administrative_items(area_info, admin_budget)
            budget_items.extend(admin_items)
        
        # 6. AUDITORIA (OBRIGATÓRIA)
        audit_budget = max(total_budget * 0.03, 5000)  # Mínimo 3% ou R$ 5.000
        budget_items.append({
            "category": "auditoria",
            "subcategory": "Auditoria Independente",
            "description": "Auditoria independente conforme exigência PRONAS/PCD",
            "unit": "serviço",
            "quantity": 1,
            "unit_value": audit_budget,
            "total_value": audit_budget,
            "nature_expense_code": "339039",
            "justification": "Auditoria independente obrigatória conforme Portaria de Consolidação nº 5/2017"
        })
        
        # 7. CAPTAÇÃO DE RECURSOS
        captacao_percentage = min(5, (50000 / total_budget) * 100)  # 5% ou R$ 50.000 (o menor)
        captacao_budget = total_budget * (captacao_percentage / 100)
        budget_items.append({
            "category": "captacao_recursos",
            "subcategory": "Captação de Recursos",
            "description": f"Captação de recursos - {captacao_percentage:.1f}% do orçamento total",
            "unit": "serviço",
            "quantity": 1,
            "unit_value": captacao_budget,
            "total_value": captacao_budget,
            "nature_expense_code": "339039",
            "justification": "Captação de recursos conforme limite estabelecido (máximo 5% ou R$ 50.000)"
        })
        
        return budget_items
    
    async def _generate_equipment_items(
        self, area_info: Dict[str, Any], budget: float
    ) -> List[Dict[str, Any]]:
        """Gerar itens de material permanente por área"""
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        equipment_catalog = {
            "QSS": [
                {"name": "Cadeira de rodas hospitalar", "unit_price": 2500, "quantity": 4},
                {"name": "Maca de transferência hidráulica", "unit_price": 8000, "quantity": 2},
                {"name": "Sistema de sinalização tátil", "unit_price": 15000, "quantity": 1},
                {"name": "Mobiliário adaptado para recepção", "unit_price": 12000, "quantity": 1},
                {"name": "Equipamento de comunicação alternativa", "unit_price": 5000, "quantity": 3},
                {"name": "Barras de apoio e corrimãos", "unit_price": 3000, "quantity": 2}
            ],
            "RPD": [
                {"name": "Aparelho de FES (Estimulação Elétrica)", "unit_price": 25000, "quantity": 1},
                {"name": "Mesa de fisioterapia elétrica", "unit_price": 8000, "quantity": 2},
                {"name": "Equipamento de marcha assistida", "unit_price": 35000, "quantity": 1},
                {"name": "Kit de órteses e próteses", "unit_price": 15000, "quantity": 1},
                {"name": "Equipamento de terapia ocupacional", "unit_price": 12000, "quantity": 1},
                {"name": "Sistema de comunicação alternativa", "unit_price": 8000, "quantity": 2}
            ],
            "DDP": [
                {"name": "Equipamento de avaliação neuropsicológica", "unit_price": 20000, "quantity": 1},
                {"name": "Kit de testes diagnósticos", "unit_price": 15000, "quantity": 1},
                {"name": "Equipamento de audiometria", "unit_price": 25000, "quantity": 1},
                {"name": "Material de avaliação do desenvolvimento", "unit_price": 10000, "quantity": 1},
                {"name": "Sistema de videoconferência para discussão de casos", "unit_price": 8000, "quantity": 1}
            ],
            "EPD": [
                {"name": "Brinquedos terapêuticos para estimulação", "unit_price": 8000, "quantity": 2},
                {"name": "Equipamento de estimulação sensorial", "unit_price": 15000, "quantity": 1},
                {"name": "Material de fisioterapia pediátrica", "unit_price": 12000, "quantity": 1},
                {"name": "Kit de avaliação do desenvolvimento infantil", "unit_price": 10000, "quantity": 1},
                {"name": "Mobiliário adaptado para crianças", "unit_price": 6000, "quantity": 2}
            ],
            "ITR": [
                {"name": "Equipamento de tecnologia assistiva para trabalho", "unit_price": 20000, "quantity": 2},
                {"name": "Software de treinamento profissional", "unit_price": 15000, "quantity": 1},
                {"name": "Equipamento de adaptação de posto de trabalho", "unit_price": 12000, "quantity": 2},
                {"name": "Ferramentas e equipamentos de oficina", "unit_price": 18000, "quantity": 1},
                {"name": "Material didático para capacitação", "unit_price": 8000, "quantity": 1}
            ],
            "APE": [
                {"name": "Equipamento de musculação adaptado", "unit_price": 35000, "quantity": 1},
                {"name": "Material esportivo paradesportivo", "unit_price": 15000, "quantity": 2},
                {"name": "Cadeiras de rodas esportivas", "unit_price": 12000, "quantity": 3},
                {"name": "Equipamento de fisioterapia esportiva", "unit_price": 20000, "quantity": 1},
                {"name": "Material de natação adaptada", "unit_price": 8000, "quantity": 1}
            ],
            "TAA": [
                {"name": "Equipamento de higienização para animais", "unit_price": 8000, "quantity": 1},
                {"name": "Material de segurança para TAA", "unit_price": 5000, "quantity": 2},
                {"name": "Equipamento veterinário básico", "unit_price": 12000, "quantity": 1},
                {"name": "Material de treinamento animal", "unit_price": 6000, "quantity": 1},
                {"name": "Estrutura física para atividades", "unit_price": 15000, "quantity": 1}
            ],
            "APC": [
                {"name": "Instrumentos musicais adaptados", "unit_price": 15000, "quantity": 1},
                {"name": "Material de artes visuais", "unit_price": 8000, "quantity": 2},
                {"name": "Equipamento de som e audiovisual", "unit_price": 12000, "quantity": 1},
                {"name": "Material de teatro e expressão", "unit_price": 6000, "quantity": 1},
                {"name": "Equipamento de produção cultural", "unit_price": 10000, "quantity": 1}
            ]
        }
        
        items = []
        available_equipment = equipment_catalog.get(area_code, [])
        remaining_budget = budget
        
        for equipment in available_equipment:
            if remaining_budget <= 0:
                break
                
            total_cost = equipment['unit_price'] * equipment['quantity']
            if total_cost <= remaining_budget:
                items.append({
                    "category": "material_permanente",
                    "subcategory": equipment['name'],
                    "description": f"{equipment['name']} - {equipment['quantity']} unidade(s)",
                    "unit": "unidade",
                    "quantity": equipment['quantity'],
                    "unit_value": equipment['unit_price'],
                    "total_value": total_cost,
                    "nature_expense_code": "449052",
                    "justification": f"Equipamento necessário para {area_info['name']}"
                })
                remaining_budget -= total_cost
        
        return items
    
    async def _generate_consumable_items(
        self, area_info: Dict[str, Any], budget: float
    ) -> List[Dict[str, Any]]:
        """Gerar itens de material de consumo"""
        
        items = [
            {
                "category": "material_consumo",
                "subcategory": "Material de escritório",
                "description": "Papelaria, impressos, material gráfico para 24 meses",
                "unit": "mês",
                "quantity": 24,
                "unit_value": budget * 0.3 / 24,
                "total_value": budget * 0.3,
                "nature_expense_code": "339030",
                "justification": "Material de escritório necessário para funcionamento do projeto"
            },
            {
                "category": "material_consumo",
                "subcategory": "Material específico da área",
                "description": f"Materiais específicos para {area_info['name']} por 24 meses",
                "unit": "mês",
                "quantity": 24,
                "unit_value": budget * 0.7 / 24,
                "total_value": budget * 0.7,
                "nature_expense_code": "339030",
                "justification": "Materiais de consumo específicos para as atividades do projeto"
            }
        ]
        
        return items
    
    async def _generate_reform_items(
        self, area_info: Dict[str, Any], budget: float
    ) -> List[Dict[str, Any]]:
        """Gerar itens de reforma e adequação"""
        
        items = [
            {
                "category": "reformas",
                "subcategory": "Adequação de acessibilidade",
                "description": "Reformas para adequação de acessibilidade conforme NBR 9050",
                "unit": "m²",
                "quantity": 200,
                "unit_value": budget / 200,
                "total_value": budget,
                "nature_expense_code": "449051",
                "justification": "Adequação da infraestrutura física para acessibilidade universal"
            }
        ]
        
        return items
    
    async def _generate_administrative_items(
        self, area_info: Dict[str, Any], budget: float
    ) -> List[Dict[str, Any]]:
        """Gerar itens de despesas administrativas"""
        
        items = [
            {
                "category": "despesas_administrativas",
                "subcategory": "Comunicação e internet",
                "description": "Telefone fixo e móvel, internet banda larga por 24 meses",
                "unit": "mês",
                "quantity": 24,
                "unit_value": budget * 0.4 / 24,
                "total_value": budget * 0.4,
                "nature_expense_code": "339039",
                "justification": "Despesas com comunicação necessárias para o projeto"
            },
            {
                "category": "despesas_administrativas",
                "subcategory": "Transporte e combustível",
                "description": "Transporte para atividades do projeto e visitas domiciliares",
                "unit": "mês",
                "quantity": 24,
                "unit_value": budget * 0.6 / 24,
                "total_value": budget * 0.6,
                "nature_expense_code": "339039",
                "justification": "Despesas com transporte para execução das atividades"
            }
        ]
        
        return items
    
    async def _generate_project_timeline(
        self, area_info: Dict[str, Any], timeline_months: int
    ) -> List[Dict[str, Any]]:
        """Gerar cronograma do projeto"""
        
        timeline = [
            {
                "phase_name": "Planejamento e Preparação",
                "start_month": 1,
                "end_month": 3,
                "deliverables": [
                    "Contratação da equipe técnica",
                    "Aquisição de equipamentos",
                    "Adequação da infraestrutura",
                    "Capacitação da equipe"
                ]
            },
            {
                "phase_name": "Implementação das Atividades",
                "start_month": 4,
                "end_month": timeline_months - 3,
                "deliverables": [
                    "Início dos atendimentos",
                    "Desenvolvimento das atividades principais",
                    "Acompanhamento dos beneficiários",
                    "Relatórios parciais"
                ]
            },
            {
                "phase_name": "Monitoramento e Avaliação",
                "start_month": timeline_months - 2,
                "end_month": timeline_months,
                "deliverables": [
                    "Avaliação final dos resultados",
                    "Relatório final do projeto",
                    "Prestação de contas",
                    "Disseminação dos resultados"
                ]
            }
        ]
        
        # Ajustar para projetos mais curtos
        if timeline_months <= 12:
            timeline = [
                {
                    "phase_name": "Planejamento e Início",
                    "start_month": 1,
                    "end_month": 2,
                    "deliverables": ["Contratação", "Aquisições", "Capacitação"]
                },
                {
                    "phase_name": "Execução",
                    "start_month": 3,
                    "end_month": timeline_months - 1,
                    "deliverables": ["Atendimentos", "Atividades", "Monitoramento"]
                },
                {
                    "phase_name": "Finalização",
                    "start_month": timeline_months,
                    "end_month": timeline_months,
                    "deliverables": ["Relatório final", "Prestação de contas"]
                }
            ]
        
        return timeline
    
    async def _generate_project_goals(
        self, area_info: Dict[str, Any], target_beneficiaries: int
    ) -> List[Dict[str, Any]]:
        """Gerar metas e indicadores do projeto"""
        
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        goals_templates = {
            "QSS": [
                {
                    "indicator_name": "Número de pessoas atendidas mensalmente",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de atendimentos no sistema",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Percentual de satisfação dos usuários",
                    "target_value": 85,
                    "measurement_method": "Pesquisa de satisfação trimestral",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Percentual de adequação de acessibilidade",
                    "target_value": 100,
                    "measurement_method": "Checklist de conformidade NBR 9050",
                    "frequency": "semestral"
                }
            ],
            "RPD": [
                {
                    "indicator_name": "Número de pessoas em reabilitação",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de prontuários",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Percentual de melhoria funcional",
                    "target_value": 70,
                    "measurement_method": "Avaliação funcional padronizada",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Taxa de adesão ao tratamento",
                    "target_value": 80,
                    "measurement_method": "Percentual de frequência aos atendimentos",
                    "frequency": "mensal"
                }
            ],
            "DDP": [
                {
                    "indicator_name": "Número de diagnósticos realizados",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de laudos emitidos",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Tempo médio para diagnóstico (dias)",
                    "target_value": 30,
                    "measurement_method": "Cálculo do tempo entre avaliação e laudo",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Percentual de diagnósticos precoces",
                    "target_value": 60,
                    "measurement_method": "Análise da idade no momento do diagnóstico",
                    "frequency": "trimestral"
                }
            ],
            "EPD": [
                {
                    "indicator_name": "Número de crianças em estimulação precoce",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de atendimentos",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Percentual de melhoria do desenvolvimento",
                    "target_value": 75,
                    "measurement_method": "Escala de desenvolvimento aplicada",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Taxa de engajamento familiar",
                    "target_value": 90,
                    "measurement_method": "Participação em atividades e orientações",
                    "frequency": "mensal"
                }
            ],
            "ITR": [
                {
                    "indicator_name": "Número de pessoas capacitadas",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de participantes nos cursos",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Taxa de inserção no mercado de trabalho",
                    "target_value": 40,
                    "measurement_method": "Acompanhamento pós-capacitação",
                    "frequency": "semestral"
                },
                {
                    "indicator_name": "Percentual de manutenção no emprego",
                    "target_value": 70,
                    "measurement_method": "Follow-up após 6 meses da inserção",
                    "frequency": "semestral"
                }
            ],
            "APE": [
                {
                    "indicator_name": "Número de praticantes regulares",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Frequência nas atividades esportivas",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Melhoria do condicionamento físico",
                    "target_value": 60,
                    "measurement_method": "Testes de aptidão física",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Participação em competições",
                    "target_value": 20,
                    "measurement_method": "Número de atletas em competições",
                    "frequency": "anual"
                }
            ],
            "TAA": [
                {
                    "indicator_name": "Número de pessoas em TAA",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Registro de sessões de TAA",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Melhoria da comunicação",
                    "target_value": 65,
                    "measurement_method": "Avaliação da comunicação pré/pós",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Redução de ansiedade",
                    "target_value": 50,
                    "measurement_method": "Escala de avaliação de ansiedade",
                    "frequency": "trimestral"
                }
            ],
            "APC": [
                {
                    "indicator_name": "Número de participantes nas oficinas",
                    "target_value": target_beneficiaries,
                    "measurement_method": "Lista de presença nas atividades",
                    "frequency": "mensal"
                },
                {
                    "indicator_name": "Produções artísticas realizadas",
                    "target_value": 50,
                    "measurement_method": "Registro de obras/apresentações produzidas",
                    "frequency": "trimestral"
                },
                {
                    "indicator_name": "Melhoria da autoestima",
                    "target_value": 70,
                    "measurement_method": "Escala de autoestima aplicada",
                    "frequency": "semestral"
                }
            ]
        }
        
        return goals_templates.get(area_code, [])
    
    async def _validate_project_compliance(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Validar conformidade do projeto com regras do PRONAS/PCD"""
        
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": []
        }
        
        # 1. Validar justificativa mínima
        if len(project.get('justification', '')) < self.compliance_rules['min_justification_length']:
            validation_results["errors"].append(
                f"Justificativa deve ter pelo menos {self.compliance_rules['min_justification_length']} caracteres"
            )
            validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Tamanho mínimo da justificativa")
        
        # 2. Validar objetivos específicos
        specific_obj = project.get('specific_objectives', [])
        if len(specific_obj) < self.compliance_rules['min_specific_objectives']:
            validation_results["errors"].append(
                f"Deve haver pelo menos {self.compliance_rules['min_specific_objectives']} objetivos específicos"
            )
            validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Número mínimo de objetivos específicos")
        
        # 3. Validar cronograma
        timeline_months = project.get('timeline_months', 0)
        if timeline_months < self.compliance_rules['min_timeline_months']:
            validation_results["errors"].append(
                f"Prazo mínimo do projeto é {self.compliance_rules['min_timeline_months']} meses"
            )
            validation_results["is_valid"] = False
        
        if timeline_months > self.compliance_rules['max_timeline_months']:
            validation_results["errors"].append(
                f"Prazo máximo do projeto é {self.compliance_rules['max_timeline_months']} meses"
            )
            validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Prazo do projeto")
        
        # 4. Validar orçamento - auditoria obrigatória
        budget_items = project.get('budget_items', [])
        has_audit = any(item.get('category') == 'auditoria' for item in budget_items)
        if not has_audit:
            validation_results["errors"].append("Orçamento deve incluir item de auditoria independente")
            validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Auditoria independente obrigatória")
        
        # 5. Validar captação de recursos
        total_budget = project.get('budget_total', 0)
        captacao_items = [item for item in budget_items if item.get('category') == 'captacao_recursos']
        if captacao_items:
            captacao_total = sum(item.get('total_value', 0) for item in captacao_items)
            max_captacao_abs = self.compliance_rules['max_captacao_absolute']
            max_captacao_perc = total_budget * (self.compliance_rules['max_captacao_percentage_of_total'] / 100)
            max_allowed = min(max_captacao_abs, max_captacao_perc)
            
            if captacao_total > max_allowed:
                validation_results["errors"].append(
                    f"Captação de recursos não pode exceder 5% do orçamento total ou R$ {max_captacao_abs:,.2f}"
                )
                validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Limites de captação de recursos")
        
        # 6. Validar equipe técnica
        team_members = project.get('team_members', [])
        if len(team_members) < 2:
            validation_results["warnings"].append("Projeto deveria ter pelo menos 2 profissionais na equipe")
        
        validation_results["checks_performed"].append("Composição da equipe técnica")
        
        # 7. Validar consistência orçamentária
        budget_total_items = sum(item.get('total_value', 0) for item in budget_items)
        if abs(budget_total_items - total_budget) > 100:  # Margem de R$ 100
            validation_results["errors"].append(
                "Soma dos itens orçamentários deve ser igual ao orçamento total"
            )
            validation_results["is_valid"] = False
        
        validation_results["checks_performed"].append("Consistência orçamentária")
        
        # 8. Validar metas e indicadores
        goals = project.get('goals', [])
        if len(goals) < 2:
            validation_results["warnings"].append("Projeto deveria ter pelo menos 2 metas/indicadores")
        
        validation_results["checks_performed"].append("Metas e indicadores")
        
        return validation_results
    
    async def _calculate_compliance_score(
        self, project: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> float:
        """Calcular score de conformidade (0.0 a 1.0)"""
        
        total_checks = len(validation_results.get('checks_performed', []))
        if total_checks == 0:
            return 0.0
        
        errors = len(validation_results.get('errors', []))
        warnings = len(validation_results.get('warnings', []))
        
        # Penalidades por erros e avisos
        error_penalty = errors * 0.15  # 15% por erro
        warning_penalty = warnings * 0.05  # 5% por aviso
        
        # Score base
        base_score = 1.0
        
        # Aplicar penalidades
        final_score = max(0.0, base_score - error_penalty - warning_penalty)
        
        # Bonus por elementos extras
        bonus = 0.0
        
        # Bonus por sustentabilidade
        if project.get('sustainability_plan') and len(project['sustainability_plan']) > 200:
            bonus += 0.05
        
        # Bonus por metodologia detalhada
        if project.get('methodology') and len(project['methodology']) > 300:
            bonus += 0.05
        
        # Bonus por equipe qualificada
        team_members = project.get('team_members', [])
        if len(team_members) >= 4:
            bonus += 0.05
        
        return min(1.0, final_score + bonus)
    
    async def _calculate_confidence_score(
        self, project: Dict[str, Any], area_info: Dict[str, Any]
    ) -> float:
        """Calcular score de confiança da IA (0.0 a 1.0)"""
        
        confidence_factors = []
        
        # 1. Conformidade com área prioritária
        area_alignment = 0.9  # Alta conformidade com templates da área
        confidence_factors.append(area_alignment)
        
        # 2. Completude dos dados
        required_fields = ['title', 'general_objective', 'specific_objectives', 'justification', 
                          'methodology', 'team_members', 'budget_items', 'goals']
        completed_fields = sum(1 for field in required_fields if project.get(field))
        completeness = completed_fields / len(required_fields)
        confidence_factors.append(completeness)
        
        # 3. Qualidade do orçamento
        budget_items = project.get('budget_items', [])
        if budget_items:
            has_all_categories = all(
                any(item.get('category') == cat for item in budget_items)
                for cat in ['pessoal', 'auditoria']  # Categorias essenciais
            )
            budget_quality = 0.9 if has_all_categories else 0.6
        else:
            budget_quality = 0.3
        confidence_factors.append(budget_quality)
        
        # 4. Adequação da equipe
        team_members = project.get('team_members', [])
        required_roles = len(area_info.get('required_team_roles', []))
        actual_roles = len(team_members)
        team_adequacy = min(1.0, actual_roles / max(1, required_roles))
        confidence_factors.append(team_adequacy)
        
        # 5. Viabilidade do cronograma
        timeline_months = project.get('timeline_months', 0)
        if 6 <= timeline_months <= 48:
            timeline_viability = 0.9
        else:
            timeline_viability = 0.5
        confidence_factors.append(timeline_viability)
        
        # Média ponderada
        weights = [0.25, 0.2, 0.2, 0.2, 0.15]  # Soma = 1.0
        weighted_confidence = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
        
        return min(1.0, max(0.0, weighted_confidence))
    
    async def _generate_recommendations(
        self, project: Dict[str, Any], validation_results: Dict[str, Any], area_info: Dict[str, Any]
    ) -> List[str]:
        """Gerar recomendações baseadas na validação"""
        
        recommendations = []
        
        # Recomendações baseadas nos erros
        if validation_results.get('errors'):
            recommendations.append(
                "Corrigir os erros identificados na validação antes da submissão do projeto"
            )
        
        # Recomendações baseadas nos avisos
        if validation_results.get('warnings'):
            recommendations.append(
                "Considerar as sugestões de melhoria identificadas na validação"
            )
        
        # Recomendações específicas por área
        area_code = next(code for code, info in self.priority_areas.items() if info == area_info)
        
        area_recommendations = {
            "QSS": [
                "Realizar diagnóstico de acessibilidade antes do início das adequações",
                "Envolver pessoas com deficiência na avaliação das melhorias implementadas",
                "Documentar todas as adequações com fotos antes e depois"
            ],
            "RPD": [
                "Estabelecer protocolos de avaliação funcional padronizados",
                "Implementar sistema de registro eletrônico de evolução dos pacientes",
                "Criar programa de orientação familiar para continuidade do tratamento"
            ],
            "DDP": [
                "Desenvolver fluxograma de atendimento para otimizar o processo diagnóstico",
                "Estabelecer rede de referência com outros serviços especializados",
                "Criar protocolo de comunicação de diagnóstico às famílias"
            ],
            "EPD": [
                "Articular com serviços de saúde materno-infantil para identificação precoce",
                "Desenvolver material educativo para orientação familiar",
                "Estabelecer critérios claros de alta e transição para outros serviços"
            ],
            "ITR": [
                "Mapear empresas locais para parcerias de colocação profissional",
                "Desenvolver programa de sensibilização empresarial sobre inclusão",
                "Criar sistema de acompanhamento pós-inserção no trabalho"
            ],
            "APE": [
                "Estabelecer parcerias com clubes e associações esportivas locais",
                "Desenvolver programa de formação de instrutores especializados",
                "Criar calendário de eventos esportivos inclusivos"
            ],
            "TAA": [
                "Desenvolver protocolos rigorosos de higiene e segurança",
                "Estabelecer parceria com clínica veterinária para cuidados dos animais",
                "Criar programa de certificação para condutores de animais"
            ],
            "APC": [
                "Estabelecer parcerias com instituições culturais locais",
                "Desenvolver programa de formação de arte-terapeutas",
                "Criar calendário de eventos culturais inclusivos"
            ]
        }
        
        specific_recommendations = area_recommendations.get(area_code, [])
        recommendations.extend(random.sample(specific_recommendations, min(3, len(specific_recommendations))))
        
        # Recomendações gerais
        general_recommendations = [
            "Estabelecer indicadores de qualidade para monitoramento contínuo",
            "Desenvolver plano de comunicação para divulgação dos resultados",
            "Criar comitê gestor com representação da comunidade beneficiária",
            "Implementar sistema de feedback dos usuários",
            "Estabelecer parcerias com universidades para avaliação externa",
            "Desenvolver plano de sustentabilidade financeira do projeto"
        ]
        
        recommendations.extend(random.sample(general_recommendations, 2))
        
        return recommendations
    
    async def _find_similar_projects(self, priority_area_code: str) -> List[Dict[str, Any]]:
        """Buscar projetos similares (simulado)"""
        
        # Simulação de projetos similares baseados na área prioritária
        similar_projects = [
            {
                "title": f"Projeto similar em {priority_area_code} - Região Sul",
                "institution": "Instituição Similar",
                "budget": 450000,
                "beneficiaries": 180,
                "similarity_score": 0.85,
                "outcomes": "Resultados positivos relatados",
                "lessons_learned": "Importância da articulação com rede local"
            },
            {
                "title": f"Experiência exitosa em {priority_area_code} - Nordeste",
                "institution": "Centro de Referência",
                "budget": 520000,
                "beneficiaries": 220,
                "similarity_score": 0.78,
                "outcomes": "Metas superadas em 15%",
                "lessons_learned": "Engajamento familiar é fundamental para sucesso"
            }
        ]
        
        return similar_projects

# ==================== UTILITY FUNCTIONS ====================

def format_currency(value: float) -> str:
    """Formatar valor monetário para Real brasileiro"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calculate_percentage(value: float, total: float) -> float:
    """Calcular percentual"""
    if total == 0:
        return 0.0
    return (value / total) * 100

def validate_cnpj(cnpj: str) -> bool:
    """Validar CNPJ (implementação básica)"""
    import re
    return bool(re.match(r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$', cnpj))

def validate_cpf(cpf: str) -> bool:
    """Validar CPF (implementação básica)"""
    import re
    return bool(re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf))

def validate_cep(cep: str) -> bool:
    """Validar CEP"""
    import re
    return bool(re.match(r'^\d{5}-\d{3}$', cep))