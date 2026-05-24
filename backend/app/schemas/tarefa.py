from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarefa import StatusTarefa


class TarefaCreate(BaseModel):
    titulo: str = Field(max_length=200)
    descricao: str | None = Field(default=None, max_length=1000)
    disciplina: str | None = Field(default=None, max_length=100)
    prazo: date | None = None


class TarefaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    titulo: str
    descricao: str | None
    disciplina: str | None
    status: StatusTarefa
    prazo: date | None
    criada_em: datetime
    concluida_em: datetime | None


class TarefaUpdate(BaseModel):
    titulo: str | None = Field(default=None, max_length=200)
    descricao: str | None = Field(default=None, max_length=1000)
    disciplina: str | None = Field(default=None, max_length=100)
    status: StatusTarefa | None = None
    prazo: date | None = None
    concluida_em: datetime | None = None
