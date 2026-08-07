from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.diretorio import (
    DiretorioResponse, CriarPasta, RenomearPasta, MoverPasta
)
from app.services.diretorio import diretorio_service

from fastapi.responses import StreamingResponse # 👈 NOVA IMPORTAÇÃO
import urllib.parse # 👈 NOVA IMPORTAÇÃO (Para formatar o nome do arquivo com espaços/acentos)
from app.services.google_drive_service import google_drive_service
import os
from app.core.config import settings

# ========= API ROUTER ================================
router = APIRouter(prefix="/diretorios", tags=["Diretórios"])


# =====================================================
# LISTAR CONTEÚDO DA PASTA
# =====================================================
@router.get("/conteudo")
@router.get("/conteudo/{parent_id}")
def listar_conteudo(parent_id: str | None = None, db: Session = Depends(get_db)):
    resposta = diretorio_service.listar_conteudo(db, parent_id)
    dados = resposta if isinstance(resposta, dict) else resposta.dict()

    if "pasta_raiz" not in dados or not dados["pasta_raiz"]:
        try:
            # Busca o ID da variável GOOGLE_DRIVE_ROOT_FOLDER_ID do .env / settings
            folder_id = (
                getattr(settings, "GOOGLE_DRIVE_ROOT_FOLDER_ID", None)
                or getattr(settings, "google_drive_root_folder_id", None)
                or os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
            )

            if folder_id:
                folder_id = folder_id.strip()

                # Busca os dados da pasta diretamente na API do Drive
                info_pasta = google_drive_service.buscar_arquivo(folder_id)

                dados["pasta_raiz"] = {
                    "id": folder_id,
                    "nome": info_pasta.get("name", "Meu Drive"),
                }
            else:
                dados["pasta_raiz"] = {"nome": "Meu Drive"}

        except Exception as e:
            print(f"❌ Erro ao buscar nome da pasta raiz no Drive: {e}")
            dados["pasta_raiz"] = {"nome": "Meu Drive"}

    return dados

# =====================================================
# LISTAR TODAS AS PASTAS
# =====================================================
@router.get("/", response_model=list[DiretorioResponse])
def listar(db: Session = Depends(get_db)):
    return diretorio_service.listar(db)

# =====================================================
# CRIAR PASTA
# =====================================================
@router.post(
    "/criar",
    response_model=DiretorioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar(
    dados: CriarPasta,
    db: Session = Depends(get_db),
):
    return diretorio_service.criar_pasta(
        db,
        dados.nome,
        dados.parent_id,
    )

# =====================================================
# RENOMEAR
# =====================================================
@router.patch("/{id}/renomear")
def renomear(id: int, dados: RenomearPasta, db: Session = Depends(get_db)):
    return diretorio_service.renomear(db, id, dados.nome)

# =====================================================
# MOVER
# =====================================================
@router.patch("/{id}/mover")
def mover(id: int, dados: MoverPasta, db: Session = Depends(get_db)):
    return diretorio_service.mover(db, id, dados.pasta_destino)

# =====================================================
# EXCLUIR
# =====================================================
@router.delete("/{diretorio_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(diretorio_id: int, db: Session = Depends(get_db)):
    diretorio_service.excluir(db, diretorio_id)
    return None

# =====================================================
# DOWNLOAD DE PASTA (.ZIP)
# =====================================================
@router.get("/{diretorio_id}/download")
def baixar_pasta(diretorio_id: int, db: Session = Depends(get_db)):
    try:
        # O service vai retornar o buffer (em memória) do zip e o nome da pasta
        zip_buffer, nome_pasta = diretorio_service.baixar_pasta_zip(db, diretorio_id)
        
        # Formata o nome do arquivo para aceitar acentos e espaços no navegador
        nome_seguro = urllib.parse.quote(f"{nome_pasta}.zip")
        
        return StreamingResponse(
            zip_buffer, 
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{nome_seguro}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ZIP: {str(e)}")

# =====================================================
# BUSCAR UMA PASTA POR ID (Sempre no final das rotas GET)
# =====================================================
@router.get("/{diretorio_id}", response_model=DiretorioResponse)
def buscar(diretorio_id: int, db: Session = Depends(get_db)):
    try:
        return diretorio_service.buscar(db, diretorio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))