from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    String,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Auditoria(Base):
    __tablename__ = "auditorias"
    id: Mapped[int] = mapped_column(primary_key=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"),nullable=False)

    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"),nullable=False)

    acao: Mapped[str] = mapped_column(String(100),nullable=False)

    ip: Mapped[str | None] = mapped_column(String(50),nullable=True)

    observacao: Mapped[str | None] = mapped_column(String(500),nullable=True)

    data_hora: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    usuario = relationship("Usuario",back_populates="auditorias")

    documento = relationship("Documento",back_populates="auditorias")