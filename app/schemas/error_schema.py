from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Formato de las respuestas de error de la API."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"detail": "Recurso no encontrado"}]}
    )

    detail: str


_ERROR_DESCRIPTIONS = {
    400: "Solicitud inválida: dato duplicado o cuerpo sin campos",
    404: "Recurso no encontrado",
    409: "Conflicto con una regla de negocio",
}


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Declara en OpenAPI las respuestas de error esperadas de un endpoint."""
    return {
        code: {"model": ErrorResponse, "description": _ERROR_DESCRIPTIONS[code]}
        for code in codes
    }
