# device_systems

API REST para la gestión de usuarios del sistema device_systems, construida con FastAPI.

## Requisitos

- Python 3.x
- [uv](https://docs.astral.sh/uv/)

## Instalación de dependencias

```bash
uv sync
```

## Ejecución del servidor

```bash
uv run uvicorn app.main:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs

## Modelo de usuario

| Campo | Tipo | Validación |
|---|---|---|
| id | int | Asignado por el sistema |
| name | str | Obligatorio, mínimo 3 caracteres |
| email | str | Formato de correo válido |
| role | str | `admin`, `support` o `user` |
| is_active | bool | Booleano (por defecto `true`) |

## Endpoints

| Método | Ruta | Descripción | Parámetros |
|---|---|---|---|
| GET | `/users` | Lista todos los usuarios | Query opcionales: `role`, `is_active` |
| GET | `/users/{user_id}` | Consulta un usuario por ID | Path: `user_id` (int) |

### Ejemplos de peticiones GET

```bash
curl http://127.0.0.1:8000/users
curl "http://127.0.0.1:8000/users?role=admin"
curl "http://127.0.0.1:8000/users?is_active=true"
curl http://127.0.0.1:8000/users/1
```

Respuesta de `GET /users/1`:

```json
{
  "id": 1,
  "name": "Ana Pérez",
  "email": "ana@sena.edu.co",
  "role": "admin",
  "is_active": true
}
```

| POST | `/users` | Registra un nuevo usuario | Body JSON: `name`, `email`, `role`, `is_active` (opcional) |

### Ejemplo de petición POST

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Marta Ruiz", "email": "marta@sena.edu.co", "role": "user"}'
```

Respuesta `201 Created`:

```json
{
  "id": 4,
  "name": "Marta Ruiz",
  "email": "marta@sena.edu.co",
  "role": "user",
  "is_active": true
}
```

### Respuestas de error del POST

| Código | Caso |
|---|---|
| 400 Bad Request | El correo ya está registrado |
| 422 Unprocessable Entity | Datos inválidos (nombre corto, email mal formado, rol no permitido) |

## Response models y cabeceras HTTP

Todos los endpoints declaran un `response_model` (`UserResponse`), que define los campos que la API expone: `id`, `name`, `email`, `role` e `is_active`.

Las respuestas exitosas incluyen estas cabeceras personalizadas:

| Cabecera | Valor |
|---|---|
| `X-App-Name` | `device_systems` |
| `X-API-Version` | `1.0` |