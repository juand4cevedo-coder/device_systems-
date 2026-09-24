from fastapi import APIRouter, HTTPException, status

from app.schemas.user_schema import User, UserRole

router = APIRouter(prefix="/users")

# Almacenamiento temporal en memoria; en EV08 pasa a app/data/users_db.py.
users_db: list[User] = [
    User(
        id=1,
        name="Ana Pérez",
        email="ana@sena.edu.co",
        role=UserRole.ADMIN,
        is_active=True,
    ),
    User(
        id=2,
        name="Carlos Gómez",
        email="carlos@sena.edu.co",
        role=UserRole.SUPPORT,
        is_active=True,
    ),
    User(
        id=3,
        name="Laura Torres",
        email="laura@sena.edu.co",
        role=UserRole.USER,
        is_active=False,
    ),
]


@router.get("")
def list_users(
    role: UserRole | None = None, is_active: bool | None = None
) -> list[User]:
    users = users_db
    if role is not None:
        users = [user for user in users if user.role == role]
    if is_active is not None:
        users = [user for user in users if user.is_active == is_active]
    return users


@router.get("/{user_id}")
def get_user(user_id: int) -> User:
    user = next((user for user in users_db if user.id == user_id), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return user
