from fastapi import HTTPException, status

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# BCrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# Senhas
def gerar_hash_senha(senha: str) -> str:
    # Garante limite máximo de 72 bytes suportado pelo algoritmo bcrypt
    senha_cortada = senha.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(senha_cortada)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    #Verifica se a senha informa corresponde com o hash
    return pwd_context.verify(senha, senha_hash)


# JWT
def criar_access_token(data: dict[str,Any]) -> str:
    #Gera um Token de Aesso JWT
    dados = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    dados.update({"exp":expire})

    return jwt.encode(dados,settings.secret_key,algorithm=settings.algorithm)


def verificar_token(
    token: str
) -> dict[str, Any] | None:
    """
    Decodifica um JWT.
    Retorna None caso seja inválido.
    """
    try:
        payload = jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None

def get_user_id_from_token(token: str) -> int:
    payload = verificar_token(token)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido.")
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido.")
    return int(user_id)

#Criar essa função posteriormente
#def get_user_profile(token: str) -> str: