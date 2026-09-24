from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import (
    get_user_or_404,
    set_api_headers,
    validate_new_user,
    validate_user_changes,
    validate_user_replacement,
)
from app.models.user_model import User
from app.schemas.user_schema import (
    UserCreate,
    UserOrderBy,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(set_api_headers)]
)


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
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
    summary="Crear un usuario",
    description="Registra un nuevo usuario. Valida el nombre (mínimo 3 caracteres), el formato del correo y el rol. Responde 400 si el correo ya está registrado.",
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
    summary="Eliminar un usuario",
    description="Elimina el usuario indicado. Responde 404 si no existe.",
    response_description="Usuario eliminado; la respuesta no tiene cuerpo",
)
def delete_user(
    user: User = Depends(get_user_or_404), db: Session = Depends(get_db)
) -> None:
    user_service.delete_user(db, user)
