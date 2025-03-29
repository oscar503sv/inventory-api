from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config.database import Base

class Ubicacion(Base):
    __tablename__ = 'ubicaciones'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True)
    direccion = Column(String(255), nullable=True)
    tipo = Column(String(50), nullable=True)  # almacén, tienda, etc.
    activo = Column(Boolean, default=True)
    
    # Relaciones
    stocks = relationship("Stock", back_populates="ubicacion")
    movimientos_destino = relationship("MovimientoInventario", foreign_keys="MovimientoInventario.ubicacion_destino_id", back_populates="ubicacion_destino")
    movimientos_origen = relationship("MovimientoInventario", foreign_keys="MovimientoInventario.ubicacion_origen_id", back_populates="ubicacion_origen") 