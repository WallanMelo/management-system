from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import PerfilUsuario


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    senha: str | None = None
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class UsuarioResponse(UsuarioBase):
    id: int
    ultimo_login: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str