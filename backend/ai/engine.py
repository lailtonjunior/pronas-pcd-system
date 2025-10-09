"""
Motor de IA especializada para o PRONAS/PCD (v2.0 - RAG + Gemini)
Utiliza Retrieval-Augmented Generation para fornecer respostas e gerar projetos
com base em uma base de conhecimento vetorizada.
"""

import asyncio
import logging
from typing import Dict, List, Any

import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.domain.services.vector_service import VectorService

# Configurar logging
logger = logging.getLogger(__name__)

settings = get_settings()

# --- Configuração do Modelo Generativo Gemini ---
try:
    # Configura a API do Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    # Configurações de segurança para a geração de conteúdo
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # Modelo generativo que será usado para criar as respostas
    generative_model = genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest',
        safety_settings=safety_settings
    )
    logger.info("✅ Modelo Generativo Gemini (gemini-1.5-pro-latest) configurado com sucesso.")

except Exception as e:
    logger.error(f"❌ Falha crítica ao configurar a API ou o modelo do Gemini: {e}")
    generative_model = None


class PronasAIEngine:
    """
    Motor de IA que integra a busca vetorial (RAG) com o poder de geração do Gemini.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa o motor de IA.

        Args:
            session: Uma sessão assíncrona do SQLAlchemy para acessar o banco de dados.
        """
        if not generative_model:
            raise RuntimeError("O modelo generativo do Gemini não foi inicializado. Verifique a chave de API e as configurações.")
            
        self.session = session
        self.vector_service = VectorService(session)

    async def answer_query_with_context(self, query: str) -> str:
        """
        Responde a uma pergunta do usuário buscando contexto na base de conhecimento.

        Args:
            query: A pergunta do usuário.

        Returns:
            A resposta gerada pela IA.
        """
        logger.info(f"Buscando contexto para a pergunta: '{query[:50]}...'")
        
        # 1. Buscar chunks de conhecimento relevantes no banco de dados vetorial
        similar_chunks = await self.vector_service.find_similar_chunks(query, limit=5)
        
        if not similar_chunks:
            logger.warning("Nenhum contexto relevante encontrado na base de conhecimento.")
            return "Desculpe, não encontrei informações sobre este tópico na minha base de conhecimento do PRONAS/PCD."

        # 2. Construir o prompt para o Gemini
        context = "\n\n".join([chunk[0] for chunk in similar_chunks])
        
        prompt = f"""
        Você é um especialista sênior no programa PRONAS/PCD do Ministério da Saúde do Brasil.
        Sua tarefa é responder à pergunta do usuário de forma clara, objetiva e baseada
        estritamente nas informações fornecidas no contexto abaixo.

        **Contexto Relevante (extraído de documentos oficiais):**
        ---
        {context}
        ---

        **Pergunta do Usuário:**
        "{query}"

        **Instruções:**
        - Responda em português do Brasil.
        - Se a resposta não estiver no contexto, afirme que a informação não foi encontrada nos documentos fornecidos.
        - Não invente informações. Ater-se aos fatos do contexto.
        - Formate a resposta de maneira clara, usando listas ou parágrafos curtos se necessário.

        **Resposta:**
        """
        
        logger.info("Enviando prompt enriquecido com contexto para o Gemini...")
        
        # 3. Chamar o modelo generativo do Gemini
        try:
            response = await generative_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com o Gemini: {e}")
            return "Ocorreu um erro ao processar sua solicitação com a IA. Por favor, tente novamente."

    async def generate_project_outline(self, user_prompt: str) -> Dict[str, Any]:
        """
        Gera a estrutura de um projeto PRONAS/PCD com base em um prompt do usuário,
        utilizando a base de conhecimento para garantir conformidade.

        Args:
            user_prompt: A descrição do projeto desejado pelo usuário.
                         Ex: "Gerar um projeto de reabilitação para crianças com paralisia cerebral
                         em Brasília, com orçamento de 500 mil reais e duração de 24 meses."

        Returns:
            Um dicionário representando a estrutura do projeto.
        """
        logger.info(f"Iniciando geração de projeto para o prompt: '{user_prompt[:50]}...'")
        
        # 1. Buscar contexto relevante para a criação de projetos
        search_query = f"Diretrizes para criação de projetos PRONAS/PCD relacionados a: {user_prompt}"
        relevant_docs = await self.vector_service.find_similar_chunks(search_query, limit=7)
        
        context = "\n\n".join([doc[0] for doc in relevant_docs])
        
        # 2. Construir o prompt para o Gemini
        prompt = f"""
        Você é um especialista na elaboração de projetos para o PRONAS/PCD. Sua tarefa é criar
        a estrutura de um novo projeto com base na solicitação do usuário e nas diretrizes
        oficiais extraídas do contexto.

        **Contexto (Diretrizes e exemplos de documentos oficiais):**
        ---
        {context}
        ---

        **Solicitação do Usuário:**
        "{user_prompt}"

        **Instruções:**
        - Crie uma estrutura de projeto em formato JSON, seguindo estritamente o schema abaixo.
        - Preencha todos os campos do JSON com informações detalhadas, coerentes e realistas,
          baseando-se tanto na solicitação do usuário quanto nas diretrizes do contexto.
        - Os campos "justificativa", "objetivos" e "metodologia" devem ser particularmente detalhados.
        - Seja criativo, mas mantenha-se em conformidade com as regras do PRONAS/PCD mencionadas no contexto.
        - Não inclua `id`, `created_at` ou `updated_at` no JSON.

        **Schema JSON de Saída (use exatamente esta estrutura):**
        {{
          "title": "string (título claro e objetivo)",
          "description": "string (descrição resumida do projeto)",
          "status": "draft",
          "type": "string (um de: 'assistencial', 'pesquisa', 'desenvolvimento_tecnologico', 'capacitacao', 'infraestrutura')",
          "institution_id": "integer (deixe como 0 se não especificado)",
          "start_date": "string (formato AAAA-MM-DD, data futura)",
          "end_date": "string (formato AAAA-MM-DD, data futura)",
          "total_budget": "number (orçamento total em BRL)",
          "pronas_funding": "number (valor solicitado ao PRONAS)",
          "own_funding": "number (valor de contrapartida)",
          "created_by": "string (UUID v4 de exemplo, como '00000000-0000-0000-0000-000000000000')"
        }}

        **JSON de Saída:**
        """

        logger.info("Enviando prompt de geração de projeto para o Gemini...")

        # 3. Chamar o modelo Gemini e extrair o JSON
        try:
            response = await generative_model.generate_content_async(prompt)
            
            # Limpa a resposta para extrair apenas o bloco JSON
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            
            import json
            project_data = json.loads(json_text)
            
            logger.info(f"Projeto '{project_data.get('title')}' gerado com sucesso pela IA.")
            return project_data

        except Exception as e:
            logger.error(f"Falha ao gerar ou parsear o projeto JSON do Gemini: {e}")
            return {"error": "Não foi possível gerar a estrutura do projeto. Tente refinar sua solicitação."}