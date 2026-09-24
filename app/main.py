from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models import user_model  # noqa: F401  (registra el modelo en Base.metadata)
from app.routes.user_routes import router as user_router

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Users",
        "description": "Gestión de usuarios: consulta, registro, actualización y eliminación.",
    },
]

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems",
    version="2.1.0",
    contact={
        "name": "Tu nombre completo",
        "url": "https://github.com/juand4cevedo-coder",
    },
    openapi_tags=tags_metadata,
)

app.include_router(user_router)
