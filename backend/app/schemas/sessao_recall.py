from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessaoRecallCreate(BaseModel):
    topico: str = Field(max_length=300)
    pergunta: str
    resposta_referencia: str


class SessaoRecallUpdate(BaseModel):
    resposta_usuario: str | None = None
    classificacao: str | None = Field(default=None, max_length=50)
    feedback: str | None = None
    respondida_em: datetime | None = None


class SessaoRecallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topico: str
    pergunta: str
    resposta_referencia: str
    resposta_usuario: str | None
    classificacao: str | None
    feedback: str | None
    criada_em: datetime
    respondida_em: datetime | None
