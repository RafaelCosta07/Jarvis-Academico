import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_LOG_FILE = os.getenv("LOG_FILE", "logs/tool_calls.jsonl")
_COR_OK = "\033[32m"
_COR_ERRO = "\033[31m"
_RESET = "\033[0m"


def _montar_entrada_jsonl(
    tool: str,
    input_data: dict[str, Any],
    output: dict[str, Any] | None,
    execution_time_ms: float,
    erro: str | None,
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool": tool,
        "input": input_data,
        "output": output,
        "execution_time_ms": round(execution_time_ms, 2),
        "sucesso": erro is None,
        "erro": erro,
    }


def _gravar_jsonl(entrada: dict[str, Any]) -> None:
    Path(_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(_LOG_FILE, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(entrada, ensure_ascii=False, default=str) + "\n")


def _imprimir_terminal(tool: str, execution_time_ms: float, sucesso: bool) -> None:
    cor = _COR_OK if sucesso else _COR_ERRO
    status = "OK" if sucesso else "ERRO"
    print(
        f"{cor}[TOOL] {tool} -> {status} ({execution_time_ms:.0f}ms){_RESET}",
        file=sys.stdout,
        flush=True,
    )


def registrar_chamada_tool(
    tool: str,
    input_data: dict[str, Any],
    output: dict[str, Any] | None,
    execution_time_ms: float,
    erro: str | None = None,
) -> None:
    entrada = _montar_entrada_jsonl(tool, input_data, output, execution_time_ms, erro)
    try:
        _gravar_jsonl(entrada)
    except Exception:
        logger.error("Falha ao gravar log JSONL: tool=%s", tool, exc_info=True)
    _imprimir_terminal(tool, execution_time_ms, erro is None)
