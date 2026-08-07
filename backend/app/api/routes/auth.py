
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.usuario import UsuarioLogin
from app.services.usuario import usuario_service
from app.core.security import criar_access_token

from app.api.deps import get_current_user
from app.schemas.usuario import UsuarioResponse
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/login")
def login(
    dados: UsuarioLogin,
    db: Session = Depends(get_db)
):

    usuario = usuario_service.autenticar(
        db,
        dados.email,
        dados.senha
    )

    if not usuario:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos."
        )

    usuario_service.atualizar_ultimo_login(db,usuario)

    db.commit()

    token = criar_access_token(
        {
            "sub": str(usuario.id),
            "perfil": usuario.perfil.value
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=UsuarioResponse
)
def me(
    usuario: Usuario = Depends(get_current_user)
):
    """
    Retorna os dados do usuário autenticado.
    """
    return usuario