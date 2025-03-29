from pydantic import BaseModel
from typing import Optional, Literal

class TipoMovimientoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    afecta_stock: Literal["entrada", "salida", "ninguno"]

    class Config:
        from_attributes = True

class TipoMovimientoCreate(TipoMovimientoBase):
    pass

class TipoMovimientoUpdate(TipoMovimientoBase):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    afecta_stock: Optional[Literal["entrada", "salida", "ninguno"]] = None

class TipoMovimientoResponse(TipoMovimientoBase):
    id: int
    
    class Config:
        from_attributes = True 