from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.enums import TemaSistema


class ConfiguracaoBase(BaseModel):
    nome_empresa: str
    cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    logo: str | None = None
    pasta_drive: str
    tema: TemaSistema
    backup_automatico: bool = True


class ConfiguracaoUpdate(ConfiguracaoBase):
    pass

class ConfiguracaoResponse(ConfiguracaoBase):
    id: int

    start_page_token: str | None

    ultima_sincronizacao: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)