from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

class MovimientoInventarioBase(BaseModel):
    cantidad: float
    tipo_movimiento_id: int
    producto_id: int
    referencia: Optional[str] = None
    observaciones: Optional[str] = None
    ubicacion_origen_id: Optional[int] = None
    ubicacion_destino_id: Optional[int] = None

    class Config:
        from_attributes = True

class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass

class MovimientoInventarioUpdate(MovimientoInventarioBase):
    cantidad: Optional[float] = None
    tipo_movimiento_id: Optional[int] = None
    producto_id: Optional[int] = None

class MovimientoInventarioResponse(MovimientoInventarioBase):
    id: int
    fecha: datetime
    usuario_id: int
    
    class Config:
        from_attributes = True

class MovimientoInventarioDetalleResponse(MovimientoInventarioResponse):
    tipo_movimiento: 'TipoMovimientoResponse'
    producto: 'ProductoResponse'
    ubicacion_origen: Optional['UbicacionResponse'] = None
    ubicacion_destino: Optional['UbicacionResponse'] = None
    usuario: 'UserResponse'
    
    class Config:
        from_attributes = True

# Para evitar referencias circulares
from schemas.tipo_movimiento import TipoMovimientoResponse
from schemas.producto import ProductoResponse
from schemas.ubicacion import UbicacionResponse
from schemas.user import UserResponse 