# device_systems

API REST para la gestión de usuarios del sistema device_systems, construida con FastAPI. Implementa el CRUD completo del recurso `users`, con validación de datos (Pydantic v2), manejo de errores con códigos HTTP, dependencias reutilizables (`Depends()`) y documentación automática con Swagger/OpenAPI.

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

| DELETE | `/users/{user_id}` | Elimina un usuario | Path: `user_id` |

### Ejemplo de petición DELETE

```bash
curl -X DELETE http://127.0.0.1:8000/users/3
```

Responde `204 No Content`, sin cuerpo de respuesta.

| Código | Caso |
|---|---|
| 204 No Content | Usuario eliminado correctamente |
| 404 Not Found | El usuario no existe |

## Response models y cabeceras HTTP

Todos los endpoints declaran un `response_model` (`UserResponse`), que define los campos que la API expone: `id`, `name`, `email`, `role` e `is_active`.

Las respuestas exitosas incluyen estas cabeceras personalizadas:

| Cabecera | Valor |
|---|---|
| `X-App-Name` | `device_systems` |
| `X-API-Version` | `2.0` |

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

## Códigos de estado usados

| Operación | Método y ruta | Código |
|---|---|---|
| Listar usuarios | `GET /users` | 200 OK |
| Consultar usuario | `GET /users/{user_id}` | 200 OK |
| Crear usuario | `POST /users` | 201 Created |
| Actualizar completo | `PUT /users/{user_id}` | 200 OK |
| Actualizar parcial | `PATCH /users/{user_id}` | 200 OK |
| Eliminar usuario | `DELETE /users/{user_id}` | 204 No Content |
| Usuario no encontrado | Cualquier método por ID | 404 Not Found |
| Correo duplicado | `POST`, `PUT` y `PATCH` | 400 Bad Request |
| Actualización sin datos | `PATCH /users/{user_id}` | 400 Bad Request |
| Datos inválidos | Validación Pydantic | 422 Unprocessable Entity |

## Manejo de errores

| Caso | Código | Respuesta |
|---|---|---|
| Usuario no encontrado (incluye eliminar o actualizar uno inexistente) | 404 | `{"detail": "Usuario no encontrado"}` |
| Correo duplicado | 400 | `{"detail": "El correo ya está registrado"}` |
| PATCH sin ningún campo | 400 | `{"detail": "Debe enviar al menos un campo para actualizar"}` |
| Rol no permitido o datos inválidos | 422 | Lista de errores de validación de Pydantic en `detail` |

## Dependency Injection con Depends()

FastAPI resuelve las dependencias declaradas con `Depends()` antes de ejecutar cada endpoint. Las funciones reutilizables viven en `app/dependencies/user_dependencies.py`:

| Dependencia | Qué hace | Dónde se usa |
|---|---|---|
| `set_api_headers` | Agrega `X-App-Name` y `X-API-Version` a cada respuesta | Todo el router `/users` |
| `get_user_or_404` | Busca el usuario por ID o lanza 404 | GET, PUT, PATCH y DELETE por ID |
| `validate_new_user` | Valida el body del POST y que el correo no esté registrado (400) | POST |
| `validate_user_replacement` | Valida el body del PUT y que el correo no sea de otro usuario (400) | PUT |
| `validate_user_changes` | Valida el body del PATCH, rechaza el PATCH vacío (400) y el correo de otro usuario (400) | PATCH |
| `get_db` | Entrega una sesión de base de datos por petición y la cierra al terminar | Endpoints y demás dependencias, compartida en una misma petición |

Ventajas de este enfoque:

- La lógica de validación se escribe una sola vez y se reutiliza en varios endpoints.
- Las rutas quedan cortas y solo llaman al servicio.
- FastAPI ejecuta cada dependencia una sola vez por petición, aunque varias la declaren.
- Los errores (`HTTPException`) se lanzan desde las dependencias, por lo que todos los endpoints responden igual ante el mismo caso.

## Documentación automática (Swagger/OpenAPI)

FastAPI genera la documentación de la API a partir del código:

| Interfaz | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

La aplicación configura estos metadatos en `app/main.py`:

- **Título:** `device_systems API`
- **Descripción:** API REST para la gestión de usuarios del sistema device_systems
- **Versión:** `2.0.0`
- **Contacto:** autor del proyecto
- **Tags:** `Users` (con descripción)

Cada endpoint declara `summary`, `description` y `response_description`, por lo que la documentación explica qué hace, qué validaciones aplica y qué devuelve.

Swagger/OpenAPI permite probar cada endpoint desde el navegador sin herramientas externas, y mantiene la documentación siempre sincronizada con el código.

## Base de datos (SQLAlchemy)

La persistencia usa SQLAlchemy con SQLite. El archivo `device_systems.db` se crea automáticamente al iniciar la aplicación y no se versiona.

| Componente | Archivo | Descripción |
|---|---|---|
| `engine` | `app/database/connection.py` | Conexión a `sqlite:///./device_systems.db` |
| `SessionLocal` | `app/database/connection.py` | Fábrica de sesiones |
| `Base` | `app/database/connection.py` | Base declarativa de los modelos |
| `get_db` | `app/dependencies/database_dependency.py` | Dependencia que entrega una sesión por petición y la cierra al terminar |

### Modelo `User` (tabla `users`)

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | String | Obligatorio |
| `email` | String | Único y obligatorio |
| `role` | String | Obligatorio |
| `is_active` | Boolean | Valor por defecto `True` |
| `created_at` | DateTime | Fecha de creación (UTC) |

## Modelo SQLAlchemy vs schema Pydantic

| | Modelo SQLAlchemy | Schema Pydantic |
|---|---|---|
| Archivo | `app/models/user_model.py` | `app/schemas/user_schema.py` |
| Representa | La tabla `users` de la base de datos | Los datos que entran y salen de la API |
| Responsabilidad | Persistencia: tipos de columna y constraints (`nullable`, `unique`) | Validación y serialización: formato del correo, rol permitido, longitud del nombre |
| Cuándo se usa | Al leer o escribir en la base de datos | Al recibir la petición y al construir la respuesta |
| Clases | `User` | `UserCreate`, `UserUpdate`, `UserPatch`, `UserResponse` |

Se mantienen separados para que la base de datos y el contrato de la API puedan evolucionar de forma independiente. Por ejemplo, el modelo puede tener columnas que la API no expone. `UserResponse` usa `from_attributes=True` para convertir un objeto del modelo en la respuesta de la API.

## Operaciones CRUD sobre la base de datos

Los servicios de `app/services/user_service.py` reciben la sesión de base de datos y ejecutan las consultas con SQLAlchemy:

| Operación | Función |
|---|---|
| Crear usuario | `create_user` |
| Listar usuarios | `list_users` |
| Buscar usuario por ID | `get_user_by_id` |
| Buscar usuario por email | `get_user_by_email` |
| Actualizar usuario completo | `update_user` (PUT: todos los campos) |
| Actualizar usuario parcial | `update_user` (PATCH: solo los campos enviados) |
| Eliminar usuario | `delete_user` |
| Filtrar por rol y por estado | `list_users(role=..., is_active=...)` |
| Ordenar por nombre o fecha de creación | `list_users(order_by=...)` |

Los datos persisten entre reinicios del servidor. La base de datos comienza vacía: los usuarios se crean con `POST /users`.

### Schemas de usuario

| Schema | Uso | Validaciones |
|---|---|---|
| `UserCreate` | Body de `POST /users` | `name` (mín. 3 caracteres), `email` válido, `role` permitido, `is_active` booleano |
| `UserUpdate` | Body de `PUT /users/{user_id}` | Las mismas, con todos los campos obligatorios |
| `UserPatch` | Body de `PATCH /users/{user_id}` | Las mismas, con todos los campos opcionales |
| `UserResponse` | Respuesta de los endpoints | Se construye desde el modelo SQLAlchemy |
## Tecnologías utilizadas

- Python 3
- [FastAPI](https://fastapi.tiangolo.com/): framework para construir la API REST
- [Uvicorn](https://www.uvicorn.org/): servidor ASGI
- [Pydantic v2](https://docs.pydantic.dev/): validación de datos y modelos
- email-validator: validación del formato de correo
- [uv](https://docs.astral.sh/uv/): gestión de dependencias y entorno virtual
- Git, GitHub y GitFlow: control de versiones

## Evidencias de pruebas (EV08)

Pruebas funcionales de los seis endpoints y de los escenarios de error, ejecutadas desde Swagger UI, ReDoc y Thunder Client.

### Swagger UI y ReDoc

![Swagger UI: vista general](docs/images/ev08/01-swagger-overview.png)
*Título, versión 2.0.0, tag `Users` y los seis endpoints con su `summary`.*

![Swagger UI: schemas](docs/images/ev08/02-swagger-schemas.png)
*Schemas de entrada (`UserCreate`, `UserUpdate`, `UserPatch`) y de salida (`UserResponse`).*

![ReDoc: vista general](docs/images/ev08/03-redoc-overview.png)
*Documentación de la API en `/redoc`.*

![ReDoc: detalle de un endpoint](docs/images/ev08/04-redoc-endpoint-detail.png)
*Descripción y respuestas de `POST /users`.*

### Pruebas de cada endpoint

![GET /users](docs/images/ev08/05-get-users.png)
*`GET /users`: 200 con las cabeceras personalizadas.*

![GET /users/1](docs/images/ev08/06-get-user-by-id.png)
*`GET /users/{user_id}`: 200.*

![POST /users](docs/images/ev08/07-post-user-created.png)
*`POST /users`: 201 Created.*

![PUT /users/2](docs/images/ev08/08-put-user-updated.png)
*`PUT /users/{user_id}`: 200, reemplazo completo.*

![PATCH /users/3](docs/images/ev08/09-patch-user-updated.png)
*`PATCH /users/{user_id}`: 200, actualización parcial de un solo campo.*

![DELETE /users/4](docs/images/ev08/10-delete-user-204.png)
*`DELETE /users/{user_id}`: 204 No Content, sin cuerpo.*

### Errores controlados

![Error 404](docs/images/ev08/11-error-404-user-not-found.png)
*Buscar un usuario inexistente: 404 Not Found.*

![Error 400 por correo duplicado](docs/images/ev08/12-error-400-duplicate-email.png)
*Crear un usuario con un correo repetido: 400 Bad Request.*

![Error 422](docs/images/ev08/13-error-422-validation.png)
*Crear un usuario con datos inválidos: 422 Unprocessable Entity.*

![Error 404 al actualizar](docs/images/ev08/14-error-404-update-nonexistent.png)
*Actualizar un usuario inexistente: 404 Not Found.*

![Error 400 por PATCH vacío](docs/images/ev08/15-error-400-empty-patch.png)
*PATCH sin ningún campo: 400 Bad Request.*

![Error 404 al eliminar](docs/images/ev08/16-error-404-delete-nonexistent.png)
*Eliminar un usuario inexistente: 404 Not Found.*

## Reflexión final sobre la evolución del proyecto (EV08)

En EV07 la API solo permitía consultar y crear usuarios, con todo el código en las rutas. En EV08 pasó a ser un CRUD completo con una estructura por capas: rutas para los endpoints, schemas para validar, servicios para la lógica, dependencias para reutilizar validaciones y una capa de datos en memoria. Separar responsabilidades hizo que cada archivo tenga un único propósito. Con `Depends()` las validaciones se escriben una sola vez y se reutilizan, los códigos de estado y las `HTTPException` hacen que la API responda de forma predecible ante los errores, y Swagger/OpenAPI permite probarla y documentarla sin herramientas externas. [Completa con lo que más te costó o lo que más valoras de esta evolución.]
