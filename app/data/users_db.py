from app.schemas.user_schema import User, UserRole

# Simulación de base de datos en memoria; en EV09 se reemplaza por SQLAlchemy.
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
