from typing import Any
from app.data.users_db import users_db
from app.schemas.user_schema import User, UserCreate, UserRole


def list_users(
    role: UserRole | None = None, is_active: bool | None = None
) -> list[User]:
    users = users_db
    if role is not None:
        users = [user for user in users if user.role == role]
    if is_active is not None:
        users = [user for user in users if user.is_active == is_active]
    return users


def get_user_by_id(user_id: int) -> User | None:
    return next((user for user in users_db if user.id == user_id), None)


def get_user_by_email(email: str) -> User | None:
    email = email.lower()
    return next((user for user in users_db if user.email.lower() == email), None)


def create_user(user_in: UserCreate) -> User:
    new_user = User(
        id=max((user.id for user in users_db), default=0) + 1, **user_in.model_dump()
    )
    users_db.append(new_user)
    return new_user


def update_user(user: User, changes: dict[str, Any]) -> User:
    updated_user = user.model_copy(update=changes)
    users_db[users_db.index(user)] = updated_user
    return updated_user


def delete_user(user: User) -> None:
    users_db.remove(user)
