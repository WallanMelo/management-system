from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db

from app.schemas.configuracao import (
    ConfiguracaoUpdate,
    ConfiguracaoResponse,
)

from app.services.configuracao import configuracao_service

#API ROUTER
router = APIRouter(prefix="/configuracoes",tags=["Configurações"],)

@router.get("/",response_model=ConfiguracaoResponse,)
def obter_configuracao(db: Session = Depends(get_db),):
    try:
        return configuracao_service.obter(db)
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e),)
    
@router.put("/",response_model=ConfiguracaoResponse,)
def atualizar_configuracao(dados: ConfiguracaoUpdate,db: Session = Depends(get_db),):
    try:
        configuracao = configuracao_service.obter(db)
        return configuracao_service.atualizar(db,configuracao,dados,)

    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e),)
    
@router.post(
    "/",
    response_model=ConfiguracaoResponse,
    status_code=201,
)
def criar_configuracao(dados: ConfiguracaoUpdate,db: Session = Depends(get_db),):
    try:
        return configuracao_service.criar(db,dados,)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e),)