from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class MovimientoInventario(Base):
    __tablename__ = 'movimientos_inventario'

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now)
    cantidad = Column(Float(precision=2), nullable=False)
    referencia = Column(String(50), nullable=True)  # Número de documento relacionado
    observaciones = Column(Text, nullable=True)
    
    # Claves foráneas
    tipo_movimiento_id = Column(Integer, ForeignKey("tipos_movimiento.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    ubicacion_origen_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=True)  # Para transferencias o salidas
    ubicacion_destino_id = Column(Integer, ForeignKey("ubicaciones.id"), nullable=True)  # Para transferencias o entradas
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Quién registró el movimiento
    
    # Relaciones
    tipo_movimiento = relationship("TipoMovimiento", back_populates="movimientos")
    producto = relationship("Producto", back_populates="movimientos")
    ubicacion_origen = relationship("Ubicacion", foreign_keys=[ubicacion_origen_id], back_populates="movimientos_origen")
    ubicacion_destino = relationship("Ubicacion", foreign_keys=[ubicacion_destino_id], back_populates="movimientos_destino") 
    usuario = relationship("User", backref="movimientos_registrados") 