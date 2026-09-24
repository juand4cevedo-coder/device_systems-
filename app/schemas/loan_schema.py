from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class LoanStatus(StrEnum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


class LoanCreate(BaseModel):
    """Datos de entrada para registrar un préstamo."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"user_id": 1, "device_id": 3}]}
    )

    user_id: int = Field(gt=0, description="ID del usuario que recibe el préstamo")
    device_id: int = Field(gt=0, description="ID del dispositivo prestado")


class LoanUpdate(BaseModel):
    """Datos actualizables de un préstamo. La devolución se registra con PATCH /loans/{loan_id}/return."""

    status: LoanStatus | None = None
    return_date: datetime | None = None


class LoanResponse(BaseModel):
    """Modelo público de respuesta de un préstamo."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "device_id": 3,
                    "loan_date": "2026-09-24T15:04:05.123456",
                    "return_date": None,
                    "status": "active",
                }
            ]
        },
    )

    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: datetime | None
    status: LoanStatus


class LoanUserSummary(BaseModel):
    """Datos básicos del usuario dentro de un préstamo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class LoanDeviceSummary(BaseModel):
    """Datos básicos del dispositivo dentro de un préstamo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str


class LoanDetailResponse(BaseModel):
    """Préstamo con la información relacionada del usuario y del dispositivo."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "loan_id": 1,
                    "status": "active",
                    "loan_date": "2026-09-24T15:04:05.123456",
                    "return_date": None,
                    "user": {"id": 1, "name": "Ana Pérez", "email": "ana@sena.edu.co"},
                    "device": {
                        "id": 3,
                        "name": "Laptop Lenovo ThinkPad",
                        "serial_number": "LEN-2024-001",
                        "device_type": "laptop",
                    },
                }
            ]
        },
    )

    loan_id: int = Field(validation_alias="id")
    status: LoanStatus
    loan_date: datetime
    return_date: datetime | None
    user: LoanUserSummary
    device: LoanDeviceSummary
