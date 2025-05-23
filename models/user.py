from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(String(50))
    
    # Esta relación es agregada por el backref en MovimientoInventario
    # movimientos_registrados = relationship("MovimientoInventario", back_populates="usuario")

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True)
