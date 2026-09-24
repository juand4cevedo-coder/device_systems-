from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.user_schema import (
    User,
    UserCreate,
    UserPatch,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/users")


def set_api_headers(response: Response) -> None:
    """Agrega las cabeceras personalizadas de la API a la respuesta."""
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"


@router.get("", response_model=list[UserResponse])
def list_users(
    response: Response,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> list[User]:
    set_api_headers(response)
    return user_service.list_users(role, is_active)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response) -> User:
    set_api_headers(response)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, response: Response) -> User:
    set_api_headers(response)
    if user_service.get_user_by_email(user_in.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    return user_service.create_user(user_in)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, response: Response) -> User:
    set_api_headers(response)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    existing_user = user_service.get_user_by_email(user_in.email)
    if existing_user is not None and existing_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    return user_service.update_user(user, user_in.model_dump())


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, user_in: UserPatch, response: Response) -> User:
    set_api_headers(response)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    changes = user_in.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    if "email" in changes:
        existing_user = user_service.get_user_by_email(changes["email"])
        if existing_user is not None and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )

    return user_service.update_user(user, changes)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, response: Response) -> None:
    set_api_headers(response)
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    user_service.delete_user(user)
