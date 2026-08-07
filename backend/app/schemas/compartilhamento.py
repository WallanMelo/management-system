from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompartilhamentoBase(BaseModel):
    documento_id: int
    usuario_id: int
    visualizar: bool = True
    download: bool = True


class CompartilhamentoCreate(CompartilhamentoBase):
    pass


class CompartilhamentoResponse(CompartilhamentoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)