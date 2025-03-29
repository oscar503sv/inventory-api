from pydantic import BaseModel
from typing import Optional, Union, List

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[int] = 0
    activo: Optional[bool] = True
    categoria_id: int
    proveedor_id: Optional[int] = None

    class Config:
        from_attributes = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None

class ProductoResponse(ProductoBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductoDetalleResponse(ProductoResponse):
    categoria: 'CategoriaResponse'
    proveedor: Optional['ProveedorResponse'] = None
    stock_total: Optional[float] = 0
    
    class Config:
        from_attributes = True

# Para evitar referencias circulares
from schemas.categoria import CategoriaResponse
from schemas.proveedor import ProveedorResponse 