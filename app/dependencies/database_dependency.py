from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import get_session


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: una sesión de base de datos por petición."""
    yield from get_session()
