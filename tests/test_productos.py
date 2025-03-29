import pytest
from fastapi import status

# Test para crear producto
def test_create_producto(authorized_client, test_categoria, test_proveedor):
    response = authorized_client.post(
        "/productos/",
        json={
            "codigo": "PROD002",
            "nombre": "Nuevo Producto",
            "descripcion": "Descripción del nuevo producto",
            "precio_compra": 25.0,
            "precio_venta": 40.0,
            "unidad_medida": "unidad",
            "stock_minimo": 5,
            "activo": True,
            "categoria_id": test_categoria.id,
            "proveedor_id": test_proveedor.id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["codigo"] == "PROD002"
    assert data["nombre"] == "Nuevo Producto"
    assert data["precio_compra"] == 25.0
    assert data["precio_venta"] == 40.0
    assert data["categoria_id"] == test_categoria.id
    assert data["proveedor_id"] == test_proveedor.id
    assert "id" in data

def test_create_duplicate_producto(authorized_client, test_producto):
    response = authorized_client.post(
        "/productos/",
        json={
            "codigo": test_producto.codigo,  # Duplicado
            "nombre": "Otro Producto",
            "categoria_id": test_producto.categoria_id,
            "proveedor_id": test_producto.proveedor_id
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un producto con ese código" in response.json()["detail"]

# Test para obtener productos
def test_read_productos(authorized_client, test_producto):
    response = authorized_client.get("/productos/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(prod["codigo"] == test_producto.codigo for prod in data)

def test_read_producto_by_id(authorized_client, test_producto):
    response = authorized_client.get(f"/productos/{test_producto.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["codigo"] == test_producto.codigo
    assert data["nombre"] == test_producto.nombre
    assert data["categoria"]["id"] == test_producto.categoria_id
    assert data["proveedor"]["id"] == test_producto.proveedor_id
    assert "stock_total" in data  # Verificar que incluye el stock total

def test_read_nonexistent_producto(authorized_client):
    response = authorized_client.get("/productos/999")  # ID que no existe
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Producto no encontrado" in response.json()["detail"]

# Test para actualizar producto
def test_update_producto(authorized_client, test_producto):
    response = authorized_client.put(
        f"/productos/{test_producto.id}",
        json={
            "nombre": "Producto Actualizado",
            "precio_compra": 30.0,
            "precio_venta": 45.0
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Producto Actualizado"
    assert data["precio_compra"] == 30.0
    assert data["precio_venta"] == 45.0
    assert data["id"] == test_producto.id

def test_update_nonexistent_producto(authorized_client, test_categoria):
    response = authorized_client.put(
        "/productos/999",  # ID que no existe
        json={
            "nombre": "Producto Inexistente",
            "categoria_id": test_categoria.id
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Producto no encontrado" in response.json()["detail"]

# Test para eliminar producto
def test_delete_producto(authorized_client, test_categoria, test_proveedor):
    # Primero crear un producto para eliminar
    create_response = authorized_client.post(
        "/productos/",
        json={
            "codigo": "DELPRODUCT",
            "nombre": "Producto para Eliminar",
            "categoria_id": test_categoria.id,
            "proveedor_id": test_proveedor.id
        }
    )
    assert create_response.status_code == status.HTTP_200_OK
    producto_id = create_response.json()["id"]
    
    # Luego eliminarlo
    delete_response = authorized_client.delete(f"/productos/{producto_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar que ya no existe
    get_response = authorized_client.get(f"/productos/{producto_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_nonexistent_producto(authorized_client):
    response = authorized_client.delete("/productos/999")  # ID que no existe
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Producto no encontrado" in response.json()["detail"]

def test_delete_producto_con_stock(authorized_client, test_producto, test_stock):
    # Intentar eliminar un producto que tiene stock asociado
    response = authorized_client.delete(f"/productos/{test_producto.id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No se puede eliminar el producto porque tiene stock asociado" in response.json()["detail"]

# Test para verificar autenticación
def test_producto_requires_auth(client):
    response = client.get("/productos/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post(
        "/productos/",
        json={
            "codigo": "NOAUTH",
            "nombre": "Producto sin auth",
            "categoria_id": 1
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 