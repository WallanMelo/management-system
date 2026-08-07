import io
import zipfile

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.diretorio import Diretorio
from app.models.documento import Documento
from app.models.configuracao import Configuracao
from app.repositories.diretorio import diretorio_repository
from app.services.google_drive_service import google_drive_service
from app.repositories.documento import documento_repository
from app.core.config import settings

class DiretorioService:
    
    # ========== LISTAR =============================================
    def listar(self, db: Session):
        return diretorio_repository.listar(db)
    
    # ========== BUSCAR =============================================
    def buscar(self, db: Session, diretorio_id: int):
        diretorio = diretorio_repository.buscar_por_id(db, diretorio_id)
        if not diretorio:
            raise ValueError("Diretório não encontrado.")
        return diretorio

    # ========== CRIAR PASTA ========================================
    def criar_pasta(self, db: Session, nome: str, parent_id: str | None = None):
        drive_folder_id = google_drive_service.criar_pasta(nome, parent_id)
        pasta = Diretorio(nome=nome, drive_folder_id=drive_folder_id, drive_parent_id=parent_id, sincronizado=True)
        return diretorio_repository.criar(db, pasta)
    
    # ========== RENOMEAR ========================================
    def renomear(self, db: Session, diretorio_id: int, novo_nome: str):
        pasta = self.buscar(db, diretorio_id)
        google_drive_service.renomear(pasta.drive_folder_id, novo_nome)
        pasta.nome = novo_nome
        return diretorio_repository.atualizar(db, pasta)

    # ========== EXCLUIR ========================================    
    def excluir(self, db: Session, diretorio_id: int):
        pasta = db.query(Diretorio).filter(Diretorio.id == diretorio_id).first()
        if not pasta:
            raise HTTPException(status_code=404, detail="Diretório não encontrado")

        # 1. Tenta remover/enviar para a lixeira no Google Drive
        if pasta.drive_folder_id:
            # ⚠️ Se esta linha falhar, o código PARA AQUI e lança um erro HTTP 400/500
            google_drive_service.excluir(pasta.drive_folder_id)

        # 2. Só chega nesta linha se o Google Drive respondeu com SUCESSO!
        db.delete(pasta)
        db.commit()

    # ========== MOVER ========================================
    def mover(self, db: Session, diretorio_id: int, pasta_destino: str):
        pasta = self.buscar(db, diretorio_id)
        if pasta.drive_parent_id == pasta_destino:
            return pasta
        google_drive_service.mover(pasta.drive_folder_id, pasta_destino)
        pasta.drive_parent_id = pasta_destino
        return diretorio_repository.atualizar(db, pasta)

    # ========== LISTAR CONTEUDO ==============================
    def listar_conteudo(self, db: Session, drive_parent_id: str | None):
        # Se estiver na RAIZ (drive_parent_id é None na requisição)
        if drive_parent_id is None:
            # Pega o ID fixo da pasta raiz OFICIOS no settings
            pasta_raiz_id = getattr(settings, "google_drive_root_folder_id", None) or getattr(settings, "GOOGLE_DRIVE_ROOT_FOLDER_ID", None)

            # Traz SOMENTE o que for filho direto da pasta OFICIOS
            pastas = db.query(Diretorio).filter(
                Diretorio.drive_parent_id == pasta_raiz_id
            ).order_by(Diretorio.nome).all()

            documentos = db.query(Documento).filter(
                Documento.drive_parent_id == pasta_raiz_id
            ).order_by(Documento.nome_original).all()

            return {"pastas": pastas, "documentos": documentos}

        # Para subpastas (quando passa o ID da pasta clicada)
        pastas = diretorio_repository.listar_por_drive_parent(db, drive_parent_id)
        documentos = documento_repository.listar_por_drive_parent(db, drive_parent_id)
        return {"pastas": pastas, "documentos": documentos}

    # ========== BAIXAR PASTA .ZIP ==============================
    def baixar_pasta_zip(self, db: Session, diretorio_id: int):
        # 1. Busca as informações da pasta no banco
        pasta = self.buscar(db, diretorio_id)
        if not pasta:
            raise ValueError("Pasta não encontrada no banco de dados.")

        # 2. Busca os documentos pertencentes a essa pasta usando o repositorio de documentos
        documentos = []
        if pasta.drive_folder_id:
            documentos = documento_repository.listar_por_drive_parent(db, pasta.drive_folder_id)

        # Caso não encontre pelo drive_folder_id, tenta a busca direta no banco
        if not documentos:
            documentos = db.query(Documento).filter(
                or_(
                    Documento.diretorio_id == pasta.id,
                    Documento.drive_parent_id == pasta.drive_folder_id
                )
            ).all()

        print(f"🔍 [ZIP LOG] Pasta: '{pasta.nome}' | Arquivos encontrados no banco: {len(documentos)}")

        # Se não houver documentos cadastrados nesta pasta, avisa o usuário no Front-end
        if not documentos:
            raise ValueError(f"A pasta '{pasta.nome}' está vazia ou não possui arquivos cadastrados.")

        # 3. Cria o buffer em memória para o ZIP
        zip_buffer = io.BytesIO()

        # 4. Compactação dos arquivos
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documentos:
                try:
                    # Identifica o ID do Google Drive no seu model Documento
                    file_id = getattr(doc, 'drive_file_id', None) or getattr(doc, 'drive_id', None) or getattr(doc, 'file_id', None)

                    if not file_id:
                        print(f"⚠️ [ZIP LOG] O documento '{doc.nome_original}' (ID {doc.id}) não possui ID do Google Drive.")
                        continue

                    print(f"⬇️ [ZIP LOG] Baixando do Drive: {doc.nome_original} (ID Drive: {file_id})...")
                    
                    # Baixa os bytes brutos do Google Drive
                    conteudo_bytes = google_drive_service.download_arquivo_bytes(file_id)
                    
                    nome_arquivo = doc.nome_original or f"documento_{doc.id}"
                    zip_file.writestr(nome_arquivo, conteudo_bytes)
                    print(f"✅ [ZIP LOG] Adicionado com sucesso: {nome_arquivo}")

                except Exception as err:
                    print(f"❌ [ZIP LOG] Erro ao baixar arquivo '{getattr(doc, 'nome_original', doc.id)}': {err}")

        zip_buffer.seek(0)
        return zip_buffer, pasta.nome

diretorio_service = DiretorioService()