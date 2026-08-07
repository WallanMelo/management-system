from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compartilhamento import Compartilhamento

class CompartilhamentoRepository:

    def buscar_por_id(self,db: Session,compartilhamento_id: int) -> Compartilhamento | None:
        stmt = (
            select(Compartilhamento)
            .where(Compartilhamento.id == compartilhamento_id)
        )
        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Compartilhamento]:
        stmt = select(Compartilhamento)
        return list(db.scalars(stmt).all())

    def listar_documento(self,db: Session,documento_id: int) -> list[Compartilhamento]:
        stmt = (
            select(Compartilhamento)
            .where(Compartilhamento.documento_id == documento_id)
        )
        return list(db.scalars(stmt).all())

    def criar(self,db: Session,compartilhamento: Compartilhamento) -> Compartilhamento:
        db.add(compartilhamento)
        db.commit()
        db.refresh(compartilhamento)

        return compartilhamento

    def excluir(self,db: Session,compartilhamento: Compartilhamento):
        db.delete(compartilhamento)
        db.commit()


    def buscar_por_documento_e_usuario(self,db: Session,documento_id: int,usuario_id: int,) -> Compartilhamento | None:
        stmt = (
            select(Compartilhamento)
            .where(
                Compartilhamento.documento_id == documento_id,
                Compartilhamento.usuario_id == usuario_id,
            )
        )
        return db.scalar(stmt)
compartilhamento_repository = CompartilhamentoRepository()