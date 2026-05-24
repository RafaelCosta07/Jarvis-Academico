import logging
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarefa import StatusTarefa, Tarefa
from app.schemas.tarefa import TarefaCreate

logger = logging.getLogger(__name__)


async def listar_tarefas(
    db: AsyncSession,
    status: StatusTarefa | None = None,
    disciplina: str | None = None,
) -> list[Tarefa]:
    try:
        stmt = select(Tarefa)
        if status is not None:
            stmt = stmt.where(Tarefa.status == status)
        if disciplina is not None:
            stmt = stmt.where(Tarefa.disciplina == disciplina)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    except Exception:
        logger.exception("Erro ao listar tarefas: status=%s disciplina=%s", status, disciplina)
        raise


async def criar_tarefa(db: AsyncSession, payload: TarefaCreate) -> Tarefa:
    try:
        tarefa = Tarefa(**payload.model_dump())
        db.add(tarefa)
        await db.flush()
        await db.refresh(tarefa)
        logger.info("Tarefa criada: id=%s titulo=%s", tarefa.id, tarefa.titulo)
        return tarefa
    except Exception:
        logger.exception("Erro ao criar tarefa: titulo=%s", payload.titulo)
        raise


async def concluir_tarefa(db: AsyncSession, tarefa_id: str) -> Tarefa:
    resultado = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = resultado.scalar_one_or_none()
    if tarefa is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.status == StatusTarefa.concluida:
        raise HTTPException(status_code=409, detail="Tarefa já está concluída")
    try:
        tarefa.status = StatusTarefa.concluida
        tarefa.concluida_em = datetime.utcnow()
        await db.flush()
        await db.refresh(tarefa)
        logger.info("Tarefa concluída: id=%s", tarefa_id)
        return tarefa
    except Exception:
        logger.exception("Erro ao concluir tarefa: id=%s", tarefa_id)
        raise
