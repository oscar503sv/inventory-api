from pydantic import BaseModel
from typing import Optional

class StockBase(BaseModel):
    cantidad: float
    producto_id: int
    ubicacion_id: int

    class Config:
        from_attributes = True

class StockCreate(StockBase):
    pass

class StockUpdate(StockBase):
    cantidad: Optional[float] = None
    producto_id: Optional[int] = None
    ubicacion_id: Optional[int] = None

class StockResponse(StockBase):
    id: int
    
    class Config:
        from_attributes = True

class StockDetalleResponse(StockResponse):
    producto: 'ProductoResponse'
    ubicacion: 'UbicacionResponse'
    
    class Config:
        from_attributes = True

# Para evitar referencias circulares
from schemas.producto import ProductoResponse
from schemas.ubicacion import UbicacionResponse 