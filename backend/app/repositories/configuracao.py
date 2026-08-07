from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.configuracao import Configuracao

class ConfiguracaoRepository:

    def buscar(self, db: Session) -> Configuracao | None:
        stmt = select(Configuracao)
        return db.scalar(stmt)

    def criar(
        self,
        db: Session,
        configuracao: Configuracao
    ) -> Configuracao:

        db.add(configuracao)
        db.commit()
        db.refresh(configuracao)

        return configuracao

    def atualizar(
        self,
        db: Session,
        configuracao: Configuracao
    ) -> Configuracao:

        db.commit()
        db.refresh(configuracao)

        return configuracao

    def atualizar_token(self,db: Session,token: str) -> None:

        configuracao = self.buscar(db)

        if configuracao is None:
            return

        configuracao.start_page_token = token

        db.commit()

        db.refresh(configuracao)

configuracao_repository = ConfiguracaoRepository()