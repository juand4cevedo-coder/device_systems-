from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User, utc_now
from app.schemas.loan_schema import LoanStatus


def _loans_with_details():
    """Consulta base de préstamos que carga el usuario y el dispositivo con un JOIN."""
    return select(Loan).options(joinedload(Loan.user), joinedload(Loan.device))


def list_loans(db: Session) -> list[Loan]:
    return list(db.scalars(_loans_with_details().order_by(Loan.id)).all())


def get_loan_by_id(db: Session, loan_id: int) -> Loan | None:
    return db.scalar(_loans_with_details().where(Loan.id == loan_id))


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
