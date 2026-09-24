from fastapi import FastAPI

from contextlib import asynccontextmanager

from app.database.connection import engine
from app.database.migration_check import ensure_database_is_migrated

from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router


tags_metadata = [
    {
        "name": "Users",
        "description": "Gestión de usuarios: consulta, registro, actualización y eliminación.",
    },
    {
        "name": "Devices",
        "description": "Gestión de dispositivos tecnológicos disponibles para préstamo.",
    },
    {
        "name": "Loans",
        "description": "Gestión de préstamos de dispositivos a usuarios.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_is_migrated(engine)
    yield


app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems",
    version="2.2.0",
    contact={
        "name": "Tu nombre completo",
        "url": "https://github.com/juand4cevedo-coder",
    },
    openapi_tags=tags_metadata,
)

app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)
