from typing import Any
from app.auth.security import get_password_hash

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserOrderBy, UserRole


def list_users(
    db: Session,
    role: UserRole | None = None,
    is_active: bool | None = None,
    order_by: UserOrderBy = UserOrderBy.CREATED_AT,
) -> list[User]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    sort_column = User.name if order_by == UserOrderBy.NAME else User.created_at
    query = query.order_by(sort_column, User.id)
    return list(db.scalars(query).all())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.lower()))


def create_user(db: Session, user_in: UserCreate) -> User:
    user_data = user_in.model_dump(exclude={"password"})
    user = User(hashed_password=get_password_hash(user_in.password), **user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, changes: dict[str, Any]) -> User:
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
