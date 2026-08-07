from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.auditoria import AuditoriaResponse
from app.services.auditoria import auditoria_service

router = APIRouter(prefix="/auditorias",tags=["Auditoria"],)

@router.get("/",response_model=list[AuditoriaResponse],)
def listar_auditorias(db: Session = Depends(get_db),):
    return auditoria_service.listar(db)

@router.get("/{auditoria_id}",response_model=AuditoriaResponse,)
def buscar_auditoria(auditoria_id: int,db: Session = Depends(get_db),):
    try:
        return auditoria_service.buscar(db, auditoria_id)
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e))