from app.integrations.google_drive import GoogleDriveClient
from app.core.config import settings

from googleapiclient.http import MediaIoBaseDownload
import io

class GoogleDriveService:

    def __init__(self):
        self.client = GoogleDriveClient()
    """def criar_pasta_cliente(self, nome_cliente: str) -> str:
        
        #Cria uma pasta para um cliente dentro da
        #pasta raiz do sistema.

        #Retorna o ID da pasta criada.
        

        return self.client.criar_pasta(
            nome=nome_cliente,
            parent_id=settings.google_drive_root_folder_id
        )"""

    # =====================================================
    # CONEXÃO
    # =====================================================
    def testar_conexao(self):
        return self.client.testar_conexao()

    # =====================================================
    # LISTAGENS
    # =====================================================
    def listar_root(self):
        return self.client.listar_itens(
            settings.google_drive_root_folder_id
        )

    def listar_arvore_root(self):
        """
        Percorre toda a árvore da pasta raiz.
        """
        return self.client.listar_arvore(
            settings.google_drive_root_folder_id
        )

    def listar_itens(self, folder_id):
        return self.client.listar_itens(folder_id)

    def listar_pastas(self, folder_id):
        return self.client.listar_pastas(folder_id)

    def listar_arquivos(self, folder_id):
        return self.client.listar_arquivos(folder_id)

    # =====================================================
    # PASTAS
    # =====================================================
    def criar_pasta(self, nome, parent_id=None):

        if parent_id is None:
            parent_id = settings.google_drive_root_folder_id

        return self.client.criar_pasta(
            nome,
            parent_id
        )

    # =====================================================
    # ARQUIVOS
    # =====================================================
    def upload(self, caminho, nome, pasta_id=None):

        if pasta_id is None:
            pasta_id = settings.google_drive_root_folder_id

        return self.client.upload_arquivo(
            caminho,
            nome,
            pasta_id
        )

    def excluir(self, file_id):
        self.client.excluir(file_id)

    def renomear(self, file_id, novo_nome):
        self.client.renomear(file_id,novo_nome)

    def download(self, file_id, destino):
        return self.client.download(file_id, destino)
    def compartilhar(self, file_id, email):
        self.client.compartilhar(file_id, email)
    def tornar_publico(self, file_id):
        return self.client.tornar_publico(file_id)
    # =====================================================
    # SINCRONIZAÇÃO
    # =====================================================

    def obter_token_inicial(self):
        return self.client.get_start_page_token()

    def buscar_alteracoes(self, page_token):
        return self.client.get_changes(page_token)

    def mover(self, file_id, pasta_destino):
        self.client.mover(file_id, pasta_destino)

    def buscar_arquivo(self, file_id: str):
        return self.client.buscar_arquivo(file_id)
    
    def atualizar_arquivo(self, file_id, caminho):
        self.client.atualizar_arquivo(file_id, caminho)

    # =====================================================
    # DOWNLOAD DE ARQUIVO EM BYTES (MEMÓRIA PARA ZIP)
    # =====================================================
    def download_arquivo_bytes(self, drive_file_id: str) -> bytes:
        return self.client.download_bytes(drive_file_id)
    
google_drive_service = GoogleDriveService()