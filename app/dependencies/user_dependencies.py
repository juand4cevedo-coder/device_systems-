from typing import Any

from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserUpdate
from app.services import user_service


def set_api_headers(response: Response) -> None:
    """Agrega las cabeceras personalizadas de la API a cada respuesta."""
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"


def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> User:
    """Obtiene el usuario por ID o lanza 404 si no existe."""
    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return user


def _ensure_email_available(
    db: Session, email: str, current_user_id: int | None = None
) -> None:
    """Lanza 400 si el correo pertenece a otro usuario."""
    existing_user = user_service.get_user_by_email(db, email)
    if existing_user is not None and existing_user.id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )


def validate_new_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserCreate:
    """Valida el body del POST y que el correo no esté registrado."""
    _ensure_email_available(db, user_in.email)
    return user_in


def validate_user_replacement(
    user_in: UserUpdate,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> UserUpdate:
    """Valida el body del PUT y que el correo no sea de otro usuario."""
    _ensure_email_available(db, user_in.email, user.id)
    return user_in


def validate_user_changes(
    user_in: UserPatch,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Valida el body del PATCH y devuelve solo los campos enviados."""
    changes = user_in.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    if "email" in changes:
        _ensure_email_available(db, changes["email"], user.id)
    return changes
