from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(255), nullable=True)
    
    # Relación con productos
    productos = relationship("Producto", back_populates="proveedor") 