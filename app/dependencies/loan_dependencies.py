from datetime import date
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanStatus
from app.services import device_service, loan_service, user_service


def get_loan_or_404(loan_id: int, db: Session = Depends(get_db)) -> Loan:
    """Obtiene el préstamo por ID o lanza 404 si no existe."""
    loan = loan_service.get_loan_by_id(db, loan_id)
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado"
        )
    return loan


def validate_new_loan(
    loan_in: LoanCreate, db: Session = Depends(get_db)
) -> tuple[User, Device]:
    """Valida el body del POST: el usuario y el dispositivo existen y el dispositivo está disponible."""
    user = user_service.get_user_by_id(db, loan_in.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    device = device_service.get_device_by_id(db, loan_in.device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado"
        )

    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no está disponible",
        )
    return user, device


def ensure_loan_can_be_returned(loan: Loan = Depends(get_loan_or_404)) -> Loan:
    """Lanza 409 si el préstamo ya fue devuelto."""
    if loan.status == LoanStatus.RETURNED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El préstamo ya fue devuelto"
        )
    return loan


def get_loan_filters(
    loan_status: Annotated[
        LoanStatus | None, Query(alias="status", description="Estado del préstamo")
    ] = None,
    user_id: Annotated[int | None, Query(description="ID del usuario")] = None,
    device_id: Annotated[int | None, Query(description="ID del dispositivo")] = None,
    user_email: Annotated[
        str | None,
        Query(
            description="Correo del usuario (búsqueda parcial, sin distinguir mayúsculas)"
        ),
    ] = None,
    device_type: Annotated[
        str | None,
        Query(description="Tipo de dispositivo (sin distinguir mayúsculas)"),
    ] = None,
    date_from: Annotated[
        date | None,
        Query(description="Fecha de préstamo desde, inclusive (AAAA-MM-DD)"),
    ] = None,
    date_to: Annotated[
        date | None,
        Query(description="Fecha de préstamo hasta, inclusive (AAAA-MM-DD)"),
    ] = None,
) -> loan_service.LoanFilters:
    """Reúne y valida los filtros opcionales de la consulta de préstamos."""
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=422, detail="date_from no puede ser posterior a date_to"
        )
    return loan_service.LoanFilters(
        status=loan_status,
        user_id=user_id,
        device_id=device_id,
        user_email=user_email,
        device_type=device_type,
        date_from=date_from,
        date_to=date_to,
    )
