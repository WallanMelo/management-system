from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime, Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database.base import Base

class Diretorio(Base):
    __tablename__ = "diretorios"

    id: Mapped[int] = mapped_column(primary_key=True)

    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id", ondelete="CASCADE"),nullable=True)

    diretorio_pai_id: Mapped[int | None] = mapped_column(ForeignKey("diretorios.id", ondelete="CASCADE"),nullable=True)

    nome: Mapped[str] = mapped_column(String(100))

    drive_folder_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)

    cliente = relationship("Cliente",back_populates="diretorios")

    documentos = relationship("Documento",back_populates="diretorio")

    drive_parent_id: Mapped[str | None] = mapped_column(String(255),nullable=True)
 
    modified_time: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)

    ultima_sincronizacao: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)

    diretorio_pai = relationship("Diretorio",remote_side=[id],back_populates="subdiretorios")

    subdiretorios = relationship("Diretorio",back_populates="diretorio_pai")

    sincronizado: Mapped[bool] = mapped_column(Boolean,default=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)