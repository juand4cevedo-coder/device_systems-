from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(StrEnum):
    ADMIN = "admin"
    SUPPORT = "support"
    USER = "user"


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


class User(UserBase):
    """Usuario completo, con su identificador."""

    id: int


class UserResponse(UserBase):
    """Modelo público de respuesta: lo que la API expone al cliente."""

    id: int


class UserUpdate(UserBase):
    """Reemplazo completo (PUT): todos los campos son obligatorios."""

    is_active: bool


class UserPatch(BaseModel):
    """Actualización parcial (PATCH): todos los campos son opcionales."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=3)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
