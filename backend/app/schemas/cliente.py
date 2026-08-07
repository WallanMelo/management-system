from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class ClienteBase(BaseModel):
    nome: str
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    observacao: str | None = None
    ativo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = None
    cpf_cnpj: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    observacao: str | None = None
    ativo: bool | None = None


class ClienteResponse(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)