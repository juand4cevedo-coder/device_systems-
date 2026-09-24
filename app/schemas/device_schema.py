from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    """Datos de entrada para registrar un dispositivo (también se usa en el PUT)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, description="Nombre del dispositivo")
    serial_number: str = Field(min_length=1, description="Número de serie (único)")
    device_type: str = Field(
        min_length=1,
        description="Tipo de dispositivo: laptop, tablet, proyector, cámara, router, monitor...",
    )
    brand: str | None = Field(default=None, description="Marca (opcional)")


class DeviceUpdate(BaseModel):
    """Actualización parcial (PATCH): todos los campos son opcionales."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1)
    serial_number: str | None = Field(default=None, min_length=1)
    device_type: str | None = Field(default=None, min_length=1)
    brand: str | None = None


class DeviceResponse(BaseModel):
    """Modelo público de respuesta de un dispositivo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str
    brand: str | None
    is_available: bool
    created_at: datetime
