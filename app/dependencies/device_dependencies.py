from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate
from app.services import device_service


def get_device_or_404(device_id: int, db: Session = Depends(get_db)) -> Device:
    """Obtiene el dispositivo por ID o lanza 404 si no existe."""
    device = device_service.get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado"
        )
    return device


def _ensure_serial_number_available(
    db: Session, serial_number: str, current_device_id: int | None = None
) -> None:
    """Lanza 400 si el número de serie pertenece a otro dispositivo."""
    existing_device = device_service.get_device_by_serial_number(db, serial_number)
    if existing_device is not None and existing_device.id != current_device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de serie ya está registrado",
        )


def validate_new_device(
    device_in: DeviceCreate, db: Session = Depends(get_db)
) -> DeviceCreate:
    """Valida el body del POST y que el número de serie no esté registrado."""
    _ensure_serial_number_available(db, device_in.serial_number)
    return device_in


def validate_device_replacement(
    device_in: DeviceCreate,
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> DeviceCreate:
    """Valida el body del PUT y que el número de serie no sea de otro dispositivo."""
    _ensure_serial_number_available(db, device_in.serial_number, device.id)
    return device_in


def validate_device_changes(
    device_in: DeviceUpdate,
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Valida el body del PATCH y devuelve solo los campos enviados."""
    changes = device_in.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    if "serial_number" in changes:
        _ensure_serial_number_available(db, changes["serial_number"], device.id)
    return changes


def ensure_device_can_be_deleted(device: Device = Depends(get_device_or_404)) -> Device:
    """Lanza 409 si el dispositivo tiene préstamos registrados."""
    if device.loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un dispositivo con préstamos registrados",
        )
    return device
