from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente


class ClienteRepository:

    def buscar_por_id(self, db: Session, cliente_id: int) -> Cliente | None:
        stmt = select(Cliente).where(Cliente.id == cliente_id)
        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Cliente]:
        stmt = select(Cliente).order_by(Cliente.nome)
        return list(db.scalars(stmt).all())

    def criar(self, db: Session, cliente: Cliente) -> Cliente:
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

    def atualizar(self, db: Session, cliente: Cliente) -> Cliente:
        db.commit()
        db.refresh(cliente)
        return cliente

    def excluir(self, db: Session, cliente: Cliente) -> None:
        db.delete(cliente)
        db.commit()


cliente_repository = ClienteRepository()