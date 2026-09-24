from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate


def list_devices(
    db: Session,
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
) -> list[Device]:
    query = select(Device)
    if device_type:
        query = query.where(
            func.lower(Device.device_type) == device_type.strip().lower()
        )
    if is_available is not None:
        query = query.where(Device.is_available == is_available)
    if brand:
        query = query.where(func.lower(Device.brand) == brand.strip().lower())
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Device.name.ilike(pattern),
                Device.serial_number.ilike(pattern),
                Device.device_type.ilike(pattern),
                Device.brand.ilike(pattern),
            )
        )
    return list(db.scalars(query.order_by(Device.id)).all())


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return db.get(Device, device_id)


def get_device_by_serial_number(db: Session, serial_number: str) -> Device | None:
    return db.scalar(
        select(Device).where(func.lower(Device.serial_number) == serial_number.lower())
    )


def create_device(db: Session, device_in: DeviceCreate) -> Device:
    device = Device(**device_in.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device: Device, changes: dict[str, Any]) -> Device:
    for field, value in changes.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    db.delete(device)
    db.commit()
