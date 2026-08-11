from enum import Enum
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum
)

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column

from app.database.base import Base

from app.models.enums import TemaSistema


class Configuracao(Base):

    __tablename__ = "configuracoes"

    id: Mapped[int] = mapped_column(primary_key=True)

    google_refresh_token = Column(String, nullable=True)

    nome_empresa: Mapped[str] = mapped_column(String(255),nullable=True)

    cnpj: Mapped[str | None] = mapped_column(String(20),nullable=True)

    telefone: Mapped[str | None] = mapped_column(String(20),nullable=True)

    email: Mapped[str | None] = mapped_column(String(255),nullable=True)

    logo: Mapped[str | None] = mapped_column(String(255),nullable=True)

    pasta_drive: Mapped[str | None] = mapped_column(String(255),nullable=True)

    tema: Mapped[TemaSistema] = mapped_column(SQLEnum(TemaSistema),default=TemaSistema.CLARO)

    backup_automatico: Mapped[bool] = mapped_column(Boolean,default=True)

    start_page_token: Mapped[str | None] = mapped_column(String(255),nullable=True)

    ultima_sincronizacao: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)

    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now,onupdate=datetime.now)