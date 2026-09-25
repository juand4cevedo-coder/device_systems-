from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user_schema import UserRole, validate_password_strength


class UserRegister(BaseModel):
    """Datos de entrada para registrar un usuario mediante /auth/register."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Ana Pérez",
                    "email": "ana@sena.edu.co",
                    "password": "Abcdef12",
                    "role": "admin",
                }
            ]
        },
    )

    name: str = Field(
        min_length=3, description="Nombre del usuario (mínimo 3 caracteres)"
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Mínimo 8 caracteres, con mayúscula, minúscula y número",
    )
    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        return validate_password_strength(value)


class UserLogin(BaseModel):
    """Credenciales de acceso.

    /auth/login sigue el flujo estándar OAuth2PasswordBearer y recibe estos mismos
    datos como formulario (application/x-www-form-urlencoded), no como JSON: el
    campo `username` del formulario es el correo. Ese formato es el que exige el
    estándar OAuth2 y el que activa el botón "Authorize" de Swagger UI.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"email": "ana@sena.edu.co", "password": "Abcdef12"}]
        }
    )

    email: EmailStr
    password: str


class Token(BaseModel):
    """Respuesta de /auth/login."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                }
            ]
        }
    )

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraídos de un token JWT válido."""

    user_id: int | None = None
