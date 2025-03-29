from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True)
    nombre = Column(String(100), index=True)
    descripcion = Column(Text, nullable=True)
    precio_compra = Column(Float(precision=2), nullable=True)
    precio_venta = Column(Float(precision=2), nullable=True)
    unidad_medida = Column(String(20), nullable=True)  # unidad, kg, litro, etc.
    stock_minimo = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    
    # Claves foráneas
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    stocks = relationship("Stock", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto") 