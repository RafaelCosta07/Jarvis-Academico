import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 800
_CHUNK_OVERLAP = 100
_CHUNK_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]
_EMBEDDING_DIM = 384


class RAGService:
    def __init__(
        self,
        modelo_embedding: SentenceTransformer,
        index_path: str,
        metadata_path: str,
    ) -> None:
        self.modelo = modelo_embedding
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index: Any = None
        self.chunks_metadata: list[dict] = []

    # ------------------------------------------------------------------ #
    # Ingestão                                                             #
    # ------------------------------------------------------------------ #

    def _ler_pdf(self, caminho: Path) -> list[dict]:
        paginas: list[dict] = []
        try:
            leitor = PdfReader(str(caminho))
            for numero, pagina in enumerate(leitor.pages):
                texto = pagina.extract_text() or ""
                if texto.strip():
                    paginas.append({
                        "conteudo": texto,
                        "fonte": caminho.name,
                        "pagina": numero + 1,
                    })
        except Exception:
            logger.error("Falha ao ler PDF: %s", caminho.name, exc_info=True)
        return paginas

    def _ler_texto(self, caminho: Path) -> list[dict]:
        try:
            conteudo = caminho.read_text(encoding="utf-8")
            return [{"conteudo": conteudo, "fonte": caminho.name, "pagina": None}]
        except Exception:
            logger.error("Falha ao ler arquivo: %s", caminho.name, exc_info=True)
            return []

    def ingerir_documentos(self, diretorio: str) -> list[dict]:
        pasta = Path(diretorio)
        if not pasta.exists():
            logger.warning("Diretório de documentos não encontrado: %s", diretorio)
            return []
        documentos: list[dict] = []
        for arquivo in pasta.iterdir():
            sufixo = arquivo.suffix.lower()
            if sufixo == ".pdf":
                documentos.extend(self._ler_pdf(arquivo))
            elif sufixo in {".txt", ".md"}:
                documentos.extend(self._ler_texto(arquivo))
        logger.info("Ingeridos %d seções de '%s'", len(documentos), diretorio)
        return documentos

    # ------------------------------------------------------------------ #
    # Chunking                                                             #
    # ------------------------------------------------------------------ #

    def _fazer_chunks(self, documentos: list[dict]) -> list[dict]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=_CHUNK_SIZE,
            chunk_overlap=_CHUNK_OVERLAP,
            separators=_CHUNK_SEPARATORS,
        )
        chunks: list[dict] = []
        for doc in documentos:
            partes = splitter.split_text(doc["conteudo"])
            for indice, parte in enumerate(partes):
                chunks.append({
                    "conteudo": parte,
                    "fonte": doc["fonte"],
                    "pagina": doc["pagina"],
                    "chunk_index": indice,
                })
        return chunks

    # ------------------------------------------------------------------ #
    # Embedding                                                            #
    # ------------------------------------------------------------------ #

    def _gerar_embeddings(self, textos: list[str]) -> np.ndarray:
        return self.modelo.encode(
            textos, convert_to_numpy=True, show_progress_bar=False
        ).astype(np.float32)

    def _normalizar_l2(self, embedding: np.ndarray) -> np.ndarray:
        norma = np.linalg.norm(embedding, axis=1, keepdims=True)
        return embedding / np.where(norma > 0, norma, 1.0)

    # ------------------------------------------------------------------ #
    # Indexação e persistência                                             #
    # ------------------------------------------------------------------ #

    def construir_indice(self, diretorio: str) -> None:
        try:
            documentos = self.ingerir_documentos(diretorio)
            self.chunks_metadata = self._fazer_chunks(documentos)
            textos = [c["conteudo"] for c in self.chunks_metadata]
            embeddings = self._gerar_embeddings(textos)
            self.index = faiss.IndexFlatL2(_EMBEDDING_DIM)
            self.index.add(embeddings)
            self._salvar_indice()
            self._salvar_metadata()
            logger.info("Índice FAISS construído com %d chunks", len(self.chunks_metadata))
        except Exception:
            logger.error("Falha ao construir índice FAISS", exc_info=True)
            raise

    def _salvar_indice(self) -> None:
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        logger.info("Índice FAISS salvo em %s", self.index_path)

    def _salvar_metadata(self) -> None:
        Path(self.metadata_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks_metadata, f, ensure_ascii=False, indent=2, default=str)
        logger.info("Metadados salvos em %s", self.metadata_path)

    # ------------------------------------------------------------------ #
    # Carregamento                                                         #
    # ------------------------------------------------------------------ #

    def _carregar_de_disco(self) -> bool:
        if not Path(self.index_path).exists() or not Path(self.metadata_path).exists():
            return False
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, encoding="utf-8") as f:
                self.chunks_metadata = json.load(f)
            logger.info("Índice carregado do disco: %d chunks", len(self.chunks_metadata))
            return True
        except Exception:
            logger.error("Falha ao carregar índice de disco", exc_info=True)
            return False

    def carregar_indice(self, diretorio: str) -> None:
        if self._carregar_de_disco():
            return
        logger.info("Índice não encontrado — executando indexação completa")
        self.construir_indice(diretorio)

    # ------------------------------------------------------------------ #
    # Recuperação                                                          #
    # ------------------------------------------------------------------ #

    def _buscar_faiss(
        self, embedding_query: np.ndarray, top_k: int
    ) -> tuple[np.ndarray, np.ndarray]:
        distancias, indices = self.index.search(embedding_query, top_k)
        return distancias[0], indices[0]

    def recuperar_chunks(
        self, query: str, top_k: int = 5, threshold: float = 0.0
    ) -> list[dict]:
        if self.index is None:
            logger.warning("Índice FAISS não inicializado — retornando lista vazia")
            return []
        try:
            embedding_query = self._normalizar_l2(self._gerar_embeddings([query]))
            distancias, indices = self._buscar_faiss(embedding_query, top_k)
            resultados: list[dict] = []
            for distancia, indice in zip(distancias.tolist(), indices.tolist()):
                if indice < 0:
                    continue
                score = 1.0 / (1.0 + distancia)
                if score < threshold:
                    continue
                chunk = {**self.chunks_metadata[indice], "score": round(score, 4)}
                resultados.append(chunk)
            return sorted(resultados, key=lambda c: c["score"], reverse=True)
        except Exception:
            logger.error("Erro ao recuperar chunks: query=%s", query[:50], exc_info=True)
            raise


# --------------------------------------------------------------------------- #
# Fábrica — cria instância padrão a partir das variáveis de ambiente           #
# --------------------------------------------------------------------------- #

def criar_rag_service() -> RAGService:
    from app.core.config import settings  # importação local — evita circular em testes

    index_path = settings.faiss_index_path
    metadata_path = str(
        Path(index_path).parent / "processed" / "chunks_metadata.json"
    )
    modelo = SentenceTransformer(settings.embedding_model)
    return RAGService(modelo, index_path, metadata_path)
