-- database/migrations/002_add_vector_knowledge_base.sql (Versão Atualizada)

-- Habilita a extensão pgvector no banco de dados
CREATE EXTENSION IF NOT EXISTS vector;

-- (NOVO) Cria um ENUM para as categorias de conhecimento
CREATE TYPE public.knowledge_category AS ENUM (
    'norma_regulamentar',
    'projeto_aprovado',
    'projeto_reprovado',
    'checklist_diligencia',
    'glossario',
    'modelo_documento',
    'inovacao_aprovada'
);

-- Altera a tabela para adicionar a nova coluna
ALTER TABLE public.knowledge_base
ADD COLUMN category public.knowledge_category NOT NULL DEFAULT 'norma_regulamentar';

-- Adiciona um comentário para clareza
COMMENT ON COLUMN public.knowledge_base.category IS 'Categoriza o tipo de conhecimento para busca semântica direcionada.';

-- (Opcional, mas recomendado) Cria um índice combinado para buscas mais rápidas
CREATE INDEX ON public.knowledge_base (category);