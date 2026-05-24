import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StatusTarefa(str, enum.Enum):
    pendente = "pendente"
    concluida = "concluida"


class Tarefa(Base):
    __tablename__ = "tarefas"
    __table_args__ = (
        Index("ix_tarefas_disciplina", "disciplina"),
        Index("ix_tarefas_status", "status"),
        Index("ix_tarefas_prazo", "prazo"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    disciplina: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[StatusTarefa] = mapped_column(
        Enum(StatusTarefa), nullable=False, default=StatusTarefa.pendente
    )
    prazo: Mapped[date | None] = mapped_column(Date, nullable=True)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
