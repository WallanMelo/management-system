from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.repositories.auditoria import auditoria_repository

class AuditoriaService:

    def listar(self, db: Session):
        return auditoria_repository.listar(db)

    def registrar(self,db: Session,auditoria: Auditoria):
        return auditoria_repository.criar(db,auditoria)

    def buscar(self, db: Session, auditoria_id: int):
        auditoria = auditoria_repository.buscar_por_id(db,auditoria_id,)

        if not auditoria:
            raise ValueError("Registro de auditoria não encontrado.")

        return auditoria

auditoria_service = AuditoriaService()