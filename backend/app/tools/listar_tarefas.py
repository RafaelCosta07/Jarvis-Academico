import logging
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarefa import StatusTarefa, Tarefa

logger = logging.getLogger(__name__)


class EntradaListarTarefas(BaseModel):
    status: str = "pendente"
    disciplina: str | None = None


def _aplicar_filtros_consulta(stmt: Any, entrada: EntradaListarTarefas) -> Any:
    if entrada.status != "todas":
        stmt = stmt.where(Tarefa.status == StatusTarefa(entrada.status))
    if entrada.disciplina:
        stmt = stmt.where(Tarefa.disciplina == entrada.disciplina)
    return stmt


def _serializar_tarefa(tarefa: Tarefa) -> dict[str, Any]:
    return {
        "id": tarefa.id,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "disciplina": tarefa.disciplina,
        "status": tarefa.status.value,
        "prazo": tarefa.prazo.isoformat() if tarefa.prazo else None,
        "criada_em": tarefa.criada_em.isoformat() + "Z",
        "concluida_em": (tarefa.concluida_em.isoformat() + "Z") if tarefa.concluida_em else None,
    }


async def executar_listar_tarefas(
    input_data: dict[str, Any],
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaListarTarefas(**input_data)
        stmt = _aplicar_filtros_consulta(
            select(Tarefa).order_by(Tarefa.prazo.asc().nulls_last()),
            entrada,
        )
        resultado = await db.execute(stmt)
        tarefas = [_serializar_tarefa(t) for t in resultado.scalars().all()]
        return {
            "tarefas": tarefas,
            "total": len(tarefas),
            "filtros_aplicados": {"status": entrada.status, "disciplina": entrada.disciplina},
        }
    except Exception:
        logger.error("Erro em listar_tarefas: input=%s", input_data, exc_info=True)
        raise
