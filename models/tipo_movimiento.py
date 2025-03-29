from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class TipoMovimiento(Base):
    __tablename__ = 'tipos_movimiento'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True)
    nombre = Column(String(100), unique=True)
    descripcion = Column(String(255), nullable=True)
    afecta_stock = Column(String(10), nullable=False)  # "entrada", "salida", "ninguno"
    
    # Relación con movimientos de inventario
    movimientos = relationship("MovimientoInventario", back_populates="tipo_movimiento") 