"""Executa o conjunto de avaliação contra o backend JARVIS.

Para cada pergunta em questions.json: envia ao endpoint /api/chat, captura a
resposta via SSE e correlaciona os chunks recuperados lendo tool_calls.jsonl.
Gera results_intermediate.json (para classificação manual) e eval_log.jsonl.

Uso: python evaluation/evaluate.py  (com o backend rodando na porta 8000)
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

_BASE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BASE_DIR.parent
_QUESTIONS_PATH = _BASE_DIR / "questions.json"
_RESULTS_PATH = _BASE_DIR / "results_intermediate.json"
_EVAL_LOG_PATH = _BASE_DIR / "eval_log.jsonl"
_LOG_PATH = _PROJECT_ROOT / "backend" / "logs" / "tool_calls.jsonl"
_CHAT_URL = "http://localhost:8000/api/chat"
_ESPERA_LOG_S = 2.0


def _carregar_questions(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return dados.get("questions", [])


def _parse_evento_sse(linha: str) -> dict | None:
    if not linha or not linha.startswith("data:"):
        return None
    conteudo = linha[len("data:"):].strip()
    try:
        return json.loads(conteudo)
    except json.JSONDecodeError:
        return None


def _chamar_chat(client: httpx.Client, pergunta: str) -> str:
    body = {"messages": [{"role": "user", "content": pergunta}], "stream": True}
    partes: list[str] = []
    with client.stream("POST", _CHAT_URL, json=body) as resposta:
        resposta.raise_for_status()
        for linha in resposta.iter_lines():
            evento = _parse_evento_sse(linha)
            if evento is None:
                continue
            if evento.get("type") == "token":
                partes.append(evento.get("content", ""))
            elif evento.get("type") == "error":
                raise RuntimeError(evento.get("content", "erro no backend"))
            elif evento.get("type") == "done":
                break
    return "".join(partes)


def _parse_linha_log(linha: str, desde: str) -> list[dict]:
    try:
        registro = json.loads(linha)
    except json.JSONDecodeError:
        return []
    if registro.get("tool") != "buscar_material_rag":
        return []
    if registro.get("timestamp", "") < desde:
        return []
    saida = registro.get("output") or {}
    return saida.get("chunks", [])


def _ler_chunks_recentes(log_path: Path, desde: str) -> list[dict]:
    if not log_path.exists():
        return []
    chunks: list[dict] = []
    with open(log_path, encoding="utf-8") as arquivo:
        for linha in arquivo:
            chunks.extend(_parse_linha_log(linha, desde))
    return chunks


def _simplificar_chunks(chunks: list[dict]) -> list[dict]:
    return [
        {
            "fonte": c.get("fonte"),
            "pagina": c.get("pagina"),
            "score": c.get("score"),
            "conteudo": (c.get("conteudo") or "")[:300],
        }
        for c in chunks
    ]


def _montar_resultado(questao: dict, resposta: str, chunks: list[dict]) -> dict:
    return {
        "question_id": questao["id"],
        "pergunta": questao["pergunta"],
        "chunks_recuperados": _simplificar_chunks(chunks),
        "resposta_gerada": resposta,
        "classificacao": None,
        "justificativa": None,
        "criterios_atendidos": None,
        "criterios_totais": len(questao.get("criterios_avaliacao", [])),
    }


def _processar_pergunta(client: httpx.Client, questao: dict, log_path: Path) -> dict:
    desde = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resposta = _chamar_chat(client, questao["pergunta"])
    time.sleep(_ESPERA_LOG_S)
    chunks = _ler_chunks_recentes(log_path, desde)
    return _montar_resultado(questao, resposta, chunks)


def _processar_pergunta_seguro(client: httpx.Client, questao: dict, log_path: Path) -> dict:
    try:
        return _processar_pergunta(client, questao, log_path)
    except Exception as exc:
        print(f"  ERRO na pergunta {questao['id']}: {exc}")
        return _montar_resultado(questao, f"[ERRO: {exc}]", [])


def _registrar_eval_log(resultado: dict) -> None:
    entrada = {
        "question_id": resultado["question_id"],
        "pergunta": resultado["pergunta"],
        "chunks_recuperados": len(resultado["chunks_recuperados"]),
        "tamanho_resposta": len(resultado["resposta_gerada"]),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(_EVAL_LOG_PATH, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(entrada, ensure_ascii=False) + "\n")


def _salvar_resultados(resultados: list[dict]) -> None:
    payload = {
        "metadata": {
            "evaluated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_questions": len(resultados),
            "correct": None,
            "partial": None,
            "incorrect": None,
            "accuracy": None,
        },
        "results": resultados,
    }
    with open(_RESULTS_PATH, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)


def main() -> None:
    questions = _carregar_questions(_QUESTIONS_PATH)
    total = len(questions)
    resultados: list[dict] = []
    with httpx.Client(timeout=180.0) as client:
        for indice, questao in enumerate(questions, start=1):
            preview = questao["pergunta"][:60]
            print(f'[{indice}/{total}] Processando: "{preview}..."')
            resultado = _processar_pergunta_seguro(client, questao, _LOG_PATH)
            resultados.append(resultado)
            _registrar_eval_log(resultado)
    _salvar_resultados(resultados)
    print(f"\nConcluído: {len(resultados)} perguntas processadas.")
    print(f"Resultados salvos em: {_RESULTS_PATH}")


if __name__ == "__main__":
    main()
