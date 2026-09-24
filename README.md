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