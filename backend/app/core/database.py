import logging
import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

_DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./jarvis.db"


class Base(DeclarativeBase):
    pass


def _make_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, echo=False)


def _make_session_factory(
    eng: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=eng, class_=AsyncSession, expire_on_commit=False)


# Instâncias padrão — substituíveis em testes via configure_for_testing()
engine: AsyncEngine = _make_engine(
    os.getenv("DATABASE_URL", _DEFAULT_DATABASE_URL)
)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = _make_session_factory(engine)


def configure_for_testing(database_url: str) -> None:
    """Substitui engine e session factory — chamado no setup de testes."""
    global engine, AsyncSessionLocal
    engine = _make_engine(database_url)
    AsyncSessionLocal = _make_session_factory(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            logger.exception("Erro na sessão do banco — executando rollback")
            await session.rollback()
            raise


async def create_all_tables() -> None:
    # Os models devem ser importados antes desta chamada para que
    # Base.metadata os conheça (feito em app/models/__init__.py).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
