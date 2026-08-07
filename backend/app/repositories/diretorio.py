from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.diretorio import Diretorio
from app.utils.datetime import google_datetime

class DiretorioRepository:

    def criar_google(
        self,
        db: Session,
        pasta: dict
    ) -> Diretorio:
        """
        Cria um diretório baseado nas informações
        retornadas pela API do Google Drive.
        """

        diretorio = Diretorio(
            nome=pasta["name"],
            drive_folder_id=pasta["id"],
            drive_parent_id=(
                pasta["parents"][0]
                if pasta.get("parents")
                else None
            )
        )

        db.add(diretorio)
        db.commit()
        db.refresh(diretorio)

        return diretorio

    def atualizar_google(self,db: Session,diretorio: Diretorio,pasta: dict) -> Diretorio:
        """
        Atualiza um diretório já existente utilizando
        os dados do Google Drive.
        """

        diretorio.nome = pasta["name"]

        diretorio.drive_parent_id = (
            pasta["parents"][0]
            if pasta.get("parents")
            else None
        )

        if pasta.get("modifiedTime"):
            diretorio.modified_time = google_datetime(pasta.get("modifiedTime"))
        
        db.commit()
        db.refresh(diretorio)
        return diretorio

    def buscar_por_id(self, db: Session, diretorio_id: int) -> Diretorio | None:
        stmt = select(Diretorio).where(Diretorio.id == diretorio_id)
        return db.scalar(stmt)

    def listar(self, db: Session) -> list[Diretorio]:
        stmt = select(Diretorio).order_by(Diretorio.nome)
        return list(db.scalars(stmt).all())

    def listar_por_cliente(
        self,
        db: Session,
        cliente_id: int
    ) -> list[Diretorio]:

        stmt = (
            select(Diretorio)
            .where(Diretorio.cliente_id == cliente_id)
            .order_by(Diretorio.nome)
        )

        return list(db.scalars(stmt).all())

    def criar(self, db: Session, diretorio: Diretorio) -> Diretorio:
        db.add(diretorio)
        db.commit()
        db.refresh(diretorio)
        return diretorio

    def atualizar(self, db: Session, diretorio: Diretorio) -> Diretorio:
        db.commit()
        db.refresh(diretorio)
        return diretorio

    def excluir(self, db: Session, diretorio: Diretorio):
        db.delete(diretorio)
        db.commit()

    def buscar_por_drive_id(self,db: Session,drive_id: str) -> Diretorio | None:
        stmt = (
            select(Diretorio)
            .where(
                Diretorio.drive_folder_id == drive_id
            )
        )
        return db.scalar(stmt)

    def remover_por_drive_id(self,db,drive_id) -> None:

        pasta = self.buscar_por_drive_id(db,drive_id)

        if pasta:
            db.delete(pasta)
            db.commit()

    def listar_google(self,db: Session) -> list[Diretorio]:

        stmt = (
            select(Diretorio)
            .where(Diretorio.drive_folder_id.is_not(None))
        )

        return list(db.scalars(stmt).all())
        
    def listar_por_drive_parent(self,db: Session,parent_id: str | None):
        stmt = (
            select(Diretorio)
            .where(Diretorio.drive_parent_id == parent_id)
            .order_by(Diretorio.nome)
        )
        return list(db.scalars(stmt).all())
diretorio_repository = DiretorioRepository()