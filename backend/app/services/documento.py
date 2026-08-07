import os
import mimetypes
from sqlalchemy.orm import Session

from app.models.documento import Documento
from app.repositories.documento import documento_repository
from app.services.google_drive_service import google_drive_service

class DocumentoService:

    def criar(self, db: Session, dados):
        documento = Documento(**dados.model_dump())
        return documento_repository.criar(db, documento)

    def atualizar(self, db: Session, documento: Documento, dados):
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(documento, campo, valor)
        return documento_repository.atualizar(db, documento)

    def listar(self, db: Session):
        return documento_repository.listar(db)

    def buscar(self, db: Session, documento_id: int):
        documento = documento_repository.buscar_por_id(db,documento_id)
        if not documento:
            raise ValueError("Documento não encontrado.")
        return documento

    def excluir(self,db: Session,documento_id: int):
        documento = self.buscar(db,documento_id)
        google_drive_service.excluir(documento.drive_file_id)
        documento_repository.excluir(db,documento)


    def renomear(self,db: Session,documento_id: int,novo_nome: str):
        documento = self.buscar(db,documento_id)
        google_drive_service.renomear(documento.drive_file_id,novo_nome)
        documento.nome_original = novo_nome
        documento.nome_sistema = novo_nome
        return documento_repository.atualizar(db,documento)

    def upload(self, db: Session, caminho_arquivo: str, nome: str, pasta_id=None):
        print("Entrou no DocumentoService")

        # 1. Envia o arquivo para o Google Drive
        drive_file_id = google_drive_service.upload(
            caminho_arquivo,
            nome,
            pasta_id,
        )

        print("Arquivo enviado ao Drive.")
        print("ID:", drive_file_id)

        # 🎯 2. CAPTURA O TAMANHO REAL DO ARQUIVO (EM BYTES) E O TIPO MIME
        tamanho_bytes = os.path.getsize(caminho_arquivo) if os.path.exists(caminho_arquivo) else 0
        mime_type, _ = mimetypes.guess_type(nome)

        # 3. Cria a instância do documento incluindo o tamanho e o mime_type
        documento = Documento(
            nome_original=nome,
            nome_sistema=nome,
            drive_file_id=drive_file_id,
            drive_parent_id=pasta_id,
            tamanho=tamanho_bytes,  # 👈 CORRIGIDO: Agora o tamanho é gravado no banco
            mime_type=mime_type,    # 👈 CORRIGIDO: Adicionado o tipo MIME correto
            sincronizado=True,
        )

        print("Salvando no banco...")

        documento = documento_repository.criar(db, documento)

        print(f"Documento salvo! Tamanho gravado: {tamanho_bytes} bytes")

        return documento

    ## Então o ROUTER q utilizar vai chamar a função passando o true ou false comoparametro
    def definir_favorito(self,db: Session,documento_id: int,favorito: bool):
        documento = self.buscar(db,documento_id)
        documento.favorito = favorito
        return documento_repository.atualizar(db,documento)
    
    def mover(self,db: Session,documento_id: int,pasta_destino: str):
        documento = self.buscar(db, documento_id)
        if documento.drive_parent_id == pasta_destino:
            return documento
        google_drive_service.mover(documento.drive_file_id,pasta_destino)
        documento.drive_parent_id = pasta_destino
        return documento_repository.atualizar(db,documento)

    def download(self,db:Session,documento_id: int,destino: str):
        documento = self.buscar(db,documento_id)
        return google_drive_service.download(documento.drive_file_id,destino)

    def alterar_descricao(self,db: Session,documento_id: int,descricao: str):
        documento = self.buscar(db,documento_id)
        documento.descricao = descricao
        return documento_repository.atualizar(db,documento)

documento_service = DocumentoService()