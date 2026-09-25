from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario autenticado a partir del token Bearer. Lanza 401 si es inválido."""
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise _CREDENTIALS_EXCEPTION

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise _CREDENTIALS_EXCEPTION from None

    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise _CREDENTIALS_EXCEPTION
    return user


from app.schemas.auth_schema import UserRegister


def validate_new_registration(
    user_in: UserRegister, db: Session = Depends(get_db)
) -> UserRegister:
    """Valida que el correo no esté registrado antes de crear la cuenta."""
    if user_service.get_user_by_email(db, user_in.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    return user_in


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Exige que el usuario autenticado esté activo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )
    return current_user


def require_roles(*roles: str):
    """Crea una dependencia que exige uno de los roles indicados. Lanza 403 si no lo tiene."""
    allowed_roles = set(roles)

    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta operación",
            )
        return current_user

    return dependency


require_admin = require_roles("admin")
require_staff = require_roles("admin", "support")
