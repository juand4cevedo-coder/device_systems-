from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(StrEnum):
    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


class UserOrderBy(StrEnum):
    NAME = "name"
    CREATED_AT = "created_at"


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=3, description="Nombre del usuario (mínimo 3 caracteres)"
    )
    email: EmailStr
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    """Datos de entrada para registrar un usuario."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Ana Pérez",
                    "email": "ana@sena.edu.co",
                    "role": "admin",
                    "is_active": True,
                }
            ]
        }
    )


class UserResponse(UserBase):
    """Modelo público de respuesta: lo que la API expone al cliente."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Ana Pérez",
                    "email": "ana@sena.edu.co",
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2026-09-24T15:04:05.123456",
                }
            ]
        },
    )

    id: int
    created_at: datetime


class UserUpdate(UserBase):
    """Reemplazo completo (PUT): todos los campos son obligatorios."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Carlos Gómez Ruiz",
                    "email": "carlos@sena.edu.co",
                    "role": "support",
                    "is_active": True,
                }
            ]
        }
    )

    is_active: bool


class UserPatch(BaseModel):
    """Actualización parcial (PATCH): todos los campos son opcionales."""

    model_config = ConfigDict(
        str_strip_whitespace=True, json_schema_extra={"examples": [{"role": "support"}]}
    )

    name: str | None = Field(default=None, min_length=3)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
