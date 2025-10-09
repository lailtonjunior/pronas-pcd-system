"""
Vector Service - PRONAS/PCD
Serviço responsável pela vetorização de documentos e busca semântica
utilizando a API do Google Gemini e pgvector.
"""

import os
import google.generativeai as genai
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pgvector.sqlalchemy import Vector

from app.core.config.settings import get_settings

settings = get_settings()

# Configura a API do Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print("✅ API do Google Gemini configurada com sucesso.")
except Exception as e:
    print(f"❌ Erro ao configurar a API do Gemini: {e}")
    # Em um ambiente de produção, você pode querer lançar uma exceção aqui
    # raise RuntimeError("Falha ao configurar a API do Gemini. Verifique a chave de API.") from e


class VectorService:
    """
    Orquestra a geração de embeddings e a busca por similaridade.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        # Modelo de embedding do Google otimizado para RAG
        self.embedding_model = 'models/embedding-001'

    async def generate_embedding(self, text_chunk: str) -> List[float]:
        """
        Gera o vetor (embedding) para um pedaço de texto usando a API do Gemini.

        Args:
            text_chunk: O texto a ser vetorizado.

        Returns:
            Uma lista de floats representando o vetor.
        """
        try:
            result = await genai.embed_content_async(
                model=self.embedding_model,
                content=text_chunk,
                task_type="RETRIEVAL_DOCUMENT",
                title="Documento do PRONAS/PCD"
            )
            return result['embedding']
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            # Lidar com erros de API, como limites de taxa ou falhas de autenticação
            return []

    async def store_embedding(
        self,
        source_name: str,
        content_chunk: str,
        embedding: List[float],
        category: str, # Adicionar categoria
        metadata: dict = None
    ):
        query = text(
            """
            INSERT INTO knowledge_base (source_name, content_chunk, embedding, category, metadata)
            VALUES (:source_name, :content_chunk, :embedding, :category, :metadata)
            """
        )
        await self.session.execute(
            query,
            {
                "source_name": source_name,
                "content_chunk": content_chunk,
                "embedding": embedding,
                "category": category, # Salvar a categoria
                "metadata": json.dumps(metadata) if metadata else None
            }
        )
        await self.session.commit()

    async def find_similar_chunks(
        self,
        question: str,
        category: str = None, # Adicionar filtro opcional
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        question_embedding = await genai.embed_content_async(
            model=self.embedding_model,
            content=question,
            task_type="RETRIEVAL_QUERY"
        )

        sql_query = """
            SELECT content_chunk, 1 - (embedding <=> :query_embedding) AS similarity
            FROM knowledge_base
            {where_clause}
            ORDER BY similarity DESC
            LIMIT :limit
        """
        
        params = {"query_embedding": question_embedding['embedding'], "limit": limit}
        where_clause = ""
        if category:
            where_clause = "WHERE category = :category"
            params["category"] = category

        query = text(sql_query.format(where_clause=where_clause))
        
        result = await self.session.execute(query, params)
        return result.fetchall()
