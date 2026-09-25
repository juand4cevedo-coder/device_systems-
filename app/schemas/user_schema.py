from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(StrEnum):
    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


class UserOrderBy(StrEnum):
    NAME = "name"
    CREATED_AT = "created_at"


def validate_password_strength(value: str) -> str:
    """Valida que una contraseña cumpla las reglas mínimas de seguridad."""
    if any(ch.isspace() for ch in value):
        raise ValueError("La contraseña no puede contener espacios en blanco")
    if not any(ch.isupper() for ch in value):
        raise ValueError("La contraseña debe tener al menos una mayúscula")
    if not any(ch.islower() for ch in value):
        raise ValueError("La contraseña debe tener al menos una minúscula")
    if not any(ch.isdigit() for ch in value):
        raise ValueError("La contraseña debe tener al menos un número")
    return value


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
                    "password": "Abcdef12",
                }
            ]
        }
    )

    password: str = Field(
        min_length=8,
        description="Mínimo 8 caracteres, con mayúscula, minúscula y número",
    )

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


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
