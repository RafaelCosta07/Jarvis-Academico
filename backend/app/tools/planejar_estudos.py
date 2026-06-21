from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.tarefa import StatusTarefa
from app.services import agenda_service, task_service
from app.services.learning_service import LearningService
from app.services.llm_client import criar_cliente_llm

if TYPE_CHECKING:
    from app.models.evento import Evento
    from app.models.tarefa import Tarefa
    from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

_MAX_TOKENS_PLANO = 1500

_PROMPT_PLANO = """Você é um planejador de estudos acadêmico. Hoje é {hoje}. \
Monte um plano de estudos para os próximos {horizonte} dias.

AGENDA (provas, aulas, prazos):
{eventos}

TAREFAS PENDENTES:
{tarefas}

TÓPICOS COM DIFICULDADE (priorizar revisão):
{topicos_fracos}

MATERIAL DE APOIO DISPONÍVEL:
{contexto}

Critérios de priorização (ordem de peso):
1. Prazos (40%): prazo em ≤24h = URGENTE; ≤48h = ALTA; 3-7 dias = MÉDIA.
2. Dificuldade (30%): priorize os tópicos com dificuldade listados acima.
3. Carga horária (20%): sessões de no máximo 3h; fragmente tarefas grandes.
4. Balanceamento (10%): evite concentrar uma única disciplina no mesmo dia.

Gere um plano dia a dia, com horários sugeridos e o que estudar em cada sessão.
Use o formato DD/MM/AAAA para todas as datas no plano (ex: 21/06/2026).
Responda em português, de forma clara e organizada."""


class EntradaPlanejarEstudos(BaseModel):
    horizonte_dias: int = Field(default=7, ge=1, le=30)
    disciplina: str | None = None
    foco: str | None = None


def _filtrar_eventos_horizonte(eventos: list[Evento], horizonte_dias: int) -> list[Evento]:
    hoje = date.today()
    limite = hoje + timedelta(days=horizonte_dias)
    return [e for e in eventos if hoje <= e.data <= limite]


def _serializar_eventos(eventos: list[Evento]) -> str:
    if not eventos:
        return "Nenhum evento na agenda."
    ordenados = sorted(eventos, key=lambda e: e.data)
    return "\n".join(f"- {e.data.isoformat()} [{e.tipo.value}]: {e.titulo}" for e in ordenados)


def _serializar_tarefas(tarefas: list[Tarefa]) -> str:
    if not tarefas:
        return "Nenhuma tarefa pendente."
    return "\n".join(
        f"- {t.titulo} (disciplina: {t.disciplina or 'N/A'}, "
        f"prazo: {t.prazo.isoformat() if t.prazo else 'sem prazo'})"
        for t in tarefas
    )


def _serializar_topicos_fracos(topicos: dict[str, float]) -> str:
    if not topicos:
        return "Nenhum tópico com dificuldade identificada."
    return "\n".join(f"- {t} (taxa de erro: {int(taxa * 100)}%)" for t, taxa in topicos.items())


def _montar_contexto_rag(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "Nenhum material recuperado."
    return "\n\n".join(c.get("conteudo", "") for c in chunks[:8])


async def _coletar_dados(
    entrada: EntradaPlanejarEstudos, db: AsyncSession, rag_service: RAGService
) -> dict[str, Any]:
    eventos_todos = await agenda_service.listar_eventos(db)
    eventos = _filtrar_eventos_horizonte(eventos_todos, entrada.horizonte_dias)
    tarefas = await task_service.listar_tarefas(
        db, status=StatusTarefa.pendente, disciplina=entrada.disciplina
    )
    servico = LearningService(criar_cliente_llm(), rag_service, db)
    topicos_fracos = await servico.listar_erros_por_topico()
    query = entrada.foco or entrada.disciplina or "plano de estudos"
    chunks = rag_service.recuperar_chunks(query=query, top_k=10)
    return {
        "eventos": eventos,
        "tarefas": tarefas,
        "topicos_fracos": topicos_fracos,
        "chunks": chunks,
        "total_eventos": len(eventos),
        "total_tarefas": len(tarefas),
    }


async def _gerar_plano(entrada: EntradaPlanejarEstudos, dados: dict[str, Any]) -> str:
    prompt = _PROMPT_PLANO.format(
        hoje=date.today().strftime("%d/%m/%Y"),
        horizonte=entrada.horizonte_dias,
        eventos=_serializar_eventos(dados["eventos"]),
        tarefas=_serializar_tarefas(dados["tarefas"]),
        topicos_fracos=_serializar_topicos_fracos(dados["topicos_fracos"]),
        contexto=_montar_contexto_rag(dados["chunks"]),
    )
    resposta = await criar_cliente_llm().chat.completions.create(
        model=settings.gemma_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=_MAX_TOKENS_PLANO,
        temperature=0.4,
    )
    return resposta.choices[0].message.content or ""


def _montar_retorno(
    entrada: EntradaPlanejarEstudos, dados: dict[str, Any], plano: str
) -> dict[str, Any]:
    return {
        "plano": plano,
        "horizonte_dias": entrada.horizonte_dias,
        "total_eventos": dados["total_eventos"],
        "total_tarefas": dados["total_tarefas"],
        "topicos_priorizados": list(dados["topicos_fracos"].keys()),
    }


def _log_entrada(entrada: EntradaPlanejarEstudos) -> None:
    logger.info(json.dumps(
        {"tool": "planejar_estudos", "horizonte_dias": entrada.horizonte_dias,
         "disciplina": entrada.disciplina}, ensure_ascii=False))


def _log_saida(dados: dict[str, Any]) -> None:
    logger.info(json.dumps(
        {"tool": "planejar_estudos", "total_eventos": dados["total_eventos"],
         "total_tarefas": dados["total_tarefas"],
         "topicos_fracos": len(dados["topicos_fracos"])}, ensure_ascii=False))


async def executar_planejar_estudos(
    input_data: dict[str, Any],
    rag_service: RAGService,
    db: AsyncSession,
    **_kwargs: Any,
) -> dict[str, Any]:
    try:
        entrada = EntradaPlanejarEstudos(**input_data)
        _log_entrada(entrada)
        dados = await _coletar_dados(entrada, db, rag_service)
        plano = await _gerar_plano(entrada, dados)
        _log_saida(dados)
        return _montar_retorno(entrada, dados, plano)
    except Exception:
        logger.error("Erro em planejar_estudos: input=%s", input_data, exc_info=True)
        raise
