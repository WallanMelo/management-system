from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from app.core.config import settings
import os, io, threading
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from googleapiclient.errors import HttpError
from fastapi import HTTPException


SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleDriveClient:
    """
    Cliente responsável por toda comunicação com a API do Google Drive.
    Inclui um Lock de thread para evitar erros de concorrencia TLS/SSL no httplib2.
    """

    def __init__(self):
        self._lock = threading.Lock()  # Lock para thread-safety

        creds = None
        token_path = os.path.join(
            os.path.dirname(settings.google_credentials),
            "token.pickle"
        )
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_credentials,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

        self.service = build(
            "drive",
            "v3",
            credentials=creds
        )

    def _execute(self, request):
        """Método utilitário para garantir que qualquer chamada HTTP seja thread-safe."""
        with self._lock:
            return request.execute()

    # ==========================================================
    # TESTE
    # ==========================================================
    def testar_conexao(self):
        req = self.service.about().get(fields="user")
        return self._execute(req)
    
    # ======= CRIAR PASTA ========================================================
    def criar_pasta(self,nome: str,parent_id: str | None = None) -> str:
        metadata = {"name": nome,"mimeType": "application/vnd.google-apps.folder"}

        if parent_id:
            metadata["parents"] = [parent_id]

        req = self.service.files().create(body=metadata,fields="id,name")
        pasta = self._execute(req)

        return pasta["id"]

    # ======= BUSCAR PASTA ========================================================
    def buscar_pasta(self,folder_id: str):
        req = self.service.files().get(fileId=folder_id,fields="id,name")
        return self._execute(req)

    # ======= LISTAR ITENS ========================================================
    def listar_itens(self,folder_id: str):
        req = self.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,parents,createdTime,modifiedTime,size)"
        )
        resultado = self._execute(req)

        return resultado.get("files", [])

    # ======= LISTAR ARQUIVOS ========================================================
    def listar_arquivos(self,folder_id: str):
        itens = self.listar_itens(folder_id)

        return [
            item
            for item in itens
            if item["mimeType"] != "application/vnd.google-apps.folder"
        ]

    # ======= LISTAR PASTAS ========================================================
    def listar_pastas(self,folder_id: str):
        itens = self.listar_itens(folder_id)

        return [
            item
            for item in itens
            if item["mimeType"] == "application/vnd.google-apps.folder"
        ]

    # ======= EXCLUIR ========================================================
    def excluir(self, file_id: str):
        try:
            req = self.service.files().delete(fileId=file_id, supportsAllDrives=True)
            self._execute(req)

        except HttpError as error:
            if error.resp.status == 403:
                email_proprietario = "desconhecido"
                try:
                    req_dono = self.service.files().get(
                        fileId=file_id,
                        fields="owners",
                        supportsAllDrives=True
                    )
                    arquivo_info = self._execute(req_dono)
                    
                    donos = arquivo_info.get("owners", [])
                    if donos:
                        email_proprietario = donos[0].get("emailAddress", "desconhecido")
                except Exception:
                    pass
                
                raise HTTPException(
                    status_code=403, 
                    detail=f"Somente o proprietário ({email_proprietario}) pode excluir essa pasta/arquivo."
                )
                
            elif error.resp.status == 404:
                pass
            else:
                raise HTTPException(status_code=500, detail=f"Erro no Google Drive: {error}")

    # ======= RENOMEAR ========================================================
    def renomear(self,file_id: str,novo_nome: str):
        req = self.service.files().update(
            fileId=file_id,
            body={"name": novo_nome}
        )
        self._execute(req)

    # ======= UPLOAD ARQUIVOS ========================================================
    def upload_arquivo(self, caminho_arquivo: str, nome: str, pasta_id: str | None = None) -> str:
        metadata = {"name": nome}

        if pasta_id:
            metadata["parents"] = [pasta_id]

        media = MediaFileUpload(
            caminho_arquivo,
            resumable=True
        )

        req = self.service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,parents"
        )
        arquivo = self._execute(req)

        return arquivo["id"]

    # ======= START PAGE TOKEN ========================================================
    def get_start_page_token(self) -> str:
        req = self.service.changes().getStartPageToken()
        resposta = self._execute(req)

        return resposta["startPageToken"]
    
    # ======= CHANGES API ========================================================
    def get_changes(
            self,
            page_token: str
        ):
            req = self.service.changes().list(
                pageToken=page_token,
                fields="nextPageToken,newStartPageToken,changes(fileId,removed,time,file(id,name,mimeType,parents,trashed,modifiedTime,createdTime,size))"
            )
            return self._execute(req)

    # ======= DOWNLOAD ========================================================
    def download(self, file_id: str, destino: str) -> str:
        req_meta = self.service.files().get(fileId=file_id, fields="name")
        metadata = self._execute(req_meta)

        nome = metadata["name"]
        caminho = os.path.join(destino, nome)

        # ⚡ Cria a pasta temporária de destino caso ela ainda não exista no sistema
        os.makedirs(os.path.dirname(caminho), exist_ok=True)

        request = self.service.files().get_media(fileId=file_id)
        arquivo = io.FileIO(caminho, "wb")
        downloader = MediaIoBaseDownload(arquivo, request)

        done = False
        while not done:
            with self._lock:
                _, done = downloader.next_chunk()

        arquivo.close()
        return caminho

    # ======= DOWNLOAD BYTES (NOVO) ========================================================
    def download_bytes(self, file_id: str) -> bytes:
        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            with self._lock:
                _, done = downloader.next_chunk()

        return buffer.getvalue()

    # ======= COMPARTILHAR ========================================================
    def compartilhar(self, file_id: str, email: str, permissao: str = "reader"):
        permissao_body = {
            "type": "user",
            "role": permissao,
            "emailAddress": email
        }

        req = self.service.permissions().create(
            fileId=file_id,
            body=permissao_body,
            sendNotificationEmail=True
        )
        self._execute(req)

    # ======= TORNAR PÚBLICO ========================================================
    def tornar_publico(self, file_id: str):
        req_perm = self.service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        )
        self._execute(req_perm)

        req_info = self.service.files().get(
            fileId=file_id,
            fields="id,webViewLink"
        )
        arquivo = self._execute(req_info)

        return arquivo["webViewLink"]
    
    # ======= LISTAR ARVORE ========================================================
    def listar_arvore(self, folder_id: str):
        resultado = []
        itens = self.listar_itens(folder_id)

        for item in itens:
            resultado.append(item)
            if item["mimeType"] == "application/vnd.google-apps.folder":
                resultado.extend(self.listar_arvore(item["id"]))
        return resultado

    # ======= BUSCAR ARQUIVO ========================================================
    def buscar_arquivo(self, file_id: str):
        req = self.service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,parents,modifiedTime,createdTime,size,webViewLink,trashed,owners,permissions"
        )
        return self._execute(req)
    
    # ======= MOVER ========================================================
    def mover(self, file_id: str, pasta_destino: str):
        req_p = self.service.files().get(fileId=file_id, fields="parents")
        arquivo = self._execute(req_p)

        pais_atuais = ",".join(arquivo.get("parents", []))

        req_up = self.service.files().update(
            fileId=file_id,
            addParents=pasta_destino,
            removeParents=pais_atuais,
            fields="id,parents"
        )
        self._execute(req_up)

    # ======= ATUALIZAR O ARQUIVO ========================================================
    def atualizar_arquivo(self, file_id: str, caminho_arquivo: str):
        media = MediaFileUpload(caminho_arquivo, resumable=True)
        req = self.service.files().update(fileId=file_id, media_body=media)
        self._execute(req)

    # ======= COPIAR ========================================================
    def copiar(self, file_id, novo_nome):
        req = self.service.files().copy(fileId=file_id, body={"name": novo_nome})
        return self._execute(req)