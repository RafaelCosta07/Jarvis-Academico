from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
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


def _obter_rag_service() -> RAGService:
    global _rag_service_singleton
    if _rag_service_singleton is None:
        try:
            from app.services.rag_service import criar_rag_service  # lazy — evita import de torch no startup
            servico = criar_rag_service()
            servico.carregar_indice(settings.documents_dir)
            _rag_service_singleton = servico
        except Exception:
            logger.warning("RAGService indisponível — usando serviço nulo (sentence_transformers ausente?)")
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
