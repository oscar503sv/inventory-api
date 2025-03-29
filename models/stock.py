from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from config.database import Base

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Float(precision=2), default=0)
    
    # Claves foráneas
    producto_id = Column(Integer, ForeignKey("productos.id"))
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"))
    
    # Relaciones
    producto = relationship("Producto", back_populates="stocks")
    ubicacion = relationship("Ubicacion", back_populates="stocks")
    
    # Asegurar que la combinación producto-ubicación sea única
    __table_args__ = (
        UniqueConstraint('producto_id', 'ubicacion_id', name='uix_producto_ubicacion'),
    ) 