import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evento import Evento, TipoEvento
from app.schemas.evento import EventoCreate

logger = logging.getLogger(__name__)


async def listar_eventos(
    db: AsyncSession,
    tipo: TipoEvento | None = None,
    data: date | None = None,
) -> list[Evento]:
    try:
        stmt = select(Evento)
        if tipo is not None:
            stmt = stmt.where(Evento.tipo == tipo)
        if data is not None:
            stmt = stmt.where(Evento.data == data)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    except Exception:
        logger.exception("Erro ao listar eventos: tipo=%s data=%s", tipo, data)
        raise


async def criar_evento(db: AsyncSession, payload: EventoCreate) -> Evento:
    try:
        evento = Evento(**payload.model_dump())
        db.add(evento)
        await db.flush()
        await db.refresh(evento)
        logger.info("Evento criado: id=%s titulo=%s", evento.id, evento.titulo)
        return evento
    except Exception:
        logger.exception("Erro ao criar evento: titulo=%s", payload.titulo)
        raise
