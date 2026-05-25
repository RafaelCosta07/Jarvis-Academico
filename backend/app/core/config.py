from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).parent.parent.parent  # config.py → core/ → app/ → backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemma_api_key: str
    gemma_base_url: str
    gemma_model: str = "google/gemma-3-12b-it"
    database_url: str = "sqlite+aiosqlite:///./jarvis.db"
    log_level: str = "INFO"
    log_file: str = "logs/tool_calls.jsonl"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    chunk_size: int = 800
    chunk_overlap: int = 100
    faiss_index_path: str = str(_BACKEND_DIR / "data" / "faiss_index.bin")
    documents_dir: str = str(_BACKEND_DIR / "data" / "documents")


settings = Settings()
