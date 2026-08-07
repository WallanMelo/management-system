from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria


class AuditoriaRepository:

    def buscar_por_id(
        self,
        db: Session,
        auditoria_id: int
    ) -> Auditoria | None:

        stmt = (
            select(Auditoria)
            .where(Auditoria.id == auditoria_id)
        )

        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Auditoria]:
        stmt = (
            select(Auditoria)
            .order_by(Auditoria.data_hora.desc())
        )

        return list(db.scalars(stmt).all())

    def criar(
        self,
        db: Session,
        auditoria: Auditoria
    ) -> Auditoria:

        db.add(auditoria)
        db.commit()
        db.refresh(auditoria)

        return auditoria


auditoria_repository = AuditoriaRepository()