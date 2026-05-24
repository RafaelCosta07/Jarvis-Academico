import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.tarefa import StatusTarefa
from app.schemas.tarefa import TarefaCreate, TarefaRead
from app.services import task_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tasks", response_model=list[TarefaRead])
async def listar_tarefas(
    status: StatusTarefa | None = Query(default=None),
    disciplina: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[TarefaRead]:
    try:
        return await task_service.listar_tarefas(db, status=status, disciplina=disciplina)
    except Exception:
        logger.exception("Erro ao listar tarefas")
        raise


@router.post("/tasks", response_model=TarefaRead, status_code=201)
async def criar_tarefa(
    payload: TarefaCreate,
    db: AsyncSession = Depends(get_db),
) -> TarefaRead:
    try:
        return await task_service.criar_tarefa(db, payload)
    except Exception:
        logger.exception("Erro ao criar tarefa: titulo=%s", payload.titulo)
        raise


@router.patch("/tasks/{tarefa_id}/concluir", response_model=TarefaRead)
async def concluir_tarefa_endpoint(
    tarefa_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TarefaRead:
    try:
        return await task_service.concluir_tarefa(db, str(tarefa_id))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erro ao concluir tarefa: id=%s", tarefa_id)
        raise
