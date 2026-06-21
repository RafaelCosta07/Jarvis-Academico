from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.learning_service import LearningService
from app.services.llm_client import criar_cliente_llm

if TYPE_CHECKING:
    from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class EntradaGerarExercicios(BaseModel):
    topico: str = Field(min_length=3, max_length=300)
    top_k: int = Field(default=10, ge=3, le=15)


async def executar_gerar_exercicios(
    input_data: dict[str, Any],
    rag_service: RAGService,
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaGerarExercicios(**input_data)
        logger.info(json.dumps({"tool": "gerar_exercicios", "topico": entrada.topico}, ensure_ascii=False))
        servico = LearningService(criar_cliente_llm(), rag_service, db)
        exercicios = await servico.gerar_exercicios(entrada.topico, entrada.top_k)
        return {"exercicios": exercicios, "topico": entrada.topico}
    except Exception:
        logger.error("Erro em gerar_exercicios: input=%s", input_data, exc_info=True)
        raise
