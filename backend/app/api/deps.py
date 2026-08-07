from typing import Generator

from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from app.core.security import verificar_token

from app.repositories.usuario import usuario_repository

from app.models.usuario import Usuario
from app.models.enums import PerfilUsuario

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_db() -> Generator[Session, None, None]:
    """
    Cria uma sessão com o banco de dados e a fecha automaticamente
    ao final da requisição.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):

    payload = verificar_token(token)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido.")

    usuario_id = payload.get("sub")

    if usuario_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido.")

    usuario = usuario_repository.buscar_por_id(db,int(usuario_id))

    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Usuário desativado.")
    return usuario

def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil != PerfilUsuario.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Apenas administradores possuem acesso.")
    return usuario


def require_admin_or_estagiario(
    usuario: Usuario = Depends(get_current_user)
) -> Usuario:

    if usuario.perfil not in (
        PerfilUsuario.ADMIN,
        PerfilUsuario.ESTAGIARIO
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente."
        )

    return usuario

def require_authenticated(
    usuario: Usuario = Depends(get_current_user)
) -> Usuario:
    return usuario