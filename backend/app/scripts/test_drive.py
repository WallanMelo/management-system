from fastapi import APIRouter
from app.services.google_drive_service import google_drive_service


router = APIRouter()


@router.get("/teste-drive")
def teste_drive():

    return google_drive_service.listar_root()