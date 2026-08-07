from datetime import datetime
from app.models.enums import PerfilUsuario

from sqlalchemy import String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)

    senha_hash: Mapped[str] = mapped_column(String(255),nullable=False)

    perfil: Mapped[PerfilUsuario] = mapped_column(SQLEnum(PerfilUsuario),nullable=False)
    
    ativo: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)

    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)
    
    ## RELACIONAMENTOS
    documentos_enviados = relationship("Documento",back_populates="usuario")
    
    compartilhamentos = relationship("Compartilhamento",back_populates="usuario",cascade="all, delete-orphan")

    auditorias = relationship("Auditoria",back_populates="usuario",cascade="all, delete-orphan")