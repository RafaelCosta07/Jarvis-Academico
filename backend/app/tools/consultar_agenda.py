import logging
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evento import Evento

logger = logging.getLogger(__name__)


class EntradaConsultarAgenda(BaseModel):
    periodo: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None

    @model_validator(mode="after")
    def validar_presenca_de_filtro(self) -> "EntradaConsultarAgenda":
        if self.periodo is None and self.data_inicio is None:
            raise ValueError("Informe 'periodo' ou 'data_inicio'")
        return self


def _calcular_intervalo(entrada: EntradaConsultarAgenda) -> tuple[date, date]:
    hoje = date.today()
    if entrada.periodo == "hoje":
        return hoje, hoje
    if entrada.periodo == "amanha":
        amanha = hoje + timedelta(days=1)
        return amanha, amanha
    if entrada.periodo == "semana":
        return hoje, hoje + timedelta(days=7)
    if entrada.periodo == "mes":
        return hoje, hoje + timedelta(days=30)
    inicio = date.fromisoformat(entrada.data_inicio)  # type: ignore[arg-type]
    fim = date.fromisoformat(entrada.data_fim) if entrada.data_fim else inicio
    return inicio, fim


def _formatar_descricao_periodo(entrada: EntradaConsultarAgenda, inicio: date, fim: date) -> str:
    if entrada.periodo == "hoje":
        return f"Hoje ({inicio.strftime('%d/%m/%Y')})"
    if entrada.periodo == "amanha":
        return f"Amanhã ({inicio.strftime('%d/%m/%Y')})"
    if entrada.periodo == "semana":
        return f"Próximos 7 dias ({inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')})"
    if entrada.periodo == "mes":
        return f"Próximos 30 dias ({inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')})"
    return f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"


def _serializar_evento(evento: Evento) -> dict[str, Any]:
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "descricao": evento.descricao,
        "data": evento.data.isoformat(),
        "hora_inicio": evento.hora_inicio.strftime("%H:%M") if evento.hora_inicio else None,
        "hora_fim": evento.hora_fim.strftime("%H:%M") if evento.hora_fim else None,
        "tipo": evento.tipo.value,
        "local": evento.local,
    }


async def executar_consultar_agenda(
    input_data: dict[str, Any],
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaConsultarAgenda(**input_data)
        inicio, fim = _calcular_intervalo(entrada)
        stmt = (
            select(Evento)
            .where(Evento.data >= inicio, Evento.data <= fim)
            .order_by(Evento.data, Evento.hora_inicio)
        )
        resultado = await db.execute(stmt)
        eventos = [_serializar_evento(e) for e in resultado.scalars().all()]
        return {
            "eventos": eventos,
            "total": len(eventos),
            "periodo_consultado": _formatar_descricao_periodo(entrada, inicio, fim),
        }
    except Exception:
        logger.error("Erro em consultar_agenda: input=%s", input_data, exc_info=True)
        raise
