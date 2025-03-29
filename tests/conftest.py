import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from config.database import Base, get_db
from models import User, Categoria, Proveedor, Ubicacion, Producto, Stock, TipoMovimiento, MovimientoInventario
from utils.utils import get_password_hash, create_access_token, SECRET_KEY, ALGORITHM

# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    try:
        # Primero cerrar todas las conexiones
        engine.dispose()
        # Luego intentar eliminar el archivo
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    except (PermissionError, OSError):
        # Si no podemos eliminar el archivo, simplemente lo ignoramos
        pass

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Crea una sesión de prueba para cada prueba"""
    connection = db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba para FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Reemplazar la dependencia get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar las sobreescrituras después de cada prueba
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def test_user(db_session):
    """Crea un usuario de prueba (role: user)"""
    # Primero verificar si ya existe
    existing_user = db_session.query(User).filter(User.username == "testuser").first()
    if existing_user:
        return existing_user
        
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("password123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db_session):
    """Crea un usuario administrador de prueba (role: admin)"""
    # Verificar si el admin ya existe
    existing_admin = db_session.query(User).filter(User.username == "testadmin").first()
    if existing_admin:
        return existing_admin
        
    admin = User(
        username="testadmin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("password123"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def token(test_user):
    """Genera un token JWT para el usuario de prueba"""
    expire = datetime.utcnow() + timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": test_user.username}, expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture(scope="function")
def admin_token(test_admin):
    """Genera un token JWT para el administrador"""
    access_token = create_access_token(
        data={"sub": test_admin.username}, expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture(scope="function")
def user_token(test_user):
    """Genera un token JWT para el usuario normal"""
    access_token = create_access_token(
        data={"sub": test_user.username}, expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture(scope="function")
def authorized_client(client, token):
    """Cliente con token de autenticación"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

# Fixtures para datos de prueba
@pytest.fixture(scope="function")
def test_categoria(db_session):
    # Verificar si ya existe
    existing = db_session.query(Categoria).filter(Categoria.nombre == "Categoría de Prueba").first()
    if existing:
        return existing
        
    categoria = Categoria(nombre="Categoría de Prueba", descripcion="Descripción de prueba")
    db_session.add(categoria)
    db_session.commit()
    db_session.refresh(categoria)
    return categoria

@pytest.fixture(scope="function")
def test_proveedor(db_session):
    # Verificar si ya existe
    existing = db_session.query(Proveedor).filter(Proveedor.nombre == "Proveedor de Prueba").first()
    if existing:
        return existing
        
    proveedor = Proveedor(
        nombre="Proveedor de Prueba", 
        contacto="Contacto de Prueba",
        telefono="123456789",
        email="proveedor@test.com",
        direccion="Dirección de prueba"
    )
    db_session.add(proveedor)
    db_session.commit()
    db_session.refresh(proveedor)
    return proveedor

@pytest.fixture(scope="function")
def test_ubicacion(db_session):
    # Verificar si ya existe
    existing = db_session.query(Ubicacion).filter(Ubicacion.nombre == "Ubicación de Prueba").first()
    if existing:
        return existing
        
    ubicacion = Ubicacion(
        nombre="Ubicación de Prueba",
        direccion="Dirección de ubicación de prueba",
        tipo="almacén"
    )
    db_session.add(ubicacion)
    db_session.commit()
    db_session.refresh(ubicacion)
    return ubicacion

@pytest.fixture(scope="function")
def test_producto(db_session, test_categoria, test_proveedor):
    # Verificar si ya existe
    existing = db_session.query(Producto).filter(Producto.codigo == "PROD001").first()
    if existing:
        return existing
        
    producto = Producto(
        codigo="PROD001",
        nombre="Producto de Prueba",
        descripcion="Descripción del producto de prueba",
        precio_compra=10.0,
        precio_venta=15.0,
        unidad_medida="unidad",
        stock_minimo=5,
        categoria_id=test_categoria.id,
        proveedor_id=test_proveedor.id
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    return producto

@pytest.fixture(scope="function")
def test_tipo_movimiento(db_session):
    # Verificar tipos de movimiento
    tipo_entrada = db_session.query(TipoMovimiento).filter(TipoMovimiento.codigo == "ENT").first()
    if not tipo_entrada:
        tipo_entrada = TipoMovimiento(
            codigo="ENT",
            nombre="Entrada",
            descripcion="Movimiento de entrada de inventario",
            afecta_stock="entrada"
        )
        db_session.add(tipo_entrada)
    
    tipo_salida = db_session.query(TipoMovimiento).filter(TipoMovimiento.codigo == "SAL").first()
    if not tipo_salida:
        tipo_salida = TipoMovimiento(
            codigo="SAL",
            nombre="Salida",
            descripcion="Movimiento de salida de inventario",
            afecta_stock="salida"
        )
        db_session.add(tipo_salida)
    
    db_session.commit()
    return tipo_entrada

@pytest.fixture(scope="function")
def test_stock(db_session, test_producto, test_ubicacion):
    # Verificar si ya existe
    existing = db_session.query(Stock).filter(
        Stock.producto_id == test_producto.id,
        Stock.ubicacion_id == test_ubicacion.id
    ).first()
    if existing:
        return existing
        
    stock = Stock(
        producto_id=test_producto.id,
        ubicacion_id=test_ubicacion.id,
        cantidad=100.0
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock 