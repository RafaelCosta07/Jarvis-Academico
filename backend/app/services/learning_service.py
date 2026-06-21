from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from openai import AsyncOpenAI
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sessao_recall import SessaoRecall

if TYPE_CHECKING:
    from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

_MAX_TOKENS_EXERCICIOS = 1500
_MAX_TOKENS_RECALL = 512
_LIMITE_TAXA_ERRO = 0.5

_PROMPT_EXERCICIOS = """Com base nestes trechos sobre {topico}:

{contexto}

Gere EXATAMENTE 3 questões de múltipla escolha. Siga o formato abaixo sem nenhum desvio:

---

**Questão 1**

[Enunciado da questão]

a) [Alternativa A]
b) [Alternativa B]
c) [Alternativa C]
d) [Alternativa D]

**Resposta correta:** [letra]) [texto da alternativa correta]
**Explicação:** [por que essa é a resposta]

---

**Questão 2**

[Enunciado da questão]

a) [Alternativa A]
b) [Alternativa B]
c) [Alternativa C]
d) [Alternativa D]

**Resposta correta:** [letra]) [texto da alternativa correta]
**Explicação:** [por que essa é a resposta]

---

**Questão 3**

[Enunciado da questão]

a) [Alternativa A]
b) [Alternativa B]
c) [Alternativa C]
d) [Alternativa D]

**Resposta correta:** [letra]) [texto da alternativa correta]
**Explicação:** [por que essa é a resposta]

---

Baseie as questões apenas no conteúdo acima. Responda em português."""

_PROMPT_PERGUNTA = """Com base neste trecho sobre {topico}:

{contexto}

Gere UMA pergunta de compreensão sobre o conteúdo acima e a resposta esperada.
Responda APENAS com JSON puro, sem markdown, no formato exato:
{{"pergunta": "...", "resposta_referencia": "..."}}"""

_PROMPT_AVALIACAO = """Pergunta feita ao estudante: {pergunta}
Resposta esperada (baseada no material): {referencia}
Resposta do estudante: {resposta}

Avalie a resposta:
- correta: conceito explicado corretamente (aceitar sinônimos e reformulações)
- parcialmente_correta: conceito presente mas incompleto ou impreciso
- incorreta: conceito errado ou ausente

Forneça feedback construtivo: o que o estudante acertou, o que faltou ou está \
incorreto, e uma explicação breve do conceito correto.
Responda APENAS com JSON puro, sem markdown, no formato exato:
{{"classificacao": "correta|parcialmente_correta|incorreta", "feedback": "..."}}"""


def _evento_json(evento: str, **campos: Any) -> str:
    return json.dumps({"evento": evento, **campos}, ensure_ascii=False, default=str)


def _montar_contexto(chunks: list[dict[str, Any]]) -> str:
    return "\n\n".join(c.get("conteudo", "") for c in chunks[:10])


def _extrair_json(texto: str) -> dict[str, Any]:
    limpo = texto.strip()
    if limpo.startswith("```"):
        limpo = limpo.split("```")[1]
        limpo = limpo[4:] if limpo.startswith("json") else limpo
    inicio, fim = limpo.find("{"), limpo.rfind("}")
    if inicio == -1 or fim == -1:
        raise ValueError("Nenhum objeto JSON encontrado na resposta")
    return json.loads(limpo[inicio : fim + 1])


def _calcular_taxas_erro(linhas: list[Any]) -> dict[str, float]:
    taxas: dict[str, float] = {}
    for topico, total, erros in linhas:
        taxa = (erros or 0) / total if total else 0.0
        if taxa > _LIMITE_TAXA_ERRO:
            taxas[topico] = round(taxa, 2)
    return taxas


class LearningService:
    def __init__(
        self,
        cliente_llm: AsyncOpenAI,
        rag_service: RAGService,
        db: AsyncSession,
    ) -> None:
        self._llm = cliente_llm
        self._rag = rag_service
        self._db = db

    async def _chamar_llm(self, prompt: str, max_tokens: int) -> str:
        resposta = await self._llm.chat.completions.create(
            model=settings.gemma_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return resposta.choices[0].message.content or ""

    def _parse_json(self, bruto: str, metodo: str) -> dict[str, Any]:
        try:
            return _extrair_json(bruto)
        except (json.JSONDecodeError, ValueError):
            logger.error(_evento_json("parse_json_falhou", metodo=metodo, resposta_bruta=bruto[:200]))
            raise

    async def gerar_exercicios(self, topico: str, top_k: int = 10) -> str:
        try:
            chunks = self._rag.recuperar_chunks(query=topico, top_k=top_k)
            prompt = _PROMPT_EXERCICIOS.format(topico=topico, contexto=_montar_contexto(chunks))
            logger.info(_evento_json("llm_chamado", metodo="gerar_exercicios", topico=topico, total_chunks=len(chunks)))
            resultado = await self._chamar_llm(prompt, _MAX_TOKENS_EXERCICIOS)
            logger.info(_evento_json("llm_respondeu", metodo="gerar_exercicios", tamanho_resposta=len(resultado)))
            return resultado
        except Exception:
            logger.error("Erro em gerar_exercicios: topico=%s", topico, exc_info=True)
            raise

    async def gerar_pergunta_recall(self, topico: str) -> dict[str, Any]:
        try:
            chunks = self._rag.recuperar_chunks(query=topico, top_k=5)
            prompt = _PROMPT_PERGUNTA.format(topico=topico, contexto=_montar_contexto(chunks))
            logger.info(_evento_json("llm_chamado", metodo="gerar_pergunta_recall", topico=topico))
            bruto = await self._chamar_llm(prompt, _MAX_TOKENS_RECALL)
            logger.info(_evento_json("llm_respondeu", metodo="gerar_pergunta_recall"))
            dados = self._parse_json(bruto, "gerar_pergunta_recall")
            return await self._persistir_pergunta(topico, dados)
        except Exception:
            logger.error("Erro em gerar_pergunta_recall: topico=%s", topico, exc_info=True)
            raise

    async def _persistir_pergunta(self, topico: str, dados: dict[str, Any]) -> dict[str, Any]:
        sessao = SessaoRecall(
            topico=topico,
            pergunta=dados["pergunta"],
            resposta_referencia=dados["resposta_referencia"],
        )
        self._db.add(sessao)
        await self._db.flush()
        await self._db.refresh(sessao)
        await self._db.commit()
        return {
            "pergunta": sessao.pergunta,
            "sessao_id": sessao.id,
        }

    async def avaliar_resposta_recall(
        self,
        pergunta: str,
        resposta_referencia: str,
        resposta_usuario: str,
        sessao_id: str | None = None,
    ) -> dict[str, Any]:
        if sessao_id and (not pergunta or not resposta_referencia):
            sessao = await self._db.get(SessaoRecall, sessao_id)
            if sessao:
                pergunta = pergunta or sessao.pergunta or ""
                resposta_referencia = resposta_referencia or sessao.resposta_referencia or ""
        if not pergunta or not resposta_referencia:
            logger.warning(_evento_json("active_recall_sem_contexto", sessao_id=sessao_id))
            return {
                "classificacao": "erro",
                "feedback": "Contexto da pergunta original não disponível. Inicie um novo ciclo de active recall.",
            }
        avaliacao = await self._avaliar_com_llm(pergunta, resposta_referencia, resposta_usuario)
        if sessao_id:
            await self._atualizar_sessao(sessao_id, resposta_usuario, avaliacao)
        return avaliacao

    async def _avaliar_com_llm(
        self, pergunta: str, referencia: str, resposta_usuario: str
    ) -> dict[str, Any]:
        prompt = _PROMPT_AVALIACAO.format(
            pergunta=pergunta, referencia=referencia, resposta=resposta_usuario
        )
        logger.info(_evento_json("llm_chamado", metodo="avaliar_resposta_recall"))
        bruto = await self._chamar_llm(prompt, _MAX_TOKENS_RECALL)
        logger.info(_evento_json("llm_respondeu", metodo="avaliar_resposta_recall"))
        return self._parse_json(bruto, "avaliar_resposta_recall")

    async def _atualizar_sessao(
        self, sessao_id: str, resposta_usuario: str, avaliacao: dict[str, Any]
    ) -> None:
        sessao = await self._db.get(SessaoRecall, sessao_id)
        if sessao is None:
            logger.warning(_evento_json("sessao_recall_nao_encontrada", sessao_id=sessao_id))
            return
        sessao.resposta_usuario = resposta_usuario
        sessao.classificacao = avaliacao.get("classificacao")
        sessao.feedback = avaliacao.get("feedback")
        sessao.respondida_em = datetime.utcnow()
        await self._db.flush()
        await self._db.commit()

    async def listar_erros_por_topico(self) -> dict[str, float]:
        try:
            erros_expr = func.sum(case((SessaoRecall.classificacao != "correta", 1), else_=0))
            stmt = (
                select(SessaoRecall.topico, func.count().label("total"), erros_expr.label("erros"))
                .where(SessaoRecall.classificacao.isnot(None))
                .group_by(SessaoRecall.topico)
            )
            linhas = (await self._db.execute(stmt)).all()
            return _calcular_taxas_erro(linhas)
        except Exception:
            logger.error("Erro em listar_erros_por_topico", exc_info=True)
            raise
