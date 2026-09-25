# device_systems

API REST para la gestión de usuarios, dispositivos y préstamos del sistema device_systems, construida con FastAPI. Implementa el CRUD completo de usuarios y dispositivos, la gestión de préstamos con reglas de negocio, consultas con joins y filtros avanzados, validación de datos (Pydantic v2), manejo de errores con códigos HTTP, dependencias reutilizables (`Depends()`), persistencia con SQLAlchemy y SQLite, migraciones con Alembic, hash de contraseñas y tokens JWT, y documentación automática con Swagger/OpenAPI.

## Tecnologías utilizadas

- Python 3
- [FastAPI](https://fastapi.tiangolo.com/): framework para construir la API REST
- [Uvicorn](https://www.uvicorn.org/): servidor ASGI
- [Pydantic v2](https://docs.pydantic.dev/): validación de datos y modelos
- email-validator: validación del formato de correo
- [uv](https://docs.astral.sh/uv/): gestión de dependencias y entorno virtual
- Git, GitHub y GitFlow: control de versiones
- [SQLAlchemy](https://www.sqlalchemy.org/): ORM para la persistencia de datos
- SQLite: base de datos relacional de desarrollo
- [Alembic](https://alembic.sqlalchemy.org/): migraciones de la base de datos
- `passlib[bcrypt]` y `python-jose`: hash de contraseñas y tokens JWT
- `slowapi`: rate limiting

## Requisitos

- Python 3.x
- [uv](https://docs.astral.sh/uv/)

## Instalación de dependencias

```bash
uv sync
```

## Variables de entorno

La configuración de seguridad se lee desde un archivo `.env`, que no se versiona. Copia `.env.example` a `.env` y genera una clave propia:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave con la que se firman los tokens JWT |
| `ALGORITHM` | Algoritmo de firma (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de vigencia de un token |

## Dependencias de seguridad

| Paquete | Uso |
|---|---|
| `passlib[bcrypt]` | Hash de contraseñas |
| `python-jose[cryptography]` | Creación y validación de tokens JWT |
| `slowapi` | Rate limiting |
| `python-multipart` | Lectura del formulario de login de OAuth2 |
| `python-dotenv` | Lectura del archivo `.env` |

`bcrypt` se fija por debajo de la versión 5 porque `passlib` 1.7.4 falla al inicializarse con `bcrypt` 5. `passlib` y `python-jose` se usan porque los pide la guía, pero son librerías con poco mantenimiento: la documentación actual de FastAPI usa `pwdlib` y `PyJWT`, que serían la elección para un proyecto en producción.

## Ejecución del servidor

Antes de iniciar el servidor por primera vez, crea la base de datos con las migraciones. Ejecuta los comandos siempre desde la raíz del proyecto.

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs

## Estructura del proyecto

```text
device_systems/
├── app/
│   ├── main.py
│   ├── auth/
│   │   └── security.py
│   ├── database/
│   │   ├── connection.py
│   │   └── migration_check.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   ├── loan_schema.py
│   │   ├── auth_schema.py
│   │   └── error_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   └── dependencies/
│       ├── database_dependency.py
│       ├── user_dependencies.py
│       ├── device_dependencies.py
│       └── loan_dependencies.py
├── alembic/
│   ├── env.py
│   └── versions/
├── docs/
│   └── images/
├── .env.example
├── alembic.ini
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
└── README.md
```

`device_systems.db` se genera al aplicar las migraciones y no se versiona. `.env` tampoco se versiona.

| Carpeta | Responsabilidad |
|---|---|
| `auth` | Utilidades de seguridad: hash de contraseñas y tokens JWT |
| `database` | Conexión a la base de datos (engine, sesión, base declarativa) y comprobación de migraciones al arrancar |
| `models` | Modelos SQLAlchemy: tablas `users`, `devices` y `loans` y sus relaciones |
| `schemas` | Modelos Pydantic de entrada y salida, autenticación y el formato de los errores |
| `routes` | Definición de endpoints |
| `services` | Lógica de negocio y consultas a la base de datos |
| `dependencies` | Funciones reutilizables con `Depends()`: sesión, búsquedas por ID, validaciones y reglas de negocio |
| `alembic` | Migraciones que versionan el esquema de la base de datos |

## Base de datos (SQLAlchemy)

El archivo `device_systems.db` se crea al aplicar las migraciones de Alembic y no se versiona.

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
| `hashed_password` | String | Obligatorio; hash de la contraseña, nunca se expone en las respuestas |
| `role` | String | Obligatorio |
| `is_active` | Boolean | Valor por defecto `True` |
| `created_at` | DateTime | Fecha de creación (UTC) |

## Modelos de dispositivos y préstamos

### Modelo `Device` (tabla `devices`)

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | String | Obligatorio |
| `serial_number` | String | Único y obligatorio |
| `device_type` | String | Obligatorio |
| `brand` | String | Opcional |
| `is_available` | Boolean | Valor por defecto `True` |
| `created_at` | DateTime | Fecha de creación (UTC) |

### Modelo `Loan` (tabla `loans`)

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | Integer | Primary Key |
| `user_id` | Integer | Foreign Key a `users.id`, obligatorio |
| `device_id` | Integer | Foreign Key a `devices.id`, obligatorio |
| `loan_date` | DateTime | Fecha de préstamo (UTC) |
| `return_date` | DateTime | Opcional |
| `status` | String | Obligatorio: `active`, `returned` u `overdue` |

### Relaciones

| Relación | Tipo | Definición |
|---|---|---|
| Usuario → préstamos | One-to-Many | `User.loans` y `Loan.user` |
| Dispositivo → préstamos | One-to-Many | `Device.loans` y `Loan.device` |
| Préstamo → usuario y dispositivo | Many-to-One | Cada préstamo pertenece a un usuario y a un dispositivo |

Las relaciones se declaran con `relationship()` y `back_populates`.

### Integridad referencial

`loans.user_id` y `loans.device_id` son claves foráneas obligatorias, así que un préstamo siempre pertenece a un usuario y a un dispositivo existentes. SQLite no aplica las claves foráneas por defecto, por lo que `app/database/connection.py` las activa con `PRAGMA foreign_keys=ON` en cada conexión.

## Migraciones con Alembic

El esquema de la base de datos se versiona con Alembic. Las migraciones están en `alembic/versions/`.

| Comando | Uso |
|---|---|
| `uv run alembic upgrade head` | Aplica todas las migraciones pendientes |
| `uv run alembic revision --autogenerate -m "mensaje"` | Genera una migración a partir de los cambios en los modelos |
| `uv run alembic current` | Muestra la revisión aplicada en la base de datos |
| `uv run alembic history` | Lista el historial de migraciones |
| `uv run alembic downgrade -1` | Revierte la última migración |

Alembic toma la URL de conexión y la metadata de SQLAlchemy desde `app/database/connection.py` y `app/models`. Usa el modo *batch* (`render_as_batch=True`), porque SQLite no soporta la mayoría de las instrucciones `ALTER TABLE`.

### Migración de autenticación

La migración `add authentication fields to users` agrega la columna obligatoria `hashed_password`. `role` e `is_active` ya existían desde EV09.

Para que la migración no falle en bases que ya tienen usuarios, la columna se crea con un valor vacío por defecto. Ese valor nunca coincide con un hash válido, así que esos usuarios no pueden iniciar sesión hasta que se les asigne una contraseña.

### Errores al aplicar migraciones

Al iniciar, la API comprueba que la base de datos esté en la última revisión de Alembic. Si no lo está, se detiene con un mensaje que indica cómo solucionarlo, en lugar de fallar más tarde en una petición.

| Situación | Mensaje | Solución |
|---|---|---|
| La base no está migrada o está desactualizada | `RuntimeError: La base de datos no está actualizada ... Ejecuta: uv run alembic upgrade head` | Ejecutar `uv run alembic upgrade head` |
| Al generar una migración con la base desactualizada | `Target database is not up to date` | Ejecutar primero `uv run alembic upgrade head` |
| La base se creó fuera de Alembic y las tablas ya existen | `table ... already exists` | En desarrollo, borrar `device_systems.db` y volver a ejecutar `uv run alembic upgrade head` |

Cada migración incluye `downgrade()`, por lo que se puede revertir con `uv run alembic downgrade -1`.

## Seguridad

### Hash de contraseñas y tokens JWT

`app/auth/security.py` centraliza las utilidades de seguridad:

| Función | Uso |
|---|---|
| `get_password_hash(password)` | Genera el hash de una contraseña con `passlib` (bcrypt) |
| `verify_password(plain, hashed)` | Verifica una contraseña contra su hash |
| `create_access_token(data)` | Crea un token JWT firmado con `SECRET_KEY`, con expiración |
| `decode_access_token(token)` | Decodifica y valida un token; devuelve `None` si es inválido o expiró |

Ninguna contraseña se guarda ni se muestra en texto plano. `UserResponse` no incluye `hashed_password`.

### Schemas de autenticación

| Schema | Uso |
|---|---|
| `UserRegister` | Body de `POST /auth/register`: `name`, `email`, `password`, `role` |
| `UserLogin` | Representa las credenciales del login; `POST /auth/login` las recibe como formulario OAuth2 (`username` = correo, `password`), no como JSON |
| `Token` | Respuesta de `POST /auth/login`: `access_token` y `token_type` |
| `TokenData` | Datos extraídos de un token válido |

### Validación de contraseñas

Mínimo 8 caracteres, con al menos una mayúscula, una minúscula, un número, y sin espacios en blanco. Se aplica en `UserCreate` (`POST /users`) y en `UserRegister` (`POST /auth/register`).

## Modelo SQLAlchemy vs schema Pydantic

| | Modelo SQLAlchemy | Schema Pydantic |
|---|---|---|
| Archivo | `app/models/user_model.py` | `app/schemas/user_schema.py` |
| Representa | La tabla `users` de la base de datos | Los datos que entran y salen de la API |
| Responsabilidad | Persistencia: tipos de columna y constraints (`nullable`, `unique`) | Validación y serialización: formato del correo, rol permitido, longitud del nombre |
| Cuándo se usa | Al leer o escribir en la base de datos | Al recibir la petición y al construir la respuesta |
| Clases | `User` | `UserCreate`, `UserUpdate`, `UserPatch`, `UserResponse` |

Se mantienen separados para que la base de datos y el contrato de la API puedan evolucionar de forma independiente. Por ejemplo, el modelo puede tener columnas que la API no expone (`hashed_password`). `UserResponse` usa `from_attributes=True` para convertir un objeto del modelo en la respuesta de la API.

### Schemas de usuario

| Schema | Uso | Validaciones |
|---|---|---|
| `UserCreate` | Body de `POST /users` | `name` (mín. 3 caracteres), `email` válido, `role` permitido, `is_active` opcional, `password` (mín. 8, con mayúscula, minúscula y número) |
| `UserUpdate` | Body de `PUT /users/{user_id}` | Las mismas de `UserCreate` salvo `password`, con todos los campos obligatorios |
| `UserPatch` | Body de `PATCH /users/{user_id}` | Las mismas, con todos los campos opcionales |
| `UserResponse` | Respuesta de los endpoints | Se construye desde el modelo SQLAlchemy; no incluye `hashed_password` |

## Schemas de dispositivos y préstamos

### Dispositivos

| Schema | Uso | Campos |
|---|---|---|
| `DeviceCreate` | Body de `POST /devices` y `PUT /devices/{device_id}` | `name`, `serial_number`, `device_type` (obligatorios) y `brand` (opcional) |
| `DeviceUpdate` | Body de `PATCH /devices/{device_id}` | Los mismos campos, todos opcionales |
| `DeviceResponse` | Respuesta de los endpoints de dispositivos | Todos los campos, incluidos `id`, `is_available` y `created_at` |

`is_available` no se envía en las peticiones: el sistema lo actualiza al registrar y devolver préstamos.

### Préstamos

| Schema | Uso | Campos |
|---|---|---|
| `LoanCreate` | Body de `POST /loans` | `user_id` y `device_id` |
| `LoanUpdate` | Actualización de un préstamo (la devolución se registra con `PATCH /loans/{loan_id}/return`) | `status` y `return_date`, opcionales |
| `LoanResponse` | Respuesta de un préstamo | `id`, `user_id`, `device_id`, `loan_date`, `return_date` y `status` |
| `LoanDetailResponse` | Préstamo con la información relacionada | Datos del préstamo más `user` y `device` anidados |

Estados de préstamo (`LoanStatus`): `active`, `returned` y `overdue`.

Ejemplo de `LoanDetailResponse`:

```json
{
  "loan_id": 1,
  "status": "active",
  "loan_date": "2026-09-24T15:04:05.123456",
  "return_date": null,
  "user": {
    "id": 1,
    "name": "Ana Pérez",
    "email": "ana@sena.edu.co"
  },
  "device": {
    "id": 3,
    "name": "Laptop Lenovo ThinkPad",
    "serial_number": "LEN-2024-001",
    "device_type": "laptop"
  }
}
```

## Endpoints de autenticación

| Método | Ruta | Descripción | Cuerpo o cabecera |
|---|---|---|---|
| POST | `/auth/register` | Registra un usuario con contraseña segura | Body JSON: `name`, `email`, `password`, `role` (opcional, por defecto `user`) |
| POST | `/auth/login` | Autentica y devuelve un token JWT | Formulario OAuth2: `username` (correo), `password` |
| GET | `/auth/me` | Devuelve el usuario autenticado | `Authorization: Bearer <token>` |

### Ejemplos de peticiones

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana Pérez", "email": "ana@sena.edu.co", "password": "Abcdef12", "role": "admin"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=ana@sena.edu.co" \
  -d "password=Abcdef12"

curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

Respuesta `200 OK` de `POST /auth/login`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Respuestas de error

| Código | Caso |
|---|---|
| 400 Bad Request | El correo ya está registrado |
| 401 Unauthorized | Correo o contraseña incorrectos, o token ausente / inválido |
| 422 Unprocessable Entity | Datos inválidos (nombre corto, correo mal formado, contraseña débil) |

`POST /auth/register` es hoy la única forma de crear un usuario con rol `admin`, ya que `POST /users` se protegerá para administradores en el siguiente bloque.


## Endpoints

| Método | Ruta | Descripción | Parámetros |
|---|---|---|---|
| GET | `/users` | Lista todos los usuarios | Query opcionales: `role`, `is_active`, `order_by` (`name` o `created_at`) |
| GET | `/users/{user_id}` | Consulta un usuario por ID | Path: `user_id` (int) |
| GET | `/users/{user_id}/loans` | Historial de préstamos de un usuario | Path: `user_id` |
| POST | `/users` | Registra un nuevo usuario | Body JSON: `name`, `email`, `role`, `is_active` (opcional), `password` |
| PUT | `/users/{user_id}` | Reemplaza por completo un usuario | Path: `user_id`. Body: `name`, `email`, `role`, `is_active` (todos obligatorios) |
| PATCH | `/users/{user_id}` | Actualiza parcialmente un usuario | Path: `user_id`. Body: uno o más de `name`, `email`, `role`, `is_active` |
| DELETE | `/users/{user_id}` | Elimina un usuario | Path: `user_id` |

### Ejemplos de peticiones

```bash
curl http://127.0.0.1:8000/users
curl "http://127.0.0.1:8000/users?role=admin"
curl "http://127.0.0.1:8000/users?order_by=name"

curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Marta Ruiz", "email": "marta@sena.edu.co", "role": "user", "password": "Abcdef12"}'

curl -X PUT http://127.0.0.1:8000/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Carlos Gómez Ruiz", "email": "carlos@sena.edu.co", "role": "support", "is_active": true}'

curl -X PATCH http://127.0.0.1:8000/users/3 \
  -H "Content-Type: application/json" \
  -d '{"role": "support"}'

curl -X DELETE http://127.0.0.1:8000/users/3
```

Respuesta `201 Created` del POST:

```json
{
  "id": 4,
  "name": "Marta Ruiz",
  "email": "marta@sena.edu.co",
  "role": "user",
  "is_active": true,
  "created_at": "2026-09-24T15:04:05.123456"
}
```

El `DELETE` responde `204 No Content`, sin cuerpo. Los códigos de error de todos los endpoints están centralizados en "Manejo de errores".

## Response models y cabeceras HTTP

Todos los endpoints declaran un `response_model` (`UserResponse`), que define los campos que la API expone: `id`, `name`, `email`, `role`, `is_active` y `created_at`. `hashed_password` nunca se expone.

Las respuestas exitosas incluyen estas cabeceras personalizadas:

| Cabecera | Valor |
|---|---|
| `X-App-Name` | `device_systems` |
| `X-API-Version` | `2.2` |

## Endpoints de dispositivos

| Método | Ruta | Descripción | Parámetros |
|---|---|---|---|
| GET | `/devices` | Lista dispositivos | Query opcionales: `device_type`, `is_available`, `brand`, `search` |
| GET | `/devices/{device_id}` | Consulta un dispositivo por ID | Path: `device_id` (int) |
| GET | `/devices/{device_id}/loans` | Historial de préstamos de un dispositivo | Path: `device_id` |
| POST | `/devices` | Registra un dispositivo | Body JSON: `name`, `serial_number`, `device_type`, `brand` (opcional) |
| PUT | `/devices/{device_id}` | Reemplaza por completo un dispositivo | Path: `device_id`. Body: los mismos campos |
| PATCH | `/devices/{device_id}` | Actualiza parcialmente un dispositivo | Path: `device_id`. Body: uno o más campos |
| DELETE | `/devices/{device_id}` | Elimina un dispositivo | Path: `device_id` |

### Filtros de `GET /devices`

| Parámetro | Ejemplo | Comportamiento |
|---|---|---|
| `device_type` | `?device_type=laptop` | Tipo exacto, sin distinguir mayúsculas |
| `is_available` | `?is_available=true` | Dispositivos disponibles o prestados |
| `brand` | `?brand=lenovo` | Marca exacta, sin distinguir mayúsculas |
| `search` | `?search=thinkpad` | Texto contenido en el nombre, el número de serie, el tipo o la marca (`ilike` combinado con `or_`) |

Los filtros se pueden combinar: `GET /devices?device_type=laptop&is_available=true`.

### Ejemplos de peticiones

```bash
curl -X POST http://127.0.0.1:8000/devices \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop Lenovo ThinkPad", "serial_number": "LEN-2024-001", "device_type": "laptop", "brand": "Lenovo"}'

curl "http://127.0.0.1:8000/devices?brand=lenovo"
curl "http://127.0.0.1:8000/devices?search=thinkpad"
```

Respuesta `201 Created` del POST:

```json
{
  "id": 1,
  "name": "Laptop Lenovo ThinkPad",
  "serial_number": "LEN-2024-001",
  "device_type": "laptop",
  "brand": "Lenovo",
  "is_available": true,
  "created_at": "2026-09-24T15:04:05.123456"
}
```

El número de serie se compara sin distinguir mayúsculas. `is_available` no se envía en las peticiones: cambia con los préstamos. Para quitar la marca de un dispositivo se usa el PUT, porque el PATCH ignora los campos vacíos.

## Endpoints de préstamos

| Método | Ruta | Descripción | Parámetros |
|---|---|---|---|
| GET | `/loans` | Lista préstamos con usuario y dispositivo, con filtros opcionales | Query: `status`, `user_id`, `device_id`, `user_email`, `device_type`, `date_from`, `date_to` |
| GET | `/loans/details` | Lista préstamos con el detalle de usuario y dispositivo (consulta con `JOIN`) | Los mismos filtros |
| GET | `/loans/{loan_id}` | Consulta un préstamo por ID | Path: `loan_id` (int) |
| POST | `/loans` | Presta un dispositivo a un usuario | Body JSON: `user_id`, `device_id` |
| PATCH | `/loans/{loan_id}/return` | Registra la devolución de un dispositivo | Path: `loan_id` (int) |

### Reglas de negocio

**`POST /loans`**

1. Valida que el usuario exista.
2. Valida que el dispositivo exista.
3. Valida que el dispositivo esté disponible.
4. Crea el préstamo con estado `active`.
5. Cambia `is_available` del dispositivo a `False`.

**`PATCH /loans/{loan_id}/return`**

1. Valida que el préstamo exista y que no haya sido devuelto.
2. Marca el préstamo como `returned`.
3. Asigna la fecha de devolución (`return_date`).
4. Cambia `is_available` del dispositivo a `True`.

Cada operación se guarda en una sola transacción: el préstamo y el estado del dispositivo cambian juntos.

### Ejemplos de peticiones

```bash
curl -X POST http://127.0.0.1:8000/loans \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "device_id": 1}'

curl -X PATCH http://127.0.0.1:8000/loans/1/return
```

Respuesta `201 Created` del POST:

```json
{
  "id": 1,
  "user_id": 1,
  "device_id": 1,
  "loan_date": "2026-09-24T15:04:05.123456",
  "return_date": null,
  "status": "active"
}
```

Un dispositivo con préstamos registrados, aunque ya estén devueltos, no se puede eliminar: `DELETE /devices/{device_id}` responde `409 Conflict`. Lo mismo aplica a `DELETE /users/{user_id}`.

## Consultas con joins y filtros

`GET /loans` y `GET /loans/details` consultan varias tablas a la vez. Cada préstamo se devuelve con la información relacionada de su usuario y de su dispositivo, cargada en una sola consulta.

### Filtros

| Parámetro | Ejemplo | Comportamiento |
|---|---|---|
| `status` | `?status=active` | Estado del préstamo: `active`, `returned` u `overdue` |
| `user_id` | `?user_id=1` | Préstamos de un usuario |
| `device_id` | `?device_id=3` | Préstamos de un dispositivo |
| `user_email` | `?user_email=aprendiz@sena.edu.co` | Correo del usuario; búsqueda parcial, sin distinguir mayúsculas |
| `device_type` | `?device_type=laptop` | Tipo de dispositivo, sin distinguir mayúsculas |
| `date_from` | `?date_from=2026-09-01` | Préstamos desde esa fecha, inclusive (`AAAA-MM-DD`, UTC) |
| `date_to` | `?date_to=2026-09-30` | Préstamos hasta esa fecha, inclusive |

Todos son opcionales y se pueden combinar: `GET /loans?status=active&device_type=laptop`.

### Cómo funciona

La consulta está en `search_loans` (`app/services/loan_service.py`):

- **`join()`:** une `loans` con `users` y con `devices`. `contains_eager()` carga el usuario y el dispositivo en esa misma consulta.
- **`where()` y `and_()`:** solo se agregan las condiciones de los filtros enviados y se combinan con `and_()`.
- **`ilike()`:** para la búsqueda parcial del correo, sin distinguir mayúsculas.

### Filtros inválidos

Un estado inexistente, un identificador no numérico o una fecha mal escrita responden `422 Unprocessable Entity`. Si `date_from` es posterior a `date_to`, también responde `422` con un mensaje explicativo.

`GET /users/{user_id}/loans` y `GET /devices/{device_id}/loans` devuelven el historial completo de un usuario o de un dispositivo, y responden `404` si no existen. Para ver solo los préstamos activos de un usuario se usa `GET /loans?user_id=1&status=active`.

## Operaciones CRUD sobre la base de datos

Los servicios reciben la sesión de base de datos y ejecutan las consultas con SQLAlchemy:

| Operación | Función |
|---|---|
| Crear usuario | `user_service.create_user` |
| Listar usuarios | `user_service.list_users` |
| Buscar usuario por ID o email | `user_service.get_user_by_id`, `get_user_by_email` |
| Actualizar usuario completo o parcial | `user_service.update_user` |
| Eliminar usuario | `user_service.delete_user` |
| Crear, listar y actualizar dispositivos | `device_service` |
| Registrar y devolver préstamos | `loan_service.create_loan`, `loan_service.return_loan` |
| Consultar préstamos con joins y filtros | `loan_service.search_loans` |

## Códigos de estado usados

| Operación | Método y ruta | Código |
|---|---|---|
| Listar / consultar | `GET` | 200 OK |
| Registro creado | `POST` | 201 Created |
| Actualizar completo o parcial | `PUT`, `PATCH` | 200 OK |
| Devolución exitosa | `PATCH /loans/{loan_id}/return` | 200 OK |
| Eliminación exitosa | `DELETE` | 204 No Content |
| Recurso no encontrado | Cualquier método por ID | 404 Not Found |
| Dato duplicado | Correo, número de serie o `password` ausente | 400 Bad Request |
| Actualización sin datos | `PATCH` vacío | 400 Bad Request |
| Regla de negocio incumplida | Dispositivo no disponible, préstamo ya devuelto, o eliminar un usuario o dispositivo con préstamos | 409 Conflict |
| Datos o filtros inválidos | Validación Pydantic, estado, fecha o identificador con formato incorrecto | 422 Unprocessable Entity |

## Manejo de errores

| Caso | Código | Respuesta |
|---|---|---|
| Usuario, dispositivo o préstamo no encontrado | 404 | `{"detail": "Usuario no encontrado"}` (o dispositivo/préstamo) |
| Correo o número de serie duplicado | 400 | `{"detail": "El correo ya está registrado"}` (o número de serie) |
| PATCH sin ningún campo | 400 | `{"detail": "Debe enviar al menos un campo para actualizar"}` |
| Dispositivo no disponible | 409 | `{"detail": "El dispositivo no está disponible"}` |
| Préstamo ya devuelto | 409 | `{"detail": "El préstamo ya fue devuelto"}` |
| Eliminar un usuario o dispositivo con préstamos | 409 | `{"detail": "No se puede eliminar un usuario con préstamos registrados"}` (o dispositivo) |
| Datos inválidos (formato, rol, contraseña débil, filtros) | 422 | Lista de errores de validación de Pydantic en `detail` |
| Credenciales incorrectas o token inválido | 401 | `{"detail": "Correo o contraseña incorrectos"}` o `{"detail": "No se pudo validar las credenciales"}` |

## Dependency Injection con Depends()

FastAPI resuelve las dependencias declaradas con `Depends()` antes de ejecutar cada endpoint. Las funciones reutilizables viven en `app/dependencies/`:

| Dependencia | Qué hace | Dónde se usa |
|---|---|---|
| `set_api_headers` | Agrega `X-App-Name` y `X-API-Version` a cada respuesta | Todos los routers |
| `get_db` | Entrega una sesión de base de datos por petición y la cierra al terminar | Endpoints y demás dependencias |
| `get_user_or_404` / `get_device_or_404` / `get_loan_or_404` | Busca el recurso por ID o lanza 404 | Endpoints por ID |
| `validate_new_user` / `validate_user_replacement` / `validate_user_changes` | Valida el body y el correo duplicado en POST, PUT y PATCH de usuarios | `user_routes.py` |
| `ensure_user_can_be_deleted` / `ensure_device_can_be_deleted` | Lanza 409 si el recurso tiene préstamos registrados | `DELETE` de usuarios y dispositivos |
| `validate_new_loan` / `ensure_loan_can_be_returned` | Reglas de negocio de préstamos | `loan_routes.py` |
| `get_loan_filters` | Reúne y valida los filtros opcionales de `GET /loans` | `loan_routes.py` |

Ventajas de este enfoque: la lógica de validación se escribe una sola vez y se reutiliza, las rutas quedan cortas, FastAPI ejecuta cada dependencia una sola vez por petición aunque varias la declaren, y los errores (`HTTPException`) se lanzan desde las dependencias, así que todos los endpoints responden igual ante el mismo caso.

## Documentación automática (Swagger/OpenAPI)

FastAPI genera la documentación de la API a partir del código:

| Interfaz | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

La aplicación configura estos metadatos en `app/main.py`:

- **Título:** `device_systems API`
- **Descripción:** API REST para la gestión de usuarios, dispositivos y préstamos del sistema device_systems
- **Versión:** `2.2.0`
- **Tags:** `Users`, `Devices` y `Loans` (cada uno con su descripción)

Cada endpoint declara `summary`, `description` y `response_description`. Además:

- Cada endpoint declara sus respuestas de error esperadas (400, 404 y 409, según el caso) con el schema `ErrorResponse`. El 422 de validación lo agrega FastAPI.
- Los schemas de entrada y de respuesta incluyen ejemplos, que Swagger usa para precargar los cuerpos de las peticiones.

## Flujo de trabajo Git

El proyecto sigue GitFlow:

| Rama | Uso |
|---|---|
| `main` | Versiones estables, cada una con su tag (`v1.0.0` ... `v2.2.0`) |
| `develop` | Integración del trabajo en curso |
| `feature/*` | Una rama por fase de una actividad, integrada a `develop` mediante Pull Request |
| `release/*` | Preparación de cada versión antes de pasar a `main` |
| `device_systems_alembic_relaciones` | Rama de EV10 (Alembic, relaciones, joins), con nombre exigido por la guía |
| `device_systems_security` | Rama de EV11 (autenticación, seguridad), con nombre exigido por la guía |

Los commits siguen Conventional Commits: `tipo(scope): descripción` (por ejemplo, `feat(users): add POST /users`).

El trabajo de EV10 se desarrolló en la rama `device_systems_alembic_relaciones`, que se integró a `develop` y llegó a `main` con el release `2.2.0`. El de EV11 se desarrolla en `device_systems_security` y llegará a `main` con el release `3.0.0`.

## Evidencias de pruebas (EV10)

### Alembic y base de datos

![alembic init](docs/images/ev10/01-alembic-init.png)
*Inicialización de Alembic con `alembic init alembic`.*

![alembic revision --autogenerate](docs/images/ev10/02-alembic-revision-autogenerate.png)
*Generación de la migración `create devices and loans tables`.*

![alembic upgrade head](docs/images/ev10/03-alembic-upgrade-head.png)
*Aplicación de la migración con `alembic upgrade head`.*

![alembic history](docs/images/ev10/04-alembic-history.png)
*Historial de migraciones con `alembic history`.*

![Estructura de las tablas](docs/images/ev10/05-database-tables-structure.png)
*Tablas `users`, `devices` y `loans` generadas, con sus claves foráneas.*

### Swagger UI y ReDoc

![Swagger UI: vista general](docs/images/ev10/06-swagger-overview.png)
*Grupos `Users`, `Devices` y `Loans` en `/docs`, versión 2.2.0.*

![Swagger UI: schemas](docs/images/ev10/07-swagger-schemas.png)
*Schemas de dispositivos, préstamos y errores.*

![Swagger UI: respuestas de POST /loans](docs/images/ev10/08-swagger-loans-errors.png)
*Códigos de respuesta esperados de `POST /loans`.*

![ReDoc](docs/images/ev10/09-redoc-overview.png)
*Documentación en `/redoc`.*

### Pruebas funcionales mínimas

![Test 2](docs/images/ev10/10-test02-create-user.png)
*2. Crear un usuario: 201 Created.*

![Test 3](docs/images/ev10/11-test03-create-device.png)
*3. Crear un dispositivo: 201 Created.*

![Test 4](docs/images/ev10/12-test04-create-loan.png)
*4. Crear un préstamo: 201 Created, con estado `active`.*

![Test 5](docs/images/ev10/13-test05-device-unavailable-409.png)
*5. Intentar prestar un dispositivo no disponible: 409 Conflict.*

![Test 6](docs/images/ev10/14-test06-loans-details-join.png)
*6. Listar préstamos con la información del usuario y del dispositivo (consulta con `JOIN`).*

![Test 7](docs/images/ev10/15-test07-filter-by-status.png)
*7. Filtrar préstamos por estado.*

![Test 8](docs/images/ev10/16-test08-filter-by-device-type.png)
*8. Filtrar préstamos por tipo de dispositivo.*

![Test 9](docs/images/ev10/17-test09-user-loans.png)
*9. Consultar los préstamos de un usuario.*

![Test 10](docs/images/ev10/18-test10-return-device.png)
*10. Devolver un dispositivo: el préstamo pasa a `returned`.*

![Test 11](docs/images/ev10/19-test11-device-available-again.png)
*11. El dispositivo vuelve a estar disponible.*

![Test 12](docs/images/ev10/20-test12-device-loan-history.png)
*12. Historial de préstamos del dispositivo.*

La prueba 1, ejecutar las migraciones con Alembic, está documentada en la sección "Alembic y base de datos".

## Evidencias de pruebas (EV09)

### Estructura del proyecto y base de datos

![Estructura del proyecto](docs/images/ev09/01-project-structure.png)
*Estructura del proyecto con las capas `database`, `models`, `schemas`, `routes`, `services` y `dependencies`.*

![Esquema de la base de datos](docs/images/ev09/02-database-schema.png)
*Tabla `users` generada por SQLAlchemy, con sus restricciones y el índice único de `email`.*

### Swagger UI y ReDoc

![Swagger UI: vista general](docs/images/ev09/03-swagger-overview.png)
*Endpoints de `users` en `/docs`, versión 2.1.0.*

![Swagger UI: schemas](docs/images/ev09/04-swagger-schemas.png)
*Schemas de entrada y de respuesta.*

![Swagger UI: parámetros de consulta](docs/images/ev09/05-swagger-get-users-params.png)
*`GET /users` con los parámetros `role`, `is_active` y `order_by`.*

![ReDoc](docs/images/ev09/06-redoc-overview.png)
*Documentación en `/redoc`.*

### Pruebas funcionales mínimas

![Test 1](docs/images/ev09/07-test01-post-user-created.png)
*1. Crear un usuario válido: 201 Created.*

![Test 2](docs/images/ev09/08-test02-post-duplicate-email-400.png)
*2. Crear un usuario con email repetido: 400 Bad Request.*

![Test 3](docs/images/ev09/09-test03-get-users.png)
*3. Listar usuarios: 200 OK.*

![Test 4](docs/images/ev09/10-test04-get-user-by-id.png)
*4. Consultar un usuario por ID: 200 OK.*

![Test 5](docs/images/ev09/11-test05-get-user-not-found-404.png)
*5. Consultar un usuario inexistente: 404 Not Found.*

![Test 6](docs/images/ev09/12-test06-filter-by-role.png)
*6. Filtrar usuarios por rol: solo el administrador.*

![Test 7](docs/images/ev09/13-test07-filter-active-users.png)
*7. Filtrar usuarios activos: se excluye al usuario inactivo.*

![Test 8](docs/images/ev09/14-test08-put-user.png)
*8. Actualizar un usuario completo con PUT: 200 OK.*

![Test 9](docs/images/ev09/15-test09-patch-user.png)
*9. Actualizar parcialmente un usuario con PATCH: 200 OK.*

![Test 10](docs/images/ev09/16-test10-delete-user-204.png)
*10. Eliminar un usuario con DELETE: 204 No Content.*

![Test 11](docs/images/ev09/17-test11-deleted-user-not-found.png)
*11. Validar que el usuario eliminado ya no exista: 404 Not Found.*

### Errores controlados

![Error 422 por datos inválidos](docs/images/ev09/18-error-422-invalid-data.png)
*Datos inválidos (nombre corto y correo mal formado): 422 Unprocessable Entity.*

![Error 422 por rol no permitido](docs/images/ev09/19-error-422-role-not-allowed.png)
*Rol no permitido: 422 Unprocessable Entity.*

![Error 404 al actualizar](docs/images/ev09/20-error-404-update-nonexistent.png)
*Actualizar un usuario inexistente: 404 Not Found.*

![Error 404 al eliminar](docs/images/ev09/21-error-404-delete-nonexistent.png)
*Eliminar un usuario inexistente: 404 Not Found.*

## Evidencias de pruebas (EV08)

Pruebas funcionales de los seis endpoints y de los escenarios de error, ejecutadas desde Swagger UI y ReDoc.

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

## Reflexión final sobre migraciones, relaciones y consultas avanzadas (EV10)

Hasta EV09 la base de datos se creaba de golpe al iniciar la aplicación; con Alembic cada cambio del esquema queda registrado en una migración que se puede aplicar, revisar y revertir, así que la base evoluciona de forma controlada. Relacionar `User`, `Device` y `Loan` con claves foráneas y `relationship()` hizo que la base garantice la integridad: un préstamo siempre pertenece a un usuario y a un dispositivo que existen. Las consultas con `join()` y filtros opcionales permiten obtener en una sola petición los préstamos con su usuario y su dispositivo, y las reglas de negocio (dispositivo disponible, préstamo ya devuelto) se validan antes de modificar los datos, en una sola transacción. [Completa con lo que más te costó o lo que más valoras de esta etapa.]

## Reflexión final sobre la persistencia (EV09)

Hasta EV08 los usuarios vivían en una lista en memoria y desaparecían cada vez que el servidor se reiniciaba. Con SQLAlchemy y SQLite los datos se guardan en un archivo y siguen disponibles después de reiniciar el servidor. Separar el modelo SQLAlchemy (cómo se guarda un usuario) del schema Pydantic (cómo entra y sale por la API) permite que cada uno cambie sin afectar al otro, y los constraints de la base de datos (`nullable=False`, `unique=True`) protegen la integridad de los datos además de las validaciones de la API. La sesión de base de datos se entrega con `Depends(get_db)`, lo que reutiliza el mismo mecanismo de dependencias de EV08. [Completa con lo que más te costó o lo que más valoras de la persistencia.]

## Reflexión final sobre la evolución del proyecto (EV08)

En EV07 la API solo permitía consultar y crear usuarios, con todo el código en las rutas. En EV08 pasó a ser un CRUD completo con una estructura por capas: rutas para los endpoints, schemas para validar, servicios para la lógica, dependencias para reutilizar validaciones y una capa de datos en memoria. Separar responsabilidades hizo que cada archivo tenga un único propósito. Con `Depends()` las validaciones se escriben una sola vez y se reutilizan, los códigos de estado y las `HTTPException` hacen que la API responda de forma predecible ante los errores, y Swagger/OpenAPI permite probarla y documentarla sin herramientas externas. [Completa con lo que más te costó o lo que más valoras de esta evolución.]

## Reflexión sobre FastAPI (EV07)

FastAPI permitió construir la API de `users` con poco código: los path y query parameters se declaran como argumentos de las funciones, Pydantic valida los datos de entrada y los `response_model` controlan lo que la API devuelve, todo apoyado en los tipos de Python. Además, la documentación interactiva se genera automáticamente y sirvió para probar cada endpoint sin herramientas externas. [Completa con lo que más te sirvió o te costó aprender.]