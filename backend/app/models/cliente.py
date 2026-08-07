from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    cpf_cnpj: Mapped[str | None] = mapped_column(String(18))

    telefone: Mapped[str | None] = mapped_column(String(20))

    email: Mapped[str | None] = mapped_column(String(150))

    observacao: Mapped[str | None] = mapped_column(Text)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)

    diretorios = relationship("Diretorio", back_populates="cliente")

    documentos = relationship("Documento", back_populates="cliente")