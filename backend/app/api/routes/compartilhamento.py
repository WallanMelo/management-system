from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db

from app.schemas.compartilhamento import (
    CompartilhamentoCreate,
    CompartilhamentoResponse,
)

from app.services.compartilhamento import (compartilhamento_service,)

router = APIRouter(prefix="/compartilhamentos",tags=["Compartilhamentos"],)

@router.get("/",response_model=list[CompartilhamentoResponse],)
def listar_compartilhamentos(db: Session = Depends(get_db),):
    return compartilhamento_service.listar(db)


@router.post("/",response_model=CompartilhamentoResponse,status_code=status.HTTP_201_CREATED,)
def criar_compartilhamento(dados: CompartilhamentoCreate,db: Session = Depends(get_db),):
    try:
        return compartilhamento_service.criar(db,dados,)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e),)


@router.delete("/{compartilhamento_id}",status_code=status.HTTP_204_NO_CONTENT,)
def excluir_compartilhamento(compartilhamento_id: int,db: Session = Depends(get_db),):
    try:
        compartilhamento_service.excluir(db,compartilhamento_id,)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e),)
    return None