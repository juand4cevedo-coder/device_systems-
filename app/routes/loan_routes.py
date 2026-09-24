from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.loan_dependencies import (
    ensure_loan_can_be_returned,
    get_loan_or_404,
    validate_new_loan,
)
from app.dependencies.user_dependencies import set_api_headers
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanDetailResponse, LoanResponse
from app.services import loan_service

router = APIRouter(
    prefix="/loans", tags=["Loans"], dependencies=[Depends(set_api_headers)]
)


@router.get(
    "",
    response_model=list[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos",
    description="Devuelve todos los préstamos registrados, con los datos básicos del usuario y del dispositivo.",
    response_description="Lista de préstamos con su usuario y su dispositivo",
)
def list_loans(db: Session = Depends(get_db)) -> list[Loan]:
    return loan_service.list_loans(db)


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar un préstamo",
    description="Devuelve el préstamo que corresponde al ID indicado, con el usuario y el dispositivo. Responde 404 si no existe.",
    response_description="Datos del préstamo solicitado",
)
def get_loan(loan: Loan = Depends(get_loan_or_404)) -> Loan:
    return loan


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un préstamo",
    description="Presta un dispositivo a un usuario y lo marca como no disponible. Responde 404 si el usuario o el dispositivo no existen y 409 si el dispositivo no está disponible.",
    response_description="Préstamo registrado",
)
def create_loan(
    user_and_device: tuple[User, Device] = Depends(validate_new_loan),
    db: Session = Depends(get_db),
) -> Loan:
    user, device = user_and_device
    return loan_service.create_loan(db, user, device)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Devolver un dispositivo",
    description="Marca el préstamo como devuelto, registra la fecha de devolución y deja el dispositivo disponible. Responde 404 si el préstamo no existe y 409 si ya fue devuelto.",
    response_description="Préstamo devuelto",
)
def return_loan(
    loan: Loan = Depends(ensure_loan_can_be_returned),
    db: Session = Depends(get_db),
) -> Loan:
    return loan_service.return_loan(db, loan)
