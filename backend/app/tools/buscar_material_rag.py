from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class EntradaBuscarMaterialRag(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    documento: str | None = None
    threshold: float = Field(default=0.0, ge=0.0, le=1.0)


def _filtrar_por_documento(chunks: list[dict[str, Any]], documento: str | None) -> list[dict[str, Any]]:
    if not documento:
        return chunks
    return [c for c in chunks if c.get("fonte") == documento]


async def executar_buscar_material_rag(
    input_data: dict[str, Any],
    rag_service: RAGService,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaBuscarMaterialRag(**input_data)
        inicio = time.monotonic()
        chunks_brutos = rag_service.recuperar_chunks(
            query=entrada.query,
            top_k=entrada.top_k,
            threshold=entrada.threshold,
        )
        chunks = _filtrar_por_documento(chunks_brutos, entrada.documento)
        tempo_ms = (time.monotonic() - inicio) * 1000
        return {
            "chunks": chunks,
            "query": entrada.query,
            "total_recuperado": len(chunks),
            "tempo_busca_ms": round(tempo_ms, 2),
        }
    except Exception:
        logger.error(
            "Erro em buscar_material_rag: query=%s",
            str(input_data.get("query", ""))[:50],
            exc_info=True,
        )
        raise
