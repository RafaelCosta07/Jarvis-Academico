import logging
from datetime import date, time
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evento import TipoEvento
from app.schemas.evento import EventoCreate
from app.services import agenda_service

logger = logging.getLogger(__name__)


class EntradaAdicionarEvento(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    data: str
    tipo: str
    hora_inicio: str | None = None
    hora_fim: str | None = None
    local: str | None = Field(default=None, max_length=200)
    descricao: str | None = Field(default=None, max_length=1000)


def _parse_hora(hora_str: str | None) -> time | None:
    return time.fromisoformat(hora_str) if hora_str else None


def _construir_payload(entrada: EntradaAdicionarEvento) -> EventoCreate:
    return EventoCreate(
        titulo=entrada.titulo,
        data=date.fromisoformat(entrada.data),
        tipo=TipoEvento(entrada.tipo),
        hora_inicio=_parse_hora(entrada.hora_inicio),
        hora_fim=_parse_hora(entrada.hora_fim),
        local=entrada.local,
        descricao=entrada.descricao,
    )


def _serializar(evento: Any) -> dict[str, Any]:
    return {
        "id": str(evento.id),
        "titulo": evento.titulo,
        "data": str(evento.data),
        "hora_inicio": evento.hora_inicio.strftime("%H:%M") if evento.hora_inicio else None,
        "hora_fim": evento.hora_fim.strftime("%H:%M") if evento.hora_fim else None,
        "tipo": evento.tipo.value,
        "local": evento.local,
    }


async def executar_adicionar_evento(
    input_data: dict[str, Any],
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaAdicionarEvento(**input_data)
        payload = _construir_payload(entrada)
        evento = await agenda_service.criar_evento(db, payload)
        logger.info("Evento criado via tool: id=%s titulo=%s data=%s", evento.id, evento.titulo, evento.data)
        return {
            "sucesso": True,
            "evento_id": str(evento.id),
            "mensagem": f"Evento '{entrada.titulo}' adicionado para {entrada.data}.",
            "evento": _serializar(evento),
        }
    except Exception:
        logger.error("Erro em adicionar_evento: input=%s", input_data, exc_info=True)
        raise
