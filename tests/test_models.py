import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from models import User, Categoria, Proveedor, Ubicacion, Producto, Stock, TipoMovimiento, MovimientoInventario

# Tests para el modelo User
def test_user_model(db_session):
    # Crear un usuario de prueba
    user = User(
        username="testmodel",
        email="testmodel@example.com",
        first_name="Test",
        last_name="Model",
        hashed_password="hashed_password",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    
    # Recuperar el usuario y verificar sus atributos
    saved_user = db_session.query(User).filter(User.username == "testmodel").first()
    assert saved_user.username == "testmodel"
    assert saved_user.email == "testmodel@example.com"
    assert saved_user.first_name == "Test"
    assert saved_user.last_name == "Model"
    assert saved_user.hashed_password == "hashed_password"
    assert saved_user.role == "admin"

def test_user_unique_username(db_session):
    # Crear un usuario para la prueba
    user1 = User(
        username="user_unique_test1",
        email="user_unique1@example.com",
        first_name="Test",
        last_name="Unique",
        hashed_password="password_hash",
        role="user"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Intentar crear un usuario con el mismo username
    duplicate_user = User(
        username="user_unique_test1",  # Duplicado
        email="otro@example.com",
        first_name="Otro",
        last_name="Usuario",
        hashed_password="otra_contraseña",
        role="user"
    )

    with pytest.raises(IntegrityError):
        db_session.add(duplicate_user)
        db_session.commit()

    db_session.rollback()

def test_user_unique_email(db_session):
    # Crear un usuario para la prueba
    user1 = User(
        username="user_unique_test2",
        email="user_unique2@example.com",
        first_name="Test",
        last_name="Unique",
        hashed_password="password_hash",
        role="user"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Intentar crear un usuario con el mismo email
    duplicate_email = User(
        username="otrousuario",
        email="user_unique2@example.com",  # Duplicado
        first_name="Otro",
        last_name="Usuario",
        hashed_password="otra_contraseña",
        role="user"
    )

    with pytest.raises(IntegrityError):
        db_session.add(duplicate_email)
        db_session.commit()

    db_session.rollback()

# Tests para el modelo Categoria
def test_categoria_model(db_session):
    categoria = Categoria(
        nombre="Categoría de Test",
        descripcion="Descripción de la categoría de test"
    )
    db_session.add(categoria)
    db_session.commit()
    
    saved_categoria = db_session.query(Categoria).filter(Categoria.nombre == "Categoría de Test").first()
    assert saved_categoria.nombre == "Categoría de Test"
    assert saved_categoria.descripcion == "Descripción de la categoría de test"

def test_categoria_unique_constraints(db_session, test_categoria):
    # Intentar crear una categoría con el mismo nombre
    duplicate_categoria = Categoria(
        nombre=test_categoria.nombre,  # Duplicado
        descripcion="Otra descripción"
    )
    
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_categoria)
        db_session.commit()

# Tests para el modelo Producto
def test_producto_model(db_session, test_categoria, test_proveedor):
    producto = Producto(
        codigo="TEST001",
        nombre="Producto Test",
        descripcion="Descripción del producto test",
        precio_compra=50.0,
        precio_venta=75.0,
        unidad_medida="unidad",
        stock_minimo=10,
        categoria_id=test_categoria.id,
        proveedor_id=test_proveedor.id
    )
    db_session.add(producto)
    db_session.commit()
    
    saved_producto = db_session.query(Producto).filter(Producto.codigo == "TEST001").first()
    assert saved_producto.codigo == "TEST001"
    assert saved_producto.nombre == "Producto Test"
    assert saved_producto.precio_compra == 50.0
    assert saved_producto.precio_venta == 75.0
    assert saved_producto.categoria_id == test_categoria.id
    assert saved_producto.proveedor_id == test_proveedor.id

def test_producto_unique_constraints(db_session, test_producto):
    # Intentar crear un producto con el mismo código
    duplicate_producto = Producto(
        codigo=test_producto.codigo,  # Duplicado
        nombre="Otro Producto",
        categoria_id=test_producto.categoria_id
    )
    
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_producto)
        db_session.commit()

# Test para el modelo Stock
def test_stock_model(db_session, test_producto, test_ubicacion):
    stock = Stock(
        producto_id=test_producto.id,
        ubicacion_id=test_ubicacion.id,
        cantidad=200.0
    )
    db_session.add(stock)
    db_session.commit()
    
    saved_stock = db_session.query(Stock).filter(
        Stock.producto_id == test_producto.id,
        Stock.ubicacion_id == test_ubicacion.id
    ).first()
    
    assert saved_stock.cantidad == 200.0
    assert saved_stock.producto_id == test_producto.id
    assert saved_stock.ubicacion_id == test_ubicacion.id

# Test para el modelo MovimientoInventario
def test_movimiento_inventario_model(db_session, test_producto, test_ubicacion, test_tipo_movimiento, test_user):
    movimiento = MovimientoInventario(
        fecha=datetime.now(),
        cantidad=50.0,
        referencia="REF001",
        observaciones="Observaciones de prueba",
        tipo_movimiento_id=test_tipo_movimiento.id,
        producto_id=test_producto.id,
        ubicacion_destino_id=test_ubicacion.id,
        usuario_id=test_user.id
    )
    db_session.add(movimiento)
    db_session.commit()
    
    saved_movimiento = db_session.query(MovimientoInventario).filter(
        MovimientoInventario.referencia == "REF001"
    ).first()
    
    assert saved_movimiento.cantidad == 50.0
    assert saved_movimiento.tipo_movimiento_id == test_tipo_movimiento.id
    assert saved_movimiento.producto_id == test_producto.id
    assert saved_movimiento.ubicacion_destino_id == test_ubicacion.id
    assert saved_movimiento.usuario_id == test_user.id

# Test para relaciones entre modelos
def test_relaciones_producto(db_session, test_producto, test_categoria, test_proveedor):
    # Verificar relación con categoría
    assert test_producto.categoria.id == test_categoria.id
    assert test_producto.categoria.nombre == test_categoria.nombre
    
    # Verificar relación con proveedor
    assert test_producto.proveedor.id == test_proveedor.id
    assert test_producto.proveedor.nombre == test_proveedor.nombre
    
    # Verificar relación inversa (categoría -> productos)
    assert test_categoria.productos[0].id == test_producto.id
    
    # Verificar relación inversa (proveedor -> productos)
    assert test_proveedor.productos[0].id == test_producto.id

def test_relaciones_stock(db_session, test_stock, test_producto, test_ubicacion):
    # Verificar relación con producto
    assert test_stock.producto.id == test_producto.id
    assert test_stock.producto.nombre == test_producto.nombre
    
    # Verificar relación con ubicación
    assert test_stock.ubicacion.id == test_ubicacion.id
    assert test_stock.ubicacion.nombre == test_ubicacion.nombre
    
    # Verificar relación inversa (producto -> stocks)
    assert test_producto.stocks[0].id == test_stock.id
    
    # Verificar relación inversa (ubicación -> stocks)
    assert test_ubicacion.stocks[0].id == test_stock.id 