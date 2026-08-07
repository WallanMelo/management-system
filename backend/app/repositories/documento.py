from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.utils.datetime import google_datetime

class DocumentoRepository:
    def criar_google(self,db: Session,arquivo: dict) -> Documento:

        documento = Documento(
            nome_original=arquivo["name"],
            nome_sistema=arquivo["name"],
            drive_file_id=arquivo["id"],
            drive_parent_id=(
                arquivo["parents"][0]
                if arquivo.get("parents")
                else None
            ),
            mime_type=arquivo.get("mimeType"),
            tamanho=int(arquivo.get("size", 0)),
            modified_time=google_datetime(
                arquivo.get("modifiedTime")
            )
        )

        db.add(documento)
        db.commit()
        db.refresh(documento)

        return documento

    def buscar_por_id(self, db: Session, documento_id: int) -> Documento | None:
        stmt = select(Documento).where(Documento.id == documento_id)
        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Documento]:
        stmt = select(Documento).order_by(Documento.created_at.desc())
        return list(db.scalars(stmt).all())

    def listar_por_cliente(
        self,
        db: Session,
        cliente_id: int
    ) -> list[Documento]:

        stmt = (
            select(Documento)
            .where(Documento.cliente_id == cliente_id)
            .order_by(Documento.created_at.desc())
        )

        return list(db.scalars(stmt).all())

    def criar(self, db: Session, documento: Documento) -> Documento:
        db.add(documento)
        db.commit()
        db.refresh(documento)
        return documento

    def atualizar(self, db: Session, documento: Documento) -> Documento:
        db.commit()
        db.refresh(documento)
        return documento

    def excluir(self, db: Session, documento: Documento):
        db.delete(documento)
        db.commit()

    def buscar_por_drive_id(self,db: Session,drive_id: str) -> Documento | None:

        stmt = (
            select(Documento)
            .where(
                Documento.drive_file_id == drive_id
            )
        )
        return db.scalar(stmt)

    def remover_por_drive_id(self,db: Session,drive_id: str)-> None:
        documento = self.buscar_por_drive_id(db,drive_id)

        if documento:
            db.delete(documento)
            db.commit()

    def listar_google(self,db: Session) -> list[Documento]:

        stmt = (
            select(Documento)
            .where(Documento.drive_file_id.is_not(None))
        )
        return list(db.scalars(stmt).all())

    def atualizar_google(self,db: Session,documento: Documento,arquivo: dict) -> Documento:

        documento.nome_original = arquivo["name"]
        documento.nome_sistema = arquivo["name"]

        documento.drive_parent_id = (
            arquivo["parents"][0]
            if arquivo.get("parents")
            else None
        )

        documento.mime_type = arquivo.get("mimeType")

        documento.tamanho = int(
            arquivo.get("size", 0)
        )

        if arquivo.get("modifiedTime"):
            documento.modified_time = google_datetime(
                arquivo["modifiedTime"]
            )

        db.commit()
        db.refresh(documento)

        return documento

    def listar_por_drive_parent(self,db: Session,parent_id: str | None):

        stmt = (
            select(Documento)
            .where(Documento.drive_parent_id == parent_id)
            .order_by(Documento.nome_original)
        )

        return list(db.scalars(stmt).all())
    
    def buscar_por_hash(self,db: Session,hash: str):
        stmt = select(Documento).where(Documento.hash == hash)
        return db.scalar(stmt)

documento_repository = DocumentoRepository()