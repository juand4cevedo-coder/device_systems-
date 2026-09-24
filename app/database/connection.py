from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///./device_systems.db"

# check_same_thread=False: FastAPI puede atender una misma petición desde hilos
# distintos y SQLite, por defecto, no lo permite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base declarativa de la que heredan todos los modelos SQLAlchemy."""


def get_session() -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos y la cierra al terminar."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
