# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Gestión de Inventario! Este documento proporciona lineamientos para contribuir al proyecto.

## Cómo contribuir

Existen varias formas de contribuir al proyecto:

1. **Reportar bugs**: Si encuentras un bug, por favor crea un issue detallando el problema.
2. **Sugerir mejoras**: Si tienes ideas para mejorar el proyecto, por favor crea un issue con tu propuesta.
3. **Añadir funcionalidades**: Puedes implementar nuevas funcionalidades o mejorar las existentes.
4. **Mejorar documentación**: La documentación siempre puede mejorar o actualizarse.

## Proceso de desarrollo

1. **Fork el repositorio** a tu cuenta de GitHub.
2. **Crea una rama** (`git checkout -b feature/amazing-feature`).
3. **Realiza tus cambios** y asegúrate de seguir las convenciones de codificación.
4. **Ejecuta las pruebas** para asegurarte de que no has roto nada.
5. **Commit tus cambios** (`git commit -m 'Add some amazing feature'`).
6. **Push a la rama** (`git push origin feature/amazing-feature`).
7. **Abre un Pull Request** en GitHub.

## Convenciones de código

### Estilo de código

Seguimos [PEP 8](https://www.python.org/dev/peps/pep-0008/) para el estilo de código Python. Puedes usar herramientas como `flake8` o `black` para asegurar que tu código cumple con estas convenciones.

```bash
# Instalar herramientas de linting
pip install flake8 black

# Verificar estilo de código
flake8 .

# Formatear automáticamente tu código
black .
```

### Pruebas

Todas las nuevas funcionalidades deben incluir pruebas. Usamos `pytest` para ejecutar pruebas:

```bash
# Ejecutar todas las pruebas
python -m pytest

# Ejecutar pruebas con cobertura
python -m pytest --cov=.
```

### Convenciones de commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para mensajes de commit. Esto nos ayuda a mantener un historial de cambios legible y a generar automáticamente notas de lanzamiento.

Ejemplos:
- `feat: add product search by barcode`
- `fix: correct inventory calculation for exit movements`
- `docs: update API documentation`
- `test: add integration tests for authentication endpoints`
- `refactor: improve database transaction handling`

## Pull Request

### Proceso de revisión

Una vez que hayas enviado un Pull Request:

1. Uno o más mantenedores del proyecto revisarán tus cambios.
2. Pueden solicitarte cambios o mejoras.
3. Una vez aprobados, tus cambios serán fusionados en la rama principal.

### Checklist para Pull Requests

Antes de enviar un Pull Request, asegúrate de que:

- [ ] Has ejecutado las pruebas y todas pasan.
- [ ] Has seguido las convenciones de código.
- [ ] Has documentado cualquier nueva función o cambio de comportamiento.
- [ ] Has actualizado la documentación si es necesario.
- [ ] Has añadido pruebas para cualquier nueva funcionalidad.

## Reporte de bugs

Al reportar un bug, incluye:

- Una descripción clara del bug.
- Pasos para reproducir el problema.
- El comportamiento esperado y el comportamiento actual.
- Capturas de pantalla si es posible.
- Información sobre tu entorno (sistema operativo, versión de Python, etc.).

## Contacto

Si tienes preguntas o necesitas ayuda, puedes:

- Crear un issue en GitHub.
- Enviar un correo electrónico a ozkar.codes@gmail.com.

¡Gracias por contribuir! 