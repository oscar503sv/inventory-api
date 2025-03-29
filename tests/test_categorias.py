import pytest
from fastapi import status

# Test para crear una categoría
def test_create_categoria(client, admin_token):
    response = client.post(
        "/categorias/",
        json={"nombre": "Categoría de Prueba", "descripcion": "Descripción de prueba"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Categoría de Prueba"
    assert data["descripcion"] == "Descripción de prueba"
    assert "id" in data

# Test para intentar crear una categoría duplicada
def test_create_categoria_duplicada(client, admin_token):
    # Crear primera categoría
    client.post(
        "/categorias/",
        json={"nombre": "Categoría Duplicada", "descripcion": "Primera descripción"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Intentar crear una categoría con el mismo nombre
    response = client.post(
        "/categorias/",
        json={"nombre": "Categoría Duplicada", "descripcion": "Segunda descripción"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ya existe una categoría con ese nombre" in response.json()["detail"].lower()

# Test para obtener todas las categorías
def test_read_categorias(client, test_categoria, admin_token):
    response = client.get(
        "/categorias/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1  # Al menos debería existir la categoría de prueba
    assert any(cat["nombre"] == test_categoria.nombre for cat in data)

# Test para obtener una categoría específica por ID
def test_read_categoria(client, test_categoria, admin_token):
    response = client.get(
        f"/categorias/{test_categoria.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_categoria.id
    assert data["nombre"] == test_categoria.nombre
    assert data["descripcion"] == test_categoria.descripcion

# Test para obtener una categoría que no existe
def test_read_categoria_nonexistent(client, admin_token):
    response = client.get(
        "/categorias/9999",  # ID que no existe
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "categoría no encontrada" in response.json()["detail"].lower()

# Test para actualizar una categoría
def test_update_categoria(client, test_categoria, admin_token):
    response = client.put(
        f"/categorias/{test_categoria.id}",
        json={"nombre": "Categoría Actualizada", "descripcion": "Descripción actualizada"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_categoria.id
    assert data["nombre"] == "Categoría Actualizada"
    assert data["descripcion"] == "Descripción actualizada"

# Test para eliminar una categoría
def test_delete_categoria(client, admin_token):
    # Primero crear una categoría
    create_response = client.post(
        "/categorias/",
        json={"nombre": "Categoría para Eliminar", "descripcion": "Será eliminada"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    categoria_id = create_response.json()["id"]
    
    # Ahora eliminarla
    response = client.delete(
        f"/categorias/{categoria_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar que ya no existe
    get_response = client.get(
        f"/categorias/{categoria_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

# Test para verificar que se requiere autenticación
def test_categoria_requires_auth(client):
    # Intentar crear sin autenticación
    response = client.post(
        "/categorias/",
        json={"nombre": "Sin Auth", "descripcion": "No debería crearse"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Intentar leer sin autenticación
    response = client.get("/categorias/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 