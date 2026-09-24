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