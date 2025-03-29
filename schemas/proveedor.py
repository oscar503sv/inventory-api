from pydantic import BaseModel, EmailStr
from typing import Optional

class ProveedorBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None

    class Config:
        from_attributes = True

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(ProveedorBase):
    nombre: Optional[str] = None

class ProveedorResponse(ProveedorBase):
    id: int

    class Config:
        from_attributes = True 