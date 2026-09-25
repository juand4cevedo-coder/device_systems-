from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.auth.auth_routes import router as auth_router
from app.core_limiter import limiter

from contextlib import asynccontextmanager

from app.database.connection import engine
from app.database.migration_check import ensure_database_is_migrated

from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.middlewares.request_middleware import RequestContextMiddleware

from slowapi.errors import RateLimitExceeded

from app.schemas.error_schema import ErrorResponse


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
    {
        "name": "Auth",
        "description": "Registro, autenticación, perfil del usuario autenticado y seguridad: hash de contraseñas, tokens JWT y control de acceso por rol.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database_is_migrated(engine)
    yield


app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems",
    version="3.0.0",
    contact={
        "name": "Tu nombre completo",
        "url": "https://github.com/juand4cevedo-coder",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            detail="Demasiadas solicitudes. Intenta de nuevo más tarde."
        ).model_dump(),
    )


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)
app.add_middleware(RequestContextMiddleware)
