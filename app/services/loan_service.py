from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User, utc_now
from app.schemas.loan_schema import LoanStatus


@dataclass(frozen=True)
class LoanFilters:
    """Filtros opcionales para consultar préstamos."""

    status: LoanStatus | None = None
    user_id: int | None = None
    device_id: int | None = None
    user_email: str | None = None
    device_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None


def search_loans(db: Session, filters: LoanFilters | None = None) -> list[Loan]:
    """Consulta préstamos uniendo usuarios y dispositivos, con filtros opcionales."""
    filters = filters or LoanFilters()

    query = (
        select(Loan)
        .join(Loan.user)
        .join(Loan.device)
        .options(contains_eager(Loan.user), contains_eager(Loan.device))
    )

    conditions = []
    if filters.status is not None:
        conditions.append(Loan.status == filters.status.value)
    if filters.user_id is not None:
        conditions.append(Loan.user_id == filters.user_id)
    if filters.device_id is not None:
        conditions.append(Loan.device_id == filters.device_id)
    if filters.user_email:
        conditions.append(User.email.ilike(f"%{filters.user_email.strip()}%"))
    if filters.device_type:
        conditions.append(
            func.lower(Device.device_type) == filters.device_type.strip().lower()
        )
    if filters.date_from is not None:
        conditions.append(
            Loan.loan_date >= datetime.combine(filters.date_from, time.min)
        )
    if filters.date_to is not None:
        # Inclusiva: hasta el final del día indicado.
        conditions.append(
            Loan.loan_date
            < datetime.combine(filters.date_to + timedelta(days=1), time.min)
        )

    if conditions:
        query = query.where(and_(*conditions))
    return list(db.scalars(query.order_by(Loan.id)).all())


def get_loan_by_id(db: Session, loan_id: int) -> Loan | None:
    query = (
        select(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .where(Loan.id == loan_id)
    )
    return db.scalar(query)


def create_loan(db: Session, user: User, device: Device) -> Loan:
    loan = Loan(user_id=user.id, device_id=device.id, status=LoanStatus.ACTIVE.value)
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan) -> Loan:
    loan.status = LoanStatus.RETURNED.value
    loan.return_date = utc_now()
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan
