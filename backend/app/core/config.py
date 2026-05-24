from pydantic_settings import BaseSettings, SettingsConfigDict


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
    faiss_index_path: str = "data/faiss_index.bin"
    documents_dir: str = "data/documents"


settings = Settings()
