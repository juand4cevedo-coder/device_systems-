from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import (
    get_current_active_user,
    require_admin,
    require_staff,
)
from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import (
    ensure_user_can_be_deleted,
    get_user_or_404,
    validate_new_user,
    validate_user_changes,
    validate_user_replacement,
)
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.error_schema import error_responses
from app.schemas.loan_schema import LoanDetailResponse
from app.schemas.user_schema import (
    UserCreate,
    UserOrderBy,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services import loan_service, user_service
from app.services.loan_service import LoanFilters

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_user)],
    summary="Listar usuarios",
    description="Devuelve todos los usuarios. Se puede filtrar por rol (`role`) y por estado (`is_active`), combinando ambos filtros, y ordenar por nombre (`name`) o por fecha de creación (`created_at`, el valor por defecto).",
    response_description="Lista de usuarios que cumplen los filtros",
)
def list_users(
    role: UserRole | None = None,
    is_active: bool | None = None,
    order_by: UserOrderBy = UserOrderBy.CREATED_AT,
    db: Session = Depends(get_db),
) -> list[User]:
    return user_service.list_users(db, role, is_active, order_by)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses(404),
    dependencies=[Depends(get_current_active_user)],
    summary="Consultar un usuario",
    description="Devuelve el usuario que corresponde al ID indicado en la ruta. Responde 404 si no existe.",
    response_description="Datos del usuario solicitado",
)
def get_user(user: User = Depends(get_user_or_404)) -> User:
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(400),
    dependencies=[Depends(require_admin)],
    summary="Crear un usuario",
    description="Registra un nuevo usuario. Valida el nombre (mínimo 3 caracteres), el formato del correo, el rol y la fortaleza de la contraseña. Responde 400 si el correo ya está registrado.",
    response_description="Usuario creado",
)
def create_user(
    user_in: UserCreate = Depends(validate_new_user),
    db: Session = Depends(get_db),
) -> User:
    return user_service.create_user(db, user_in)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses(400, 404),
    dependencies=[Depends(require_staff)],
    summary="Reemplazar un usuario",
    description="Reemplaza por completo los datos de un usuario existente; deben enviarse todos los campos. Responde 404 si no existe y 400 si el correo pertenece a otro usuario.",
    response_description="Usuario con los datos reemplazados",
)
def update_user(
    user_in: UserUpdate = Depends(validate_user_replacement),
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> User:
    return user_service.update_user(db, user, user_in.model_dump())


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=error_responses(400, 404),
    dependencies=[Depends(require_staff)],
    summary="Actualizar parcialmente un usuario",
    description="Modifica solo los campos enviados. Responde 400 si el cuerpo no trae ningún campo o si el correo pertenece a otro usuario, y 404 si el usuario no existe.",
    response_description="Usuario con los cambios aplicados",
)
def patch_user(
    changes: dict[str, Any] = Depends(validate_user_changes),
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
) -> User:
    return user_service.update_user(db, user, changes)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_responses(404, 409),
    dependencies=[Depends(require_admin)],
    summary="Eliminar un usuario",
    description="Elimina el usuario indicado. Responde 404 si no existe y 409 si tiene préstamos registrados.",
    response_description="Usuario eliminado; la respuesta no tiene cuerpo",
)
def delete_user(
    user: User = Depends(ensure_user_can_be_deleted), db: Session = Depends(get_db)
) -> None:
    user_service.delete_user(db, user)


@router.get(
    "/{user_id}/loans",
    response_model=list[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    responses=error_responses(404),
    dependencies=[Depends(require_staff)],
    summary="Consultar los préstamos de un usuario",
    description="Devuelve el historial de préstamos del usuario indicado, con los datos de cada dispositivo. Responde 404 si el usuario no existe.",
    response_description="Préstamos del usuario",
)
def list_user_loans(
    user: User = Depends(get_user_or_404), db: Session = Depends(get_db)
) -> list[Loan]:
    return loan_service.search_loans(db, LoanFilters(user_id=user.id))
