import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SessaoRecall(Base):
    __tablename__ = "sessoes_recall"
    __table_args__ = (
        Index("ix_sessoes_recall_topico", "topico"),
        Index("ix_sessoes_recall_classificacao", "classificacao"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    topico: Mapped[str] = mapped_column(String(300), nullable=False)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta_referencia: Mapped[str] = mapped_column(Text, nullable=False)
    resposta_usuario: Mapped[str | None] = mapped_column(Text, nullable=True)
    classificacao: Mapped[str | None] = mapped_column(String(50), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    respondida_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
