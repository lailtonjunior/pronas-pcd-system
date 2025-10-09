"""
Script de Ingestão Estruturada de Documentos para a Base de Conhecimento Vetorial
PRONAS/PCD System - IA com RAG (v2.0)
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
import yaml  # Adicionaremos o PyYAML para ler os metadados

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.adapters.database.session import get_async_session
from app.domain.services.vector_service import VectorService

SOURCE_DOCUMENTS_PATH = Path(__file__).parent.parent / "knowledge_base_docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def extract_metadata_and_content(file_path: Path) -> tuple[dict, str]:
    """Extrai metadados (se houver) e conteúdo de um arquivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verifica se há um bloco de metadados no estilo 'frontmatter'
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata_str = parts[1]
            main_content = parts[2]
            try:
                metadata = yaml.safe_load(metadata_str)
                return metadata, main_content.strip()
            except yaml.YAMLError as e:
                print(f"⚠️  Aviso: Erro ao parsear metadados em {file_path.name}: {e}")
    
    return {}, content # Retorna metadados vazios se não encontrar

def extract_text_from_pdf(pdf_path: Path) -> str:
    # (Função permanece a mesma da versão anterior)
    print(f"📄 Lendo o arquivo PDF: {pdf_path.name}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n\n--- Página {page_num + 1} ---\n\n{page_text}"
        return text
    except Exception as e:
        print(f"❌ Erro ao ler o PDF {pdf_path.name}: {e}")
        return ""

def split_text_into_chunks(text: str) -> list[str]:
    # (Função permanece a mesma da versão anterior)
    if not text: return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    print(f"    Dividido em {len(chunks)} pedaços (chunks).")
    return chunks

async def ingest_documents():
    print("🚀 Iniciando o processo de ingestão ESTRUTURADA de documentos...")
    
    async with get_async_session() as session:
        vector_service = VectorService(session)
        
        # Mapeia o nome da pasta para a categoria do ENUM
        category_map = {
            "normas_regulamentares": "norma_regulamentar",
            "projetos_aprovados": "projeto_aprovado",
            "projetos_reprovados": "projeto_reprovado",
            "checklists_diligencia": "checklist_diligencia",
            "glossario": "glossario"
        }

        total_chunks_processed = 0

        for folder_name, category in category_map.items():
            folder_path = SOURCE_DOCUMENTS_PATH / folder_name
            if not folder_path.exists():
                continue

            print(f"\n📁 Processando categoria: '{category}'")
            files_to_process = list(folder_path.glob("*.pdf")) + list(folder_path.glob("*.txt"))

            for file_path in files_to_process:
                metadata = {}
                content = ""
                
                if file_path.suffix == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif file_path.suffix == '.txt':
                    metadata, content = extract_metadata_and_content(file_path)

                chunks = split_text_into_chunks(content)
                if not chunks: continue
                
                print(f"   Vetorizando e salvando {len(chunks)} chunks de '{file_path.name}'...")

                for i, chunk in enumerate(chunks):
                    await asyncio.sleep(1) # Rate limiting
                    
                    embedding = await vector_service.generate_embedding(chunk)
                    
                    if embedding:
                        # Adiciona metadados do arquivo ao chunk
                        chunk_metadata = metadata.copy()
                        chunk_metadata['source_file'] = file_path.name
                        
                        # Modificação para usar o novo método store_embedding
                        await vector_service.store_embedding(
                            source_name=file_path.name,
                            content_chunk=chunk,
                            embedding=embedding,
                            category=category, # Passando a categoria!
                            metadata=chunk_metadata
                        )
                        print(f"     -> Chunk {i+1}/{len(chunks)} salvo na categoria '{category}'.")
                        total_chunks_processed += 1
                    else:
                        print(f"     -> Falha ao vetorizar o chunk {i+1}/{len(chunks)}.")

    print(f"\n🎉 Processo de ingestão estruturada concluído! Total de chunks salvos: {total_chunks_processed}")

if __name__ == "__main__":
    # Adicionar PyYAML aos requirements.txt
    # pip install PyYAML
    asyncio.run(ingest_documents())