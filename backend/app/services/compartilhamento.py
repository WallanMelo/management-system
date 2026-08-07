from sqlalchemy.orm import Session

from app.models.compartilhamento import Compartilhamento
from app.repositories.compartilhamento import (compartilhamento_repository)
from app.schemas.compartilhamento import CompartilhamentoCreate

class CompartilhamentoService:

    def listar(self, db: Session):
        return compartilhamento_repository.listar(db)

    def criar(self,db: Session,dados: CompartilhamentoCreate,):
        compartilhamento_existente = (compartilhamento_repository.buscar_por_documento_e_usuario(db,dados.documento_id,dados.usuario_id,))

        if compartilhamento_existente:
            raise ValueError("Este documento já foi compartilhado com este usuário.")
        compartilhamento = Compartilhamento(documento_id=dados.documento_id,usuario_id=dados.usuario_id,visualizar=dados.visualizar,download=dados.download,)

        return compartilhamento_repository.criar(db,compartilhamento,)

    def excluir(self,db: Session,compartilhamento: Compartilhamento):
        compartilhamento_repository.excluir(db,compartilhamento)

    def buscar(self,db: Session,compartilhamento_id: int,):
        return compartilhamento_repository.buscar_por_id(db,compartilhamento_id,)
compartilhamento_service = CompartilhamentoService()