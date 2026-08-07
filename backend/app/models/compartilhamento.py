from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    Boolean,
    DateTime, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Compartilhamento(Base):
    __tablename__ = "compartilhamentos"

    __table_args__ = (
        UniqueConstraint(
            "documento_id",
            "usuario_id",
            name="uq_documento_usuario",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"),nullable=False)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"),nullable=False)

    visualizar: Mapped[bool] = mapped_column(Boolean,default=True)

    download: Mapped[bool] = mapped_column(Boolean,default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    documento = relationship("Documento",back_populates="compartilhamentos")

    usuario = relationship("Usuario",back_populates="compartilhamentos")