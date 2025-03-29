# Sistema de Gestión de Inventario API

Una API RESTful para gestionar inventario de productos, desarrollada con FastAPI y SQLAlchemy.

## Características

- **Autenticación**: Registro, login y logout de usuarios con JWT
- **Control de acceso**: Roles de usuario (admin, usuario normal)
- **Gestión de productos**: CRUD completo de productos con categorías, proveedores y ubicaciones
- **Gestión de inventario**: Control de stock y movimientos (entradas y salidas)
- **Trazabilidad**: Seguimiento de movimientos con usuario, fecha y referencias
- **API documentada**: Interfaz interactiva con Swagger UI

## Tecnologías utilizadas

- **FastAPI**: Framework web para creación de APIs
- **SQLAlchemy**: ORM para interacción con la base de datos
- **Pydantic**: Validación de datos y serialización
- **JWT**: Autenticación basada en tokens
- **Pytest**: Framework de pruebas
- **Alembic**: Migraciones de base de datos

## Requisitos

- Python 3.8+
- pip

## Instalación

1. Clona el repositorio
```bash
git clone https://github.com/oscar503sv/inventory-api.git
cd inventory-api
```

2. Crea y activa un entorno virtual
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

3. Instala las dependencias
```bash
pip install -r requirements.txt
```

4. Ejecuta las migraciones para crear la base de datos
```bash
alembic upgrade head
```

5. Inicia el servidor de desarrollo
```bash
fastapi dev app.py
```

La API estará disponible en http://localhost:8000

## Documentación API

Una vez que el servidor esté en funcionamiento, puedes acceder a la documentación interactiva de la API:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura del proyecto

```
inventory-system-api/
├── alembic/            # Configuración y migraciones de la base de datos
├── app.py              # Punto de entrada de la aplicación
├── config/             # Configuración (base de datos, etc.)
├── models/             # Modelos SQLAlchemy
├── routes/             # Rutas de la API organizadas por funcionalidad
├── schemas/            # Esquemas Pydantic para validación
├── utils/              # Utilidades (autenticación, etc.)
└── tests/              # Pruebas unitarias e integración
```

## Uso básico

### Autenticación

```python
# Registrar un nuevo usuario
POST /signup
{
  "username": "usuario",
  "email": "usuario@ejemplo.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "password": "contraseña",
  "role": "user"
}

# Iniciar sesión
POST /login
{
  "username": "usuario",
  "password": "contraseña"
}

# Respuesta
{
  "access_token": "token...",
  "token_type": "bearer"
}
```

### Ejemplo de movimiento de inventario

```python
# Crear un movimiento de entrada
POST /movimientos/
{
  "cantidad": 50.0,
  "referencia": "REF-001",
  "observaciones": "Compra inicial",
  "tipo_movimiento_id": 1,  # Tipo entrada
  "producto_id": 1,
  "ubicacion_destino_id": 1
}
```

## Pruebas

Para ejecutar las pruebas:

```bash
python -m pytest
```

Para obtener un informe de cobertura:

```bash
python -m pytest --cov=.
```

## Estado del proyecto

Este proyecto está activamente mantenido. Las nuevas características, correcciones de errores y mejoras son bienvenidas a través de issues y pull requests.

## Licencia

Este proyecto está bajo la licencia GNU General Public License. Consulta el archivo [LICENSE](LICENSE) para más detalles. 