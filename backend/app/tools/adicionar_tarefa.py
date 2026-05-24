import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarefa import Tarefa

logger = logging.getLogger(__name__)


class EntradaAdicionarTarefa(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str | None = Field(default=None, max_length=1000)
    disciplina: str | None = Field(default=None, max_length=100)
    prazo: str | None = None


def _construir_objeto_tarefa(entrada: EntradaAdicionarTarefa) -> Tarefa:
    prazo_date = date.fromisoformat(entrada.prazo) if entrada.prazo else None
    return Tarefa(
        titulo=entrada.titulo,
        descricao=entrada.descricao,
        disciplina=entrada.disciplina,
        prazo=prazo_date,
    )


def _dados_tarefa_criada(tarefa: Tarefa) -> dict[str, Any]:
    return {
        "id": tarefa.id,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "disciplina": tarefa.disciplina,
        "status": tarefa.status.value,
        "prazo": tarefa.prazo.isoformat() if tarefa.prazo else None,
        "criada_em": tarefa.criada_em.isoformat() + "Z",
        "concluida_em": None,
    }


async def executar_adicionar_tarefa(
    input_data: dict[str, Any],
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaAdicionarTarefa(**input_data)
        tarefa = _construir_objeto_tarefa(entrada)
        db.add(tarefa)
        await db.flush()
        await db.refresh(tarefa)
        logger.info("Tarefa criada: id=%s titulo=%s", tarefa.id, tarefa.titulo)
        return {
            "sucesso": True,
            "tarefa_id": tarefa.id,
            "mensagem": f"Tarefa '{tarefa.titulo}' criada com sucesso",
            "tarefa": _dados_tarefa_criada(tarefa),
        }
    except Exception:
        logger.error("Erro em adicionar_tarefa: input=%s", input_data, exc_info=True)
        raise
