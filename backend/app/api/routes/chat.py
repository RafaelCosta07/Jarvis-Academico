from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.chat import ChatRequest
from app.services.llm_client import criar_cliente_llm
from app.services.orchestrator import processar_mensagem

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()

_rag_service_singleton: RAGService | None = None


class _NullRAGService:
    """Null Object para quando sentence_transformers não está disponível."""

    def recuperar_chunks(self, *_args: Any, **_kwargs: Any) -> list:
        return []


def _documentos_atuais(docs_dir: Path) -> list[str]:
    if not docs_dir.exists():
        return []
    return sorted(f for f in os.listdir(docs_dir) if f.lower().endswith(('.pdf', '.txt', '.md')))


def _fontes_indexadas(metadata_path: Path) -> list[str]:
    if not metadata_path.exists():
        return []
    with open(metadata_path, encoding='utf-8') as f:
        meta: list[dict[str, str]] = json.load(f)
    return sorted({c['fonte'] for c in meta})


def _indice_desatualizado(index_path: Path, metadata_path: Path, docs_dir: Path) -> bool:
    if not index_path.exists():
        return True
    return _fontes_indexadas(metadata_path) != _documentos_atuais(docs_dir)


def inicializar_rag_startup() -> None:
    global _rag_service_singleton
    index_path = Path(settings.faiss_index_path)
    metadata_path = index_path.parent / 'processed' / 'chunks_metadata.json'
    docs_dir = Path(settings.documents_dir)
    try:
        from app.services.rag_service import criar_rag_service
        rag = criar_rag_service()
        if _indice_desatualizado(index_path, metadata_path, docs_dir):
            n = len(_documentos_atuais(docs_dir))
            logger.info("Índice FAISS desatualizado — reconstruindo com %d documentos...", n)
            rag.construir_indice(str(docs_dir))
        else:
            rag.carregar_indice(str(docs_dir))
        _rag_service_singleton = rag
        logger.info("RAGService pronto.")
    except Exception:
        logger.exception("Falha ao inicializar RAG no startup — RAG desativado.")
        _rag_service_singleton = _NullRAGService()  # type: ignore[assignment]


def _obter_rag_service() -> RAGService:
    global _rag_service_singleton
    if _rag_service_singleton is None:
        try:
            from app.services.rag_service import criar_rag_service  # lazy — evita import de torch no startup
            servico = criar_rag_service()
            servico.carregar_indice(settings.documents_dir)
            logger.info("RAGService inicializado com índice FAISS.")
            _rag_service_singleton = servico
        except Exception:
            logger.exception("RAGService falhou ao inicializar — RAG desativado, busca retornará vazio.")
            _rag_service_singleton = _NullRAGService()  # type: ignore[assignment]
    return _rag_service_singleton


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_obter_rag_service),
    cliente_llm: AsyncOpenAI = Depends(criar_cliente_llm),
) -> StreamingResponse:
    async def _stream() -> AsyncGenerator[str, None]:
        try:
            resposta = await processar_mensagem(
                payload.messages,
                db=db,
                rag_service=rag_service,
                cliente_llm=cliente_llm,
            )
            yield f'data: {json.dumps({"type": "token", "content": resposta}, ensure_ascii=False)}\n\n'
        except Exception:
            logger.exception("Erro ao processar requisição de chat")
            yield f'data: {json.dumps({"type": "error", "content": "Erro interno no servidor"})}\n\n'
        finally:
            yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(_stream(), media_type="text/event-stream")
