from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.cliente import (ClienteCreate,ClienteUpdate,ClienteResponse,)
from app.services.cliente import cliente_service

router = APIRouter(prefix="/clientes",tags=["Clientes"],)

# ==========================================================
# LISTAR
# ==========================================================
@router.get("/",response_model=list[ClienteResponse],)
def listar_clientes(db: Session = Depends(get_db),):
    return cliente_service.listar(db)


# ==========================================================
# BUSCAR
# ==========================================================
@router.get("/{cliente_id}",response_model=ClienteResponse,)
def buscar_cliente(cliente_id: int,db: Session = Depends(get_db),):
    try:
        return cliente_service.buscar(db, cliente_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==========================================================
# CRIAR
# ==========================================================
@router.post("/",response_model=ClienteResponse,status_code=status.HTTP_201_CREATED,)
def criar_cliente(dados: ClienteCreate,db: Session = Depends(get_db),):
    try:
        return cliente_service.criar(db, dados)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# ATUALIZAR
# ==========================================================
@router.put("/{cliente_id}",response_model=ClienteResponse,)
def atualizar_cliente(cliente_id: int,dados: ClienteUpdate,db: Session = Depends(get_db),):
    try:
        cliente = cliente_service.buscar(db, cliente_id)
        return cliente_service.atualizar(db,cliente,dados,)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e),)


# ==========================================================
# EXCLUIR
# ==========================================================
@router.delete("/{cliente_id}",status_code=status.HTTP_204_NO_CONTENT,)
def excluir_cliente(cliente_id: int,db: Session = Depends(get_db),):
    try:
        cliente = cliente_service.buscar(db, cliente_id)
        cliente_service.excluir(db,cliente,)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e),)
    return None