from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaResponse(BaseModel):
    id: int
    usuario_id: int | None
    documento_id: int | None
    acao: str
    ip: str | None
    observacao: str | None
    data_hora: datetime

    model_config = ConfigDict(from_attributes=True)