import pytest
from fastapi import status
from datetime import datetime, timedelta

# Test para crear un movimiento de entrada
def test_create_movimiento_entrada(authorized_client, test_producto, test_ubicacion, test_tipo_movimiento):
    # Asegurarse de que el tipo de movimiento sea de entrada
    tipo_response = authorized_client.get(f"/tipos-movimiento/{test_tipo_movimiento.id}")
    tipo_data = tipo_response.json()
    if tipo_data["afecta_stock"] != "entrada":
        # Crear un tipo de movimiento de entrada
        tipo_response = authorized_client.post(
            "/tipos-movimiento/",
            json={
                "codigo": "ENT",
                "nombre": "Entrada Test",
                "afecta_stock": "entrada"
            }
        )
        assert tipo_response.status_code == status.HTTP_200_OK
        tipo_movimiento_id = tipo_response.json()["id"]
    else:
        tipo_movimiento_id = test_tipo_movimiento.id
    
    # Crear un movimiento de entrada
    response = authorized_client.post(
        "/movimientos/",
        json={
            "cantidad": 50.0,
            "referencia": "REF-TEST-001",
            "observaciones": "Movimiento de prueba",
            "tipo_movimiento_id": tipo_movimiento_id,
            "producto_id": test_producto.id,
            "ubicacion_destino_id": test_ubicacion.id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cantidad"] == 50.0
    assert data["referencia"] == "REF-TEST-001"
    assert data["tipo_movimiento_id"] == tipo_movimiento_id
    assert data["producto_id"] == test_producto.id
    assert data["ubicacion_destino_id"] == test_ubicacion.id
    assert "id" in data
    
    # Verificar que el stock se haya incrementado
    stock_response = authorized_client.get("/stocks/", params={
        "producto_id": test_producto.id,
        "ubicacion_id": test_ubicacion.id
    })
    assert stock_response.status_code == status.HTTP_200_OK
    stocks = stock_response.json()
    assert len(stocks) > 0
    
    # El stock debe haberse incrementado en 50
    found = False
    for stock in stocks:
        if stock["producto_id"] == test_producto.id and stock["ubicacion_id"] == test_ubicacion.id:
            assert stock["cantidad"] >= 50.0
            found = True
            break
    assert found, "No se encontró el stock actualizado"

def test_create_movimiento_salida(authorized_client, test_producto, test_ubicacion, test_stock):
    # Crear un tipo de movimiento de salida
    tipo_response = authorized_client.post(
        "/tipos-movimiento/",
        json={
            "codigo": "SAL",
            "nombre": "Salida Test",
            "afecta_stock": "salida"
        }
    )
    assert tipo_response.status_code == status.HTTP_200_OK
    tipo_movimiento_id = tipo_response.json()["id"]
    
    # Verificar el stock actual
    cantidad_inicial = test_stock.cantidad
    assert cantidad_inicial > 0, "El stock debe ser mayor a 0 para la prueba"
    
    # Crear un movimiento de salida
    cantidad_salida = min(25.0, cantidad_inicial / 2)  # Asegurar que no supere el stock disponible
    response = authorized_client.post(
        "/movimientos/",
        json={
            "cantidad": cantidad_salida,
            "referencia": "REF-TEST-002",
            "observaciones": "Movimiento de salida de prueba",
            "tipo_movimiento_id": tipo_movimiento_id,
            "producto_id": test_producto.id,
            "ubicacion_origen_id": test_ubicacion.id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cantidad"] == cantidad_salida
    assert data["referencia"] == "REF-TEST-002"
    assert data["tipo_movimiento_id"] == tipo_movimiento_id
    assert data["producto_id"] == test_producto.id
    assert data["ubicacion_origen_id"] == test_ubicacion.id
    
    # Verificar que el stock se haya reducido
    stock_response = authorized_client.get("/stocks/", params={
        "producto_id": test_producto.id,
        "ubicacion_id": test_ubicacion.id
    })
    assert stock_response.status_code == status.HTTP_200_OK
    stocks = stock_response.json()
    assert len(stocks) > 0
    
    # El stock debe haberse reducido en cantidad_salida
    found = False
    for stock in stocks:
        if stock["producto_id"] == test_producto.id and stock["ubicacion_id"] == test_ubicacion.id:
            assert stock["cantidad"] == pytest.approx(cantidad_inicial - cantidad_salida)
            found = True
            break
    assert found, "No se encontró el stock actualizado"

def test_create_movimiento_stock_insuficiente(authorized_client, test_producto, test_ubicacion):
    # Crear un tipo de movimiento de salida
    tipo_response = authorized_client.post(
        "/tipos-movimiento/",
        json={
            "codigo": "SAL2",
            "nombre": "Salida Test 2",
            "afecta_stock": "salida"
        }
    )
    assert tipo_response.status_code == status.HTTP_200_OK
    tipo_movimiento_id = tipo_response.json()["id"]
    
    # Crear una ubicación nueva (que no tendrá stock)
    ubicacion_response = authorized_client.post(
        "/ubicaciones/",
        json={
            "nombre": "Ubicación sin stock",
            "tipo": "almacén"
        }
    )
    assert ubicacion_response.status_code == status.HTTP_200_OK
    ubicacion_id = ubicacion_response.json()["id"]
    
    # Intentar crear un movimiento de salida con stock insuficiente
    response = authorized_client.post(
        "/movimientos/",
        json={
            "cantidad": 100.0,
            "referencia": "REF-TEST-003",
            "observaciones": "Movimiento que debería fallar",
            "tipo_movimiento_id": tipo_movimiento_id,
            "producto_id": test_producto.id,
            "ubicacion_origen_id": ubicacion_id  # Ubicación sin stock
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "stock insuficiente" in response.json()["detail"].lower()

# Test para obtener movimientos
def test_read_movimientos(authorized_client, test_producto, test_ubicacion, test_tipo_movimiento, test_user):
    # Crear un movimiento para asegurarnos de que hay datos
    response = authorized_client.post(
        "/movimientos/",
        json={
            "cantidad": 10.0,
            "referencia": "REF-READ-TEST",
            "observaciones": "Movimiento para probar lectura",
            "tipo_movimiento_id": test_tipo_movimiento.id,
            "producto_id": test_producto.id,
            "ubicacion_destino_id": test_ubicacion.id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Obtener todos los movimientos
    response = authorized_client.get("/movimientos/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(mov["referencia"] == "REF-READ-TEST" for mov in data)
    
    # Verificar estructura de un movimiento
    movimiento = next(mov for mov in data if mov["referencia"] == "REF-READ-TEST")
    assert "id" in movimiento
    assert "fecha" in movimiento
    assert "cantidad" in movimiento
    assert "tipo_movimiento" in movimiento
    assert "producto" in movimiento
    assert "usuario" in movimiento

def test_read_movimientos_filtrados(authorized_client, test_producto, test_tipo_movimiento):
    # Obtener movimientos filtrados por producto
    response = authorized_client.get(f"/movimientos/?producto_id={test_producto.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(mov["producto_id"] == test_producto.id for mov in data)
    
    # Obtener movimientos filtrados por tipo
    response = authorized_client.get(f"/movimientos/?tipo_movimiento_id={test_tipo_movimiento.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(mov["tipo_movimiento_id"] == test_tipo_movimiento.id for mov in data)
    
    # Filtrar por fecha (desde hace un día)
    fecha_desde = (datetime.now() - timedelta(days=1)).isoformat()
    response = authorized_client.get(f"/movimientos/?fecha_desde={fecha_desde}")
    assert response.status_code == status.HTTP_200_OK

def test_read_movimiento_by_id(authorized_client, test_producto, test_tipo_movimiento, test_ubicacion):
    # Crear un movimiento para obtenerlo por ID
    create_response = authorized_client.post(
        "/movimientos/",
        json={
            "cantidad": 5.0,
            "referencia": "REF-GET-BY-ID",
            "tipo_movimiento_id": test_tipo_movimiento.id,
            "producto_id": test_producto.id,
            "ubicacion_destino_id": test_ubicacion.id
        }
    )
    assert create_response.status_code == status.HTTP_200_OK
    movimiento_id = create_response.json()["id"]
    
    # Obtener el movimiento por ID
    response = authorized_client.get(f"/movimientos/{movimiento_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == movimiento_id
    assert data["cantidad"] == 5.0
    assert data["referencia"] == "REF-GET-BY-ID"
    assert data["tipo_movimiento"]["id"] == test_tipo_movimiento.id
    assert data["producto"]["id"] == test_producto.id

def test_read_nonexistent_movimiento(authorized_client):
    response = authorized_client.get("/movimientos/999")  # ID que no existe
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "movimiento no encontrado" in response.json()["detail"].lower()

# Test para verificar autenticación
def test_movimiento_requires_auth(client):
    response = client.get("/movimientos/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post(
        "/movimientos/",
        json={
            "cantidad": 10.0,
            "producto_id": 1,
            "tipo_movimiento_id": 1
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 