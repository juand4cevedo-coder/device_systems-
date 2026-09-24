# Changelog

Todos los cambios relevantes de este proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el versionado sigue [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - AAAA-MM-DD

### Added
- Configuración del proyecto con uv y estructura `app/` (EV07, Fase 1).
- Schemas Pydantic v2 de usuario con validaciones de nombre, email y rol (Fase 2).
- Endpoints `GET /users` (filtros `role` e `is_active`) y `GET /users/{user_id}` (Fase 3).
- Endpoint `POST /users` con validación y control de correos duplicados (Fase 4).
- Response model `UserResponse` y cabeceras `X-App-Name` y `X-API-Version` (Fase 5).
- Evidencias de pruebas y documentación en el README (Fase 6).

## [2.0.0] - AAAA-MM-DD

### Added
- Endpoints `PUT /users/{user_id}` y `PATCH /users/{user_id}` con los schemas `UserUpdate` y `UserPatch` (EV08, Fase 3).
- Endpoint `DELETE /users/{user_id}` con respuesta `204 No Content` (Fase 4).
- Dependencias reutilizables con `Depends()`: búsqueda de usuario con 404, validación de correo duplicado y cabeceras de la API (Fase 7).
- Metadatos OpenAPI, tag `Users` y `summary`, `description` y `response_description` en cada endpoint (Fase 8).
- `requirements.txt` exportado desde `uv.lock`.
- Evidencias de pruebas, sección de tecnologías y reflexión en el README (Fases 9 y 10).

### Changed
- Código reorganizado en capas: `routes`, `schemas`, `services`, `dependencies` y `data` (Fase 2).
- Códigos de estado declarados explícitamente y errores controlados con `HTTPException` (Fases 5 y 6).
- Cabecera `X-API-Version` actualizada a `2.0`.

## [2.0.1] - AAAA-MM-DD

### Fixed
- Documentación de EV08 que no se incluyó en la versión 2.0.0: capturas de pruebas en `docs/images/ev08`, sección de tecnologías, evidencias y reflexión en el README.

## [2.1.0] - AAAA-MM-DD

### Added
- Persistencia con SQLAlchemy y SQLite: conexión, sesión, base declarativa y modelo `User` con sus constraints (EV09).
- Dependencia `get_db` que entrega una sesión de base de datos por petición.
- Parámetro `order_by` en `GET /users` para ordenar por nombre o fecha de creación.
- Campo `created_at` en los usuarios y en `UserResponse`.
- Evidencias de pruebas, estructura del proyecto y reflexión de EV09 en el README.

### Changed
- Servicios y dependencias trabajan sobre una sesión de base de datos en lugar de una lista en memoria.
- Cabecera `X-API-Version` actualizada a `2.1`.
- README reorganizado en un orden de lectura más claro.

### Removed
- Capa de datos en memoria (`app/data`) y schema interno `User`.

### Fixed
- Referencia del README a una captura de EV08 que no forma parte de las evidencias.