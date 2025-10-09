"""
Endpoints for AI Functionality
"""
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.domain.services.ai_engine import PronasAIEngine

router = APIRouter()

@router.post("/query")
async def ask_ai(
    query: str = Body(..., embed=True, description="A pergunta para a IA"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para fazer perguntas à IA, que responderá com base nos documentos.
    """
    try:
        ai_engine = PronasAIEngine(session)
        answer = await ai_engine.answer_query_with_context(query)
        return {"answer": answer}
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/generate-project")
async def generate_project(
    prompt: str = Body(..., embed=True, description="Descrição do projeto a ser gerado"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para solicitar a geração de uma estrutura de projeto via IA.
    """
    try:
        ai_engine = PronasAIEngine(session)
        project_outline = await ai_engine.generate_project_outline(prompt)
        return project_outline
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))