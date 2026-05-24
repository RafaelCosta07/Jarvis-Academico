import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarefa import StatusTarefa, Tarefa

logger = logging.getLogger(__name__)


class EntradaConcluirTarefa(BaseModel):
    tarefa_id: str


def _resultado_tarefa_nao_encontrada(tarefa_id: str) -> dict[str, Any]:
    return {
        "sucesso": False,
        "tarefa_id": tarefa_id,
        "titulo": "",
        "mensagem": "Erro: Tarefa não encontrada ou já está concluída",
        "concluida_em": None,
    }


async def _buscar_tarefa_pendente(tarefa_id: str, db: AsyncSession) -> Tarefa | None:
    stmt = select(Tarefa).where(
        Tarefa.id == tarefa_id,
        Tarefa.status == StatusTarefa.pendente,
    )
    resultado = await db.execute(stmt)
    return resultado.scalar_one_or_none()


async def executar_concluir_tarefa(
    input_data: dict[str, Any],
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaConcluirTarefa(**input_data)
        tarefa = await _buscar_tarefa_pendente(entrada.tarefa_id, db)
        if tarefa is None:
            return _resultado_tarefa_nao_encontrada(entrada.tarefa_id)
        agora = datetime.now(timezone.utc).replace(tzinfo=None)
        tarefa.status = StatusTarefa.concluida
        tarefa.concluida_em = agora
        await db.flush()
        logger.info("Tarefa concluída: id=%s titulo=%s", tarefa.id, tarefa.titulo)
        return {
            "sucesso": True,
            "tarefa_id": tarefa.id,
            "titulo": tarefa.titulo,
            "mensagem": "Tarefa marcada como concluída com sucesso",
            "concluida_em": agora.isoformat() + "Z",
        }
    except Exception:
        logger.error("Erro em concluir_tarefa: id=%s", input_data.get("tarefa_id"), exc_info=True)
        raise
