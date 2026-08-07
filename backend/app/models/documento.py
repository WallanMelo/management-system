from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    BigInteger
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Documento(Base):

    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)

    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"),nullable=True)

    diretorio_id: Mapped[int | None] = mapped_column(ForeignKey("diretorios.id"),nullable=True)

    usuario_upload: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"),nullable=True)

    nome_original: Mapped[str] = mapped_column(String(255),nullable=False)

    nome_sistema: Mapped[str] = mapped_column(String(255),nullable=False)

    descricao: Mapped[str | None] = mapped_column(String(500),nullable=True)

    drive_file_id: Mapped[str | None] = mapped_column(String(255),nullable=True)

    mime_type: Mapped[str | None] = mapped_column(String(100),nullable=True)

    tamanho: Mapped[int | None] = mapped_column(BigInteger,nullable=True)

    hash: Mapped[str | None] = mapped_column(String(255),nullable=True,unique=True)

    versao: Mapped[int] = mapped_column(Integer,default=1)

    favorito: Mapped[bool] = mapped_column(Boolean,default=False)

    ativo: Mapped[bool] = mapped_column(Boolean,default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)

    sincronizado: Mapped[bool] = mapped_column(Boolean,default=False)
    
    # ======= RELACIONAMENTOS =================================================
    cliente = relationship("Cliente",back_populates="documentos")

    diretorio = relationship("Diretorio",back_populates="documentos")

    usuario = relationship("Usuario",back_populates="documentos_enviados")

    compartilhamentos = relationship("Compartilhamento",back_populates="documento")

    auditorias = relationship("Auditoria",back_populates="documento")

    drive_parent_id: Mapped[str | None] = mapped_column(String(255),nullable=True)
    modified_time: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)