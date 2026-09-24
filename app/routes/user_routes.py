from typing import Any

from fastapi import APIRouter, Depends, status

from app.dependencies.user_dependencies import (
    get_user_or_404,
    set_api_headers,
    validate_new_user,
    validate_user_changes,
    validate_user_replacement,
)
from app.schemas.user_schema import User, UserCreate, UserResponse, UserRole, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", dependencies=[Depends(set_api_headers)])


@router.get("", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_users(
    role: UserRole | None = None, is_active: bool | None = None
) -> list[User]:
    return user_service.list_users(role, is_active)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user: User = Depends(get_user_or_404)) -> User:
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate = Depends(validate_new_user)) -> User:
    return user_service.create_user(user_in)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_in: UserUpdate = Depends(validate_user_replacement),
    user: User = Depends(get_user_or_404),
) -> User:
    return user_service.update_user(user, user_in.model_dump())


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def patch_user(
    changes: dict[str, Any] = Depends(validate_user_changes),
    user: User = Depends(get_user_or_404),
) -> User:
    return user_service.update_user(user, changes)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user: User = Depends(get_user_or_404)) -> None:
    user_service.delete_user(user)
