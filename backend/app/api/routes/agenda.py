import logging
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.evento import TipoEvento
from app.schemas.evento import EventoCreate, EventoRead
from app.services import agenda_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agenda", response_model=list[EventoRead])
async def listar_eventos(
    tipo: TipoEvento | None = Query(default=None),
    data: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[EventoRead]:
    try:
        return await agenda_service.listar_eventos(db, tipo=tipo, data=data)
    except Exception:
        logger.exception("Erro ao listar eventos")
        raise


@router.post("/agenda", response_model=EventoRead, status_code=201)
async def criar_evento(
    payload: EventoCreate,
    db: AsyncSession = Depends(get_db),
) -> EventoRead:
    try:
        return await agenda_service.criar_evento(db, payload)
    except Exception:
        logger.exception("Erro ao criar evento: titulo=%s", payload.titulo)
        raise
