from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.device_dependencies import (
    ensure_device_can_be_deleted,
    get_device_or_404,
    validate_device_changes,
    validate_device_replacement,
    validate_new_device,
)
from app.dependencies.user_dependencies import set_api_headers
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceResponse
from app.services import device_service

router = APIRouter(
    prefix="/devices", tags=["Devices"], dependencies=[Depends(set_api_headers)]
)


@router.get(
    "",
    response_model=list[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar dispositivos",
    description="Devuelve todos los dispositivos. Se puede filtrar por tipo (`device_type`), disponibilidad (`is_available`) y marca (`brand`), y buscar texto (`search`) en el nombre, el número de serie, el tipo y la marca. Los filtros se pueden combinar.",
    response_description="Lista de dispositivos que cumplen los filtros",
)
def list_devices(
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[Device]:
    return device_service.list_devices(db, device_type, is_available, brand, search)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar un dispositivo",
    description="Devuelve el dispositivo que corresponde al ID indicado en la ruta. Responde 404 si no existe.",
    response_description="Datos del dispositivo solicitado",
)
def get_device(device: Device = Depends(get_device_or_404)) -> Device:
    return device


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un dispositivo",
    description="Registra un nuevo dispositivo, disponible para préstamo. Responde 400 si el número de serie ya está registrado.",
    response_description="Dispositivo creado",
)
def create_device(
    device_in: DeviceCreate = Depends(validate_new_device),
    db: Session = Depends(get_db),
) -> Device:
    return device_service.create_device(db, device_in)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Reemplazar un dispositivo",
    description="Reemplaza por completo los datos de un dispositivo existente. Responde 404 si no existe y 400 si el número de serie pertenece a otro dispositivo.",
    response_description="Dispositivo con los datos reemplazados",
)
def update_device(
    device_in: DeviceCreate = Depends(validate_device_replacement),
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> Device:
    return device_service.update_device(db, device, device_in.model_dump())


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un dispositivo",
    description="Modifica solo los campos enviados. Responde 400 si el cuerpo no trae ningún campo o si el número de serie pertenece a otro dispositivo, y 404 si el dispositivo no existe.",
    response_description="Dispositivo con los cambios aplicados",
)
def patch_device(
    changes: dict[str, Any] = Depends(validate_device_changes),
    device: Device = Depends(get_device_or_404),
    db: Session = Depends(get_db),
) -> Device:
    return device_service.update_device(db, device, changes)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un dispositivo",
    description="Elimina el dispositivo indicado. Responde 404 si no existe y 409 si tiene préstamos registrados.",
    response_description="Dispositivo eliminado; la respuesta no tiene cuerpo",
)
def delete_device(
    device: Device = Depends(ensure_device_can_be_deleted),
    db: Session = Depends(get_db),
) -> None:
    device_service.delete_device(db, device)
