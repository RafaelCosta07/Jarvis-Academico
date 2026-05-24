import enum
import uuid
from datetime import date, time

from sqlalchemy import Date, Enum, Index, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoEvento(str, enum.Enum):
    aula = "aula"
    prova = "prova"
    prazo = "prazo"
    outro = "outro"


class Evento(Base):
    __tablename__ = "eventos"
    __table_args__ = (Index("ix_eventos_data", "data"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_fim: Mapped[time | None] = mapped_column(Time, nullable=True)
    tipo: Mapped[TipoEvento] = mapped_column(Enum(TipoEvento), nullable=False)
    local: Mapped[str | None] = mapped_column(String(200), nullable=True)
