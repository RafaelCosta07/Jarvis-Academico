from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import settings


@lru_cache(maxsize=1)
def criar_cliente_llm() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.gemma_base_url,
        api_key=settings.gemma_api_key,
    )
