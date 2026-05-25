import logging
import os
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

_SIGLAS = {'ia', 'rag', 'ml', 'nlp', 'cnn', 'rnn', 'llm', 'api'}


def _formatar_titulo(nome_arquivo: str) -> str:
    sem_ext = os.path.splitext(nome_arquivo)[0]
    sem_prefixo = re.sub(r'^\d+[_\-]', '', sem_ext)
    palavras = re.split(r'[_\-]+', sem_prefixo)
    return ' '.join(
        p.upper() if p.lower() in _SIGLAS else p.capitalize()
        for p in palavras if p
    )


@router.get("/materiais")
async def listar_materiais() -> list[dict]:
    try:
        pasta = settings.documents_dir
        if not os.path.isdir(pasta):
            return []
        arquivos = sorted([
            f for f in os.listdir(pasta)
            if f.lower().endswith(('.pdf', '.txt', '.md'))
        ])
        return [{"nome": f, "titulo": _formatar_titulo(f)} for f in arquivos]
    except Exception:
        logger.exception("Erro ao listar materiais")
        return []


@router.get("/materiais/{nome_arquivo}")
async def baixar_material(nome_arquivo: str) -> FileResponse:
    pasta = os.path.realpath(settings.documents_dir)
    caminho = os.path.realpath(os.path.join(pasta, nome_arquivo))
    if not caminho.startswith(pasta + os.sep):
        raise HTTPException(status_code=400, detail="Caminho inválido")
    if not os.path.isfile(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    media = "application/pdf" if nome_arquivo.lower().endswith(".pdf") else "text/plain"
    return FileResponse(
        path=caminho,
        media_type=media,
        filename=nome_arquivo,
        headers={"Content-Disposition": f"inline; filename={nome_arquivo}"},
    )
