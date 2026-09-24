from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def ensure_database_is_migrated(engine: Engine) -> None:
    """Detiene el arranque si la base de datos no está en la última revisión de Alembic."""
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    head = ScriptDirectory.from_config(config).get_current_head()

    with engine.connect() as connection:
        current = MigrationContext.configure(connection).get_current_revision()

    if current != head:
        raise RuntimeError(
            "La base de datos no está actualizada "
            f"(revisión actual: {current or 'ninguna'}, esperada: {head}). "
            "Ejecuta: uv run alembic upgrade head"
        )
