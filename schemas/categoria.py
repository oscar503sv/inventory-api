from pydantic import BaseModel
from typing import Optional

class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    nombre: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True 