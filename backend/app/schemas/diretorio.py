from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DiretorioBase(BaseModel):
    cliente_id: int
    diretorio_pai_id: int | None = None
    nome: str
    drive_folder_id: str | None = None

class DiretorioCreate(DiretorioBase):
    pass

class CriarPasta(BaseModel):
    nome: str
    parent_id: str | None = None

class RenomearPasta(BaseModel):
    nome: str

class MoverPasta(BaseModel):
    pasta_destino: str

class DiretorioUpdate(BaseModel):
    nome: str | None = None
    diretorio_pai_id: int | None = None

class DiretorioResponse(BaseModel):
    id: int
    nome: str
    cliente_id: int | None
    diretorio_pai_id: int | None
    drive_folder_id: str | None
    drive_parent_id: str | None
    sincronizado: bool
    modified_time: datetime | None
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)