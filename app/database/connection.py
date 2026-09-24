from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///./device_systems.db"

# check_same_thread=False: FastAPI puede atender una misma petición desde hilos
# distintos y SQLite, por defecto, no lo permite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    """SQLite no aplica las claves foráneas por defecto: se activan en cada conexión."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
