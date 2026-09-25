from sqlalchemy.orm import Session

from app.auth.security import verify_password
from app.models.user_model import User
from app.services import user_service


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verifica las credenciales. Devuelve el usuario si son válidas, o None."""
    user = user_service.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
