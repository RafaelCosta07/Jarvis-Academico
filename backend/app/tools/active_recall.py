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


class EntradaActiveRecall(BaseModel):
    topico: str = Field(min_length=3, max_length=300)
    resposta_usuario: str | None = None
    pergunta: str | None = None
    resposta_referencia: str | None = None
    sessao_id: str | None = None


async def _gerar_pergunta(servico: LearningService, topico: str) -> dict[str, Any]:
    logger.info(json.dumps({"tool": "active_recall", "modo": "gerar_pergunta", "topico": topico}, ensure_ascii=False))
    resultado = await servico.gerar_pergunta_recall(topico)
    return {"modo": "pergunta", **resultado}


async def _avaliar(servico: LearningService, entrada: EntradaActiveRecall) -> dict[str, Any]:
    logger.info(json.dumps({"tool": "active_recall", "modo": "avaliar", "topico": entrada.topico}, ensure_ascii=False))
    avaliacao = await servico.avaliar_resposta_recall(
        pergunta=entrada.pergunta or "",
        resposta_referencia=entrada.resposta_referencia or "",
        resposta_usuario=entrada.resposta_usuario or "",
        sessao_id=entrada.sessao_id,
    )
    return {"modo": "avaliacao", **avaliacao}


async def executar_active_recall(
    input_data: dict[str, Any],
    rag_service: RAGService,
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaActiveRecall(**input_data)
        servico = LearningService(criar_cliente_llm(), rag_service, db)
        if entrada.resposta_usuario is None:
            return await _gerar_pergunta(servico, entrada.topico)
        return await _avaliar(servico, entrada)
    except Exception:
        logger.error("Erro em active_recall: input=%s", input_data, exc_info=True)
        raise
