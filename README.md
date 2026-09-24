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

| PUT | `/users/{user_id}` | Reemplaza por completo un usuario | Path: `user_id`. Body: `name`, `email`, `role`, `is_active` (todos obligatorios) |
| PATCH | `/users/{user_id}` | Actualiza parcialmente un usuario | Path: `user_id`. Body: uno o más de `name`, `email`, `role`, `is_active` |

### Ejemplos de peticiones PUT y PATCH

```bash
# PUT: reemplazo completo
curl -X PUT http://127.0.0.1:8000/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Carlos Gómez Ruiz", "email": "carlos@sena.edu.co", "role": "support", "is_active": true}'

# PATCH: actualización parcial
curl -X PATCH http://127.0.0.1:8000/users/3 \
  -H "Content-Type: application/json" \
  -d '{"role": "support"}'
```

Ambos responden `200 OK` con el usuario actualizado.

### Respuestas de error de PUT y PATCH

| Código | Caso |
|---|---|
| 404 Not Found | El usuario no existe |
| 400 Bad Request | El correo pertenece a otro usuario, o el PATCH no trae ningún campo |
| 422 Unprocessable Entity | Datos inválidos, o falta un campo obligatorio en el PUT |

## Response models y cabeceras HTTP

Todos los endpoints declaran un `response_model` (`UserResponse`), que define los campos que la API expone: `id`, `name`, `email`, `role` e `is_active`.

Las respuestas exitosas incluyen estas cabeceras personalizadas:

| Cabecera | Valor |
|---|---|
| `X-App-Name` | `device_systems` |
| `X-API-Version` | `1.0` |

## Estructura del proyecto

```text
device_systems/
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── user_routes.py
│   ├── schemas/
│   │   └── user_schema.py
│   ├── services/
│   │   └── user_service.py
│   ├── dependencies/
│   │   └── user_dependencies.py
│   └── data/
│       └── users_db.py
├── docs/
│   └── images/
├── pyproject.toml
├── requirements.txt
└── README.md
```

| Carpeta | Responsabilidad |
|---|---|
| `routes` | Definición de endpoints |
| `schemas` | Modelos Pydantic de entrada y salida |
| `services` | Lógica de negocio |
| `dependencies` | Funciones reutilizables con `Depends()` |
| `data` | Simulación de base de datos en memoria |

## Flujo de trabajo Git

El proyecto sigue GitFlow:

| Rama | Uso |
|---|---|
| `main` | Versiones estables, cada una con su tag (`v1.0.0`) |
| `develop` | Integración del trabajo en curso |
| `feature/*` | Una rama por fase de la actividad, integrada a `develop` mediante Pull Request |
| `release/*` | Preparación de cada versión antes de pasar a `main` |

Los commits siguen Conventional Commits: `tipo(scope): descripción` (por ejemplo, `feat(users): add POST /users`).

## Evidencias de pruebas (EV07)

### Swagger UI

![Vista general de Swagger UI](docs/images/ev07/01-swagger-overview.png)
*Endpoints del recurso `users` en `/docs`.*

![Schemas en Swagger UI](docs/images/ev07/02-swagger-schemas.png)
*Schemas de entrada y salida.*

### GET /users

![GET /users](docs/images/ev07/03-get-users.png)
*Listado completo con las cabeceras personalizadas en la respuesta.*

![GET /users con filtro por rol](docs/images/ev07/04-get-users-filter-role.png)
*Filtro con query parameter `role=admin`.*

### GET /users/{user_id}

![GET /users/1](docs/images/ev07/05-get-user-by-id.png)
*Consulta por ID con path parameter.*

### POST /users

![POST /users](docs/images/ev07/06-post-user-created.png)
*Registro de un usuario nuevo: respuesta `201 Created`.*

### Validaciones y errores

![Error 404](docs/images/ev07/07-error-404-user-not-found.png)
*Usuario inexistente: `404 Not Found`.*

![Error 400](docs/images/ev07/08-error-400-duplicate-email.png)
*Correo duplicado: `400 Bad Request`.*

![Error 422](docs/images/ev07/09-error-422-validation.png)
*Datos inválidos: `422 Unprocessable Entity`.*

## Reflexión sobre FastAPI (EV07)

FastAPI permitió construir la API de `users` con poco código: los path y query parameters se declaran como argumentos de las funciones, Pydantic valida los datos de entrada y los `response_model` controlan lo que la API devuelve, todo apoyado en los tipos de Python. Además, la documentación interactiva se genera automáticamente y sirvió para probar cada endpoint sin herramientas externas. [Completa con lo que más te sirvió o te costó aprender.]