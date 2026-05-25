from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

if TYPE_CHECKING:
    from app.services.rag_service import RAGService

from app.tools import TOOLS_EXECUTORES
from app.utils.logger import registrar_chamada_tool

logger = logging.getLogger(__name__)

_MAX_ITERACOES = 8
_MAX_TOKENS = 512
_REACT_PATTERN = re.compile(
    r'TOOL:\s*(\w+)\s+INPUT:\s*(\{.*?\})',
    re.DOTALL | re.IGNORECASE,
)


def _construir_system_prompt(data_hoje: str) -> str:
    return f"""Você é o JARVIS, assistente acadêmico inteligente. Hoje é {data_hoje}.

Você tem acesso às seguintes ferramentas:
- consultar_agenda: consulta eventos da agenda por período (hoje, amanha, semana, mes) ou data específica
- listar_tarefas: lista tarefas por status (pendente, concluida, todas)
- adicionar_tarefa: cria uma nova tarefa com titulo, descricao, disciplina e prazo opcionais
- adicionar_evento: cria um evento com titulo, data (YYYY-MM-DD), hora_inicio (HH:MM), tipo (aula/prova/prazo/outro) e local opcionais
- concluir_tarefa: marca uma tarefa como concluída pelo tarefa_id
- buscar_material_rag: busca conteúdo nos materiais de estudo por query

COMO USAR AS FERRAMENTAS:
Quando precisar de uma ferramenta, escreva EXATAMENTE neste formato em uma linha separada:
TOOL: nome_da_ferramenta
INPUT: {{"chave": "valor"}}

Exemplos corretos:
TOOL: consultar_agenda
INPUT: {{"periodo": "hoje"}}

TOOL: listar_tarefas
INPUT: {{"status": "pendente"}}

TOOL: adicionar_evento
INPUT: {{"titulo": "Aula de Cálculo II", "data": "2026-05-26", "hora_inicio": "14:00", "tipo": "aula", "local": "Sala B-204"}}

TOOL: buscar_material_rag
INPUT: {{"query": "regressão logística", "top_k": 5}}

REGRAS IMPORTANTES:

1. PERGUNTAS TÉCNICAS ou ACADÊMICAS — use buscar_material_rag SEMPRE:
   Qualquer pergunta sobre conceitos, algoritmos, teorias, técnicas de IA,
   machine learning, estatística, redes neurais, NLP ou qualquer conteúdo
   de estudo DEVE usar buscar_material_rag antes de responder.
   NUNCA responda questões técnicas de memória — busque nos documentos primeiro.
   Exemplos que SEMPRE requerem buscar_material_rag:
   - "O que é regressão logística?" → buscar_material_rag(query="regressão logística")
   - "Explique redes neurais" → buscar_material_rag(query="redes neurais")
   - "Como funciona backpropagation?" → buscar_material_rag(query="backpropagation")
   - "O que são embeddings?" → buscar_material_rag(query="embeddings")

2. DADOS DE AGENDA ou TAREFAS — use a ferramenta correspondente imediatamente.
   Nunca responda de memória — consulte a ferramenta primeiro.

3. Após receber o resultado da ferramenta, responda ao usuário em português natural
   e amigável. Nunca mostre o resultado bruto JSON ao usuário.
   Ao usar buscar_material_rag, cite o nome do arquivo fonte na resposta.

4. Para DATAS: hoje é {data_hoje}. Calcule datas relativas corretamente:
   - "amanhã" = dia seguinte a {data_hoje}
   - "esta semana" = use periodo="semana"
   - "próxima segunda" = calcule a data YYYY-MM-DD correta
   Sempre converta para YYYY-MM-DD antes de chamar qualquer tool.

5. CRIAÇÃO AUTOMÁTICA — identifique pelo contexto e aja sem perguntar:

   → É um EVENTO (use adicionar_evento) quando a frase contém:
     "aula", "prova", "reunião", "encontro", "apresentação", "entrega às [hora]",
     qualquer coisa com data + horário específico.
     Exemplos: "adiciona aula de Cálculo amanhã às 14h" → adicionar_evento
               "tenho reunião sexta às 10h" → adicionar_evento
               "marca prova de IA dia 30" → adicionar_evento

   → É uma TAREFA (use adicionar_tarefa) quando a frase contém:
     "tarefa", "lembrete", "preciso", "estudar", "fazer", "entregar" (sem horário),
     qualquer coisa a ser feita sem hora específica.
     Exemplos: "adiciona tarefa de estudar capítulo 3" → adicionar_tarefa
               "lembra de revisar as anotações" → adicionar_tarefa
               "preciso fazer a lista de exercícios" → adicionar_tarefa

   → SOMENTE pergunte "é evento ou tarefa?" se a frase for genuinamente ambígua
     e não contiver nenhuma das palavras acima. Isso deve ser raro.

6. Após criar evento ou tarefa, confirme ao usuário de forma natural.
   Exemplo: "Pronto! Adicionei a aula de Cálculo II na sua agenda para amanhã às 14h."
   Exemplo: "Feito! Criei a tarefa 'Estudar capítulo 3' na sua lista."

7. Use apenas UMA ferramenta por vez. Aguarde o resultado antes de continuar.

8. Responda sempre em português brasileiro de forma natural e prestativa."""


def _extrair_chamada_tool(texto: str) -> tuple[str, dict[str, Any]] | None:
    match = _REACT_PATTERN.search(texto)
    if not match:
        return None
    nome_tool = match.group(1).strip()
    try:
        input_dict: dict[str, Any] = json.loads(match.group(2))
        return nome_tool, input_dict
    except json.JSONDecodeError:
        logger.warning("JSON inválido na chamada ReAct: %s", match.group(2))
        return None


async def _executar_tool_react(
    nome: str,
    inputs: dict[str, Any],
    db: AsyncSession,
    rag_service: RAGService,
) -> dict[str, Any]:
    executor = TOOLS_EXECUTORES.get(nome)
    if executor is None:
        logger.warning("Tool desconhecida no ReAct: %s", nome)
        return {"erro": f"Ferramenta '{nome}' não encontrada"}
    inicio = time.monotonic()
    erro: str | None = None
    try:
        resultado: dict[str, Any] = await executor(inputs, db=db, rag_service=rag_service)
    except Exception as exc:
        erro = str(exc)
        resultado = {"erro": erro}
        logger.error("Falha na tool ReAct %s: %s", nome, erro, exc_info=True)
    ms = (time.monotonic() - inicio) * 1000
    registrar_chamada_tool(nome, inputs, resultado, ms, erro)
    return resultado


def _registrar_resultado_historico(
    historico: list[dict[str, Any]],
    conteudo: str,
    nome_tool: str,
    resultado: dict[str, Any],
) -> None:
    historico.append({"role": "assistant", "content": conteudo})
    historico.append({
        "role": "user",
        "content": f"RESULTADO DA FERRAMENTA {nome_tool}:\n{json.dumps(resultado, ensure_ascii=False, indent=2)}",
    })


async def processar_mensagem(
    messages: list[dict[str, Any]],
    db: AsyncSession,
    rag_service: RAGService,
    cliente_llm: AsyncOpenAI,
) -> str:
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    historico: list[dict[str, Any]] = [
        {"role": "system", "content": _construir_system_prompt(data_hoje)},
        *messages,
    ]
    for iteracao in range(_MAX_ITERACOES):
        resposta = await cliente_llm.chat.completions.create(
            model=settings.gemma_model,
            messages=historico,
            max_tokens=_MAX_TOKENS,
            temperature=0.1,
        )
        conteudo = resposta.choices[0].message.content or ""
        logger.debug("LLM iter %d: %s", iteracao, conteudo[:400])
        chamada = _extrair_chamada_tool(conteudo)
        if chamada is None:
            return conteudo.strip()
        nome_tool, input_tool = chamada
        logger.info("ReAct tool detectada: %s | inputs: %s", nome_tool, input_tool)
        resultado = await _executar_tool_react(nome_tool, input_tool, db, rag_service)
        _registrar_resultado_historico(historico, conteudo, nome_tool, resultado)
    logger.warning("Agent loop ReAct atingiu máximo de %d iterações", _MAX_ITERACOES)
    return "Não consegui concluir o processamento dentro do limite de iterações."
