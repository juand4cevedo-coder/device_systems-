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
