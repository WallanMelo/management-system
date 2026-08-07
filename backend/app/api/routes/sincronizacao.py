from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.sync_service import sync_service


router = APIRouter(
    prefix="/sincronizacao",
    tags=["Sincronização"]
)


@router.post("/completa")
def sincronizar_completa(db: Session = Depends(get_db)):

    sync_service.sincronizacao_completa(db)

    return {"mensagem": "Sincronização completa realizada com sucesso"}