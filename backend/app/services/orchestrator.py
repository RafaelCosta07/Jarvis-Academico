from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING, Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

if TYPE_CHECKING:
    from app.services.rag_service import RAGService

from app.tools import TOOLS_EXECUTORES, TOOLS_REGISTRY
from app.utils.logger import registrar_chamada_tool

logger = logging.getLogger(__name__)

_MAX_ITERACOES = 10
_servidor_suporta_tools: bool = True
_MAX_TOKENS = 350

_SYSTEM_PROMPT = (
    "Você é o JARVIS, assistente acadêmico. "
    "Responda em português, de forma direta e objetiva. "
    "Seja conciso: prefira listas curtas e parágrafos breves. "
    "Não repita a pergunta nem adicione introduções desnecessárias."
)


async def _chamar_llm(cliente: AsyncOpenAI, historico: list[dict[str, Any]]) -> Any:
    global _servidor_suporta_tools
    kwargs: dict[str, Any] = {
        "model": settings.gemma_model,
        "messages": historico,
        "max_tokens": _MAX_TOKENS,
    }
    if _servidor_suporta_tools:
        try:
            return await cliente.chat.completions.create(**kwargs, tools=TOOLS_REGISTRY)
        except Exception as exc:
            if "tool choice" in str(exc).lower() or "400" in str(exc):
                logger.warning("Servidor sem suporte a tool_choice — desativando tools para esta sessão")
                _servidor_suporta_tools = False
            else:
                raise
    return await cliente.chat.completions.create(**kwargs)


def _serializar_mensagem_com_tool_calls(mensagem: Any) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": mensagem.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in mensagem.tool_calls
        ],
    }


async def _executar_tool(
    nome: str,
    argumentos: dict[str, Any],
    db: AsyncSession,
    rag_service: RAGService,
) -> dict[str, Any]:
    executor = TOOLS_EXECUTORES.get(nome)
    if executor is None:
        return {"erro": f"Tool '{nome}' não registrada"}
    inicio = time.monotonic()
    erro: str | None = None
    try:
        resultado: dict[str, Any] = await executor(argumentos, db=db, rag_service=rag_service)
    except Exception as exc:
        erro = str(exc)
        resultado = {"erro": erro}
        logger.error("Falha na execução da tool %s: %s", nome, erro, exc_info=True)
    ms = (time.monotonic() - inicio) * 1000
    registrar_chamada_tool(nome, argumentos, resultado, ms, erro)
    return resultado


async def _processar_tool_calls(
    tool_calls: list[Any],
    historico: list[dict[str, Any]],
    db: AsyncSession,
    rag_service: RAGService,
) -> None:
    for chamada in tool_calls:
        nome = chamada.function.name
        argumentos = json.loads(chamada.function.arguments)
        resultado = await _executar_tool(nome, argumentos, db, rag_service)
        historico.append({
            "role": "tool",
            "tool_call_id": chamada.id,
            "content": json.dumps(resultado, ensure_ascii=False, default=str),
        })


async def processar_mensagem(
    messages: list[dict[str, Any]],
    db: AsyncSession,
    rag_service: RAGService,
    cliente_llm: AsyncOpenAI,
) -> str:
    tem_system = messages and messages[0].get("role") == "system"
    historico = list(messages) if tem_system else [{"role": "system", "content": _SYSTEM_PROMPT}, *messages]
    for _ in range(_MAX_ITERACOES):
        resposta = await _chamar_llm(cliente_llm, historico)
        mensagem = resposta.choices[0].message
        if not mensagem.tool_calls:
            return mensagem.content or ""
        historico.append(_serializar_mensagem_com_tool_calls(mensagem))
        await _processar_tool_calls(mensagem.tool_calls, historico, db, rag_service)
    logger.warning("Limite de %d iterações atingido no agent loop", _MAX_ITERACOES)
    return "Não consegui concluir o processamento dentro do limite de iterações."
