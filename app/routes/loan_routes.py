from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core_limiter import limiter
from app.dependencies.auth_dependency import get_current_active_user, require_staff
from app.dependencies.database_dependency import get_db
from app.dependencies.loan_dependencies import (
    ensure_loan_can_be_returned,
    get_loan_filters,
    get_loan_or_404,
    validate_new_loan,
)
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.error_schema import error_responses
from app.schemas.loan_schema import LoanDetailResponse, LoanResponse
from app.services import loan_service
from app.services.loan_service import LoanFilters

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get(
    "",
    response_model=list[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    responses=error_responses(401, 403),
    dependencies=[Depends(require_staff)],
    summary="Listar préstamos",
    description="Devuelve los préstamos con los datos del usuario y del dispositivo. Se puede filtrar por estado (`status`), usuario (`user_id`), dispositivo (`device_id`), correo del usuario (`user_email`), tipo de dispositivo (`device_type`) y rango de fechas de préstamo (`date_from`, `date_to`). Requiere rol admin o support.",
    response_description="Lista de préstamos que cumplen los filtros",
)
def list_loans(
    filters: LoanFilters = Depends(get_loan_filters),
    db: Session = Depends(get_db),
) -> list[Loan]:
    return loan_service.search_loans(db, filters)


# /details se declara antes que /{loan_id}; si no, FastAPI intentaría convertir "details" en un número.
@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    responses=error_responses(401, 403),
    dependencies=[Depends(require_staff)],
    summary="Listar préstamos con detalle",
    description="Consulta que une préstamos, usuarios y dispositivos (`JOIN`) y devuelve cada préstamo con la información relacionada. Requiere rol admin o support. Acepta los mismos filtros que `GET /loans`.",
    response_description="Lista de préstamos con su usuario y su dispositivo",
)
def list_loan_details(
    filters: LoanFilters = Depends(get_loan_filters),
    db: Session = Depends(get_db),
) -> list[Loan]:
    return loan_service.search_loans(db, filters)


@router.get(
    "/{loan_id}",
    response_model=LoanDetailResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses(401, 404),
    dependencies=[Depends(get_current_active_user)],
    summary="Consultar un préstamo",
    description="Devuelve el préstamo que corresponde al ID indicado, con el usuario y el dispositivo. Requiere estar autenticado. Responde 404 si no existe.",
    response_description="Datos del préstamo solicitado",
)
def get_loan(loan: Loan = Depends(get_loan_or_404)) -> Loan:
    return loan


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(401, 404, 409),
    dependencies=[Depends(get_current_active_user)],
    summary="Registrar un préstamo",
    description="Presta un dispositivo a un usuario y lo marca como no disponible. Requiere estar autenticado. Responde 404 si el usuario o el dispositivo no existen y 409 si el dispositivo no está disponible. Límite: 10 solicitudes por minuto.",
    response_description="Préstamo registrado",
)
@limiter.limit("10/minute")
def create_loan(
    request: Request,
    user_and_device: tuple[User, Device] = Depends(validate_new_loan),
    db: Session = Depends(get_db),
) -> Loan:
    user, device = user_and_device
    return loan_service.create_loan(db, user, device)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses(401, 403, 404, 409),
    dependencies=[Depends(require_staff)],
    summary="Devolver un dispositivo",
    description="Marca el préstamo como devuelto, registra la fecha de devolución y deja el dispositivo disponible. Requiere rol admin o support. Responde 404 si el préstamo no existe y 409 si ya fue devuelto.",
    response_description="Préstamo devuelto",
)
def return_loan(
    loan: Loan = Depends(ensure_loan_can_be_returned),
    db: Session = Depends(get_db),
) -> Loan:
    return loan_service.return_loan(db, loan)
