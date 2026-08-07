from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool  # 👈 Desbloqueia o Event Loop do FastAPI
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask  # 👈 Para deletar temp após o download
import traceback
import shutil
import os
import tempfile

from app.api.deps import get_db
from app.schemas.documento import (
    DocumentoCreate,
    DocumentoUpdate,
    DocumentoResponse,
    DocumentoRenomear,
    DocumentoMover,
    DocumentoDescricao,
    DocumentoFavorito,
)
from app.services.documento import documento_service
from app.services.sync_service import sync_service
from app.services.google_drive_service import google_drive_service

# =====================================================
# API ROUTER
# =====================================================
router = APIRouter(prefix="/documentos", tags=["Documentos"])

# =====================================================
# LISTAR DOCUMENTOS
# =====================================================
@router.get("/", response_model=list[DocumentoResponse])
def listar_documentos(db: Session = Depends(get_db)):
    return documento_service.listar(db)


# =====================================================
# CRIAR DOCUMENTO
# =====================================================
@router.post("/", response_model=DocumentoResponse, status_code=status.HTTP_201_CREATED)
def criar_documento(dados: DocumentoCreate, db: Session = Depends(get_db)):
    try:
        return documento_service.criar(db, dados)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

# =====================================================
# UPLOAD (ASSÍNCRONO + THREADPOOL)
# =====================================================
@router.post(
    "/upload",
    response_model=DocumentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload(
    arquivo: UploadFile = File(...),
    parent_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if parent_id in ("", "null", "undefined", "string"):
        parent_id = None

    nome_arquivo = arquivo.filename or "arquivo_sem_nome"
    sufixo = os.path.splitext(nome_arquivo)[1]

    # ⚡ Gravação em blocos direto no disco (Zero pico de RAM)
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as temp:
        shutil.copyfileobj(arquivo.file, temp)
        caminho = temp.name

    try:
        print("=" * 80)
        print("UPLOAD RECEBIDO")
        print("Arquivo:", nome_arquivo)
        print("Parent:", parent_id)
        print("Temp:", caminho)
        print("=" * 80)

        documento = await run_in_threadpool(
            documento_service.upload,
            db=db,
            caminho_arquivo=caminho,
            nome=nome_arquivo,
            pasta_id=parent_id,
        )

        print("UPLOAD CONCLUÍDO")
        print(documento)

        return documento

    except RuntimeError as e:
        print("\nERRO RuntimeError")
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        print("\nERRO NÃO TRATADO")
        traceback.print_exc()

        if "File not found" in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"Pasta '{parent_id}' não encontrada no Google Drive.",
            )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if os.path.exists(caminho):
            os.remove(caminho)


# =====================================================
# SINCRONIZAR DRIVE (ASSÍNCRONO + THREADPOOL)
# =====================================================
@router.get("/sincronizar-drive")
async def sincronizar_com_google_drive(db: Session = Depends(get_db)):
    try:
        await run_in_threadpool(sync_service.sincronizacao_completa, db)
        return {"message": "Sincronização realizada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# RENOMEAR
# =====================================================
@router.patch("/{documento_id}/renomear", response_model=DocumentoResponse)
def renomear(documento_id: int, dados: DocumentoRenomear, db: Session = Depends(get_db)):
    try:
        return documento_service.renomear(
            db,
            documento_id,
            dados.novo_nome,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# ALTERAR DESCRIÇÃO
# =====================================================
@router.patch("/{documento_id}/descricao", response_model=DocumentoResponse)
def descricao(
    documento_id: int,
    dados: DocumentoDescricao,
    db: Session = Depends(get_db),
):
    try:
        return documento_service.alterar_descricao(
            db,
            documento_id,
            dados.descricao,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# FAVORITO
# =====================================================
@router.patch("/{documento_id}/favorito", response_model=DocumentoResponse)
def favorito(documento_id: int, dados: DocumentoFavorito, db: Session = Depends(get_db)):
    try:
        return documento_service.definir_favorito(
            db,
            documento_id,
            dados.favorito,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# MOVER
# =====================================================
@router.patch("/{documento_id}/mover", response_model=DocumentoResponse)
def mover(documento_id: int, dados: DocumentoMover, db: Session = Depends(get_db)):
    try:
        return documento_service.mover(
            db,
            documento_id,
            dados.pasta_destino,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# DOWNLOAD
# =====================================================
@router.get("/{documento_id}/download")
def download(documento_id: int, db: Session = Depends(get_db)):
    try:
        destino = tempfile.gettempdir()

        caminho = documento_service.download(
            db,
            documento_id,
            destino,
        )

        return FileResponse(
            path=caminho,
            filename=os.path.basename(caminho),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =========================================================================
# DOWNLOAD TEMPORÁRIO (Chamada pelo Electron)
# =========================================================================
@router.get("/{drive_file_id}/download-temp")
async def download_temp(drive_file_id: str):
    try:
        conteudo_bytes = await run_in_threadpool(
            google_drive_service.download_arquivo_bytes, drive_file_id
        )
        
        return Response(
            content=conteudo_bytes,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao buscar arquivo do Google Drive: {str(e)}"
        )


# =========================================================================
# SINCRONIZAÇÃO AUTOMÁTICA (Chamada no Ctrl + S do Electron)
# =========================================================================
@router.put("/{drive_file_id}/sincronizar")
async def sincronizar_documento(drive_file_id: str, file: UploadFile = File(...)):
    caminho_temp = None
    try:
        # ⚡ OTIMIZAÇÃO: Copia direto do stream do arquivo em disco sem subir pra RAM
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            caminho_temp = temp_file.name

        await run_in_threadpool(
            google_drive_service.atualizar_arquivo, drive_file_id, caminho_temp
        )

        return {"message": "Arquivo atualizado no Google Drive com sucesso!"}

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao sincronizar arquivo no Drive: {str(e)}"
        )

    finally:
        if caminho_temp and os.path.exists(caminho_temp):
            os.remove(caminho_temp)


# =====================================================
# BUSCAR DOCUMENTO POR ID
# =====================================================
@router.get("/{documento_id}", response_model=DocumentoResponse)
def buscar_documento(documento_id: int,db: Session = Depends(get_db),):
    try:
        return documento_service.buscar(
            db,
            documento_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# ATUALIZAR DOCUMENTO
# =====================================================
@router.put("/{documento_id}", response_model=DocumentoResponse)
def atualizar_documento(documento_id: int, dados: DocumentoUpdate, db: Session = Depends(get_db)):
    try:
        documento = documento_service.buscar(
            db,
            documento_id,
        )

        return documento_service.atualizar(
            db,
            documento,
            dados,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# EXCLUIR DOCUMENTO
# =====================================================
@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(documento_id: int,db: Session = Depends(get_db),):
    try:
        documento_service.excluir(
            db,
            documento_id,
        )
        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )