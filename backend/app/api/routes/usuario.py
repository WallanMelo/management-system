from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario

from app.api.deps import get_db, require_admin, require_authenticated

from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    AlterarSenhaRequest
)

from app.services.usuario import usuario_service

# API ROUTER
router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# ==========================================
# ROTAS DO USUÁRIO LOGADO (ME)
# ==========================================

@router.get("/me", response_model=UsuarioResponse)
def obter_meu_perfil(current_user: Usuario = Depends(require_authenticated)):
    """Retorna os dados do usuário atualmente logado"""
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def atualizar_meu_perfil(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_authenticated)
):
    """Atualiza os dados do próprio usuário logado"""
    try:
        return usuario_service.atualizar(db, current_user, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/alterar-senha", status_code=status.HTTP_200_OK)
def alterar_minha_senha(
    dados: AlterarSenhaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_authenticated)
):
    """Altera a senha do usuário logado"""
    try:
        return usuario_service.alterar_senha(db, current_user, dados.senha_atual, dados.nova_senha)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==========================================
# GERENCIAMENTO DE USUÁRIOS
# ==========================================

# 🟢 Qualquer usuário autenticado pode listar (Resolve o Dashboard e a visualização)
@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_authenticated) # 👈 ALTERADO AQUI
):
    return usuario_service.listar(db)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse
)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_authenticated)):
    try:
        return usuario_service.buscar(db, usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# 🔴 APENAS ADMINISTRADOR pode Criar
@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    try:
        return usuario_service.criar(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# 🔴 APENAS ADMINISTRADOR pode Editar / Alterar Status
@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse
)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    try:
        usuario = usuario_service.buscar(db, usuario_id)
        return usuario_service.atualizar(db, usuario, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# 🔴 APENAS ADMINISTRADOR pode Excluir
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    try:
        usuario = usuario_service.buscar(db, usuario_id)
        usuario_service.excluir(db, usuario)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    