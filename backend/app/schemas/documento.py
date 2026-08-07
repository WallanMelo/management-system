from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =====================================================
# BASE
# =====================================================

class DocumentoBase(BaseModel):
    cliente_id: int | None = None
    diretorio_id: int | None = None
    descricao: str | None = None
    favorito: bool = False
    ativo: bool = True


# =====================================================
# CRUD
# =====================================================

class DocumentoCreate(DocumentoBase):
    pass


class DocumentoUpdate(BaseModel):
    descricao: str | None = None
    favorito: bool | None = None
    ativo: bool | None = None


# =====================================================
# OPERAÇÕES
# =====================================================

class DocumentoRenomear(BaseModel):
    novo_nome: str


class DocumentoMover(BaseModel):
    pasta_destino: str


class DocumentoDescricao(BaseModel):
    descricao: str


class DocumentoFavorito(BaseModel):
    favorito: bool


# =====================================================
# RESPONSE
# =====================================================

class DocumentoResponse(DocumentoBase):

    id: int

    usuario_upload: int | None = None

    nome_original: str

    nome_sistema: str

    drive_file_id: str | None = None

    drive_parent_id: str | None = None

    mime_type: str | None = None

    tamanho: int | None = None

    hash: str | None = None

    versao: int = 1

    sincronizado: bool = False

    modified_time: datetime | None = None

    created_at: datetime | None = None

    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)