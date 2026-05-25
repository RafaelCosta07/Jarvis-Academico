from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — registra Evento e Tarefa no Base.metadata
from app.api.routes import agenda, chat, materiais, tasks
from app.api.routes.chat import inicializar_rag_startup
from app.core.database import create_all_tables

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await create_all_tables()
    logger.info("Banco inicializado — tabelas criadas/verificadas")
    await asyncio.to_thread(inicializar_rag_startup)
    yield


app = FastAPI(
    title="JARVIS Acadêmico",
    version="1.0.0",
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agenda.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(materiais.router, prefix="/api")
