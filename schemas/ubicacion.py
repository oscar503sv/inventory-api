from pydantic import BaseModel
from typing import Optional

class UbicacionBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = True

    class Config:
        from_attributes = True

class UbicacionCreate(UbicacionBase):
    pass

class UbicacionUpdate(UbicacionBase):
    nombre: Optional[str] = None
    activo: Optional[bool] = None

class UbicacionResponse(UbicacionBase):
    id: int

    class Config:
        from_attributes = True 