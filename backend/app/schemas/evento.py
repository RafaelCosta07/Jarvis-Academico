from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.evento import TipoEvento


class EventoCreate(BaseModel):
    titulo: str = Field(max_length=200)
    data: date
    tipo: TipoEvento
    descricao: str | None = Field(default=None, max_length=1000)
    hora_inicio: time | None = None
    hora_fim: time | None = None
    local: str | None = Field(default=None, max_length=200)


class EventoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    titulo: str
    data: date
    tipo: TipoEvento
    descricao: str | None
    hora_inicio: time | None
    hora_fim: time | None
    local: str | None

    @field_serializer("hora_inicio", "hora_fim")
    def _serializar_hora(self, v: time | None) -> str | None:
        return v.strftime("%H:%M") if v is not None else None


class EventoUpdate(BaseModel):
    titulo: str | None = Field(default=None, max_length=200)
    data: date | None = None
    tipo: TipoEvento | None = None
    descricao: str | None = Field(default=None, max_length=1000)
    hora_inicio: time | None = None
    hora_fim: time | None = None
    local: str | None = Field(default=None, max_length=200)
