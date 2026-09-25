from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_service import authenticate_user
from app.auth.security import create_access_token
from app.dependencies.auth_dependency import get_current_user, validate_new_registration
from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import set_api_headers
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserRegister
from app.schemas.error_schema import error_responses
from app.schemas.user_schema import UserCreate, UserResponse
from app.services import user_service

router = APIRouter(
    prefix="/auth", tags=["Auth"], dependencies=[Depends(set_api_headers)]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(400),
    summary="Registrar un usuario",
    description="Crea una cuenta con contraseña segura. Valida el nombre, el formato del correo, que no esté registrado, la fortaleza de la contraseña y el rol. Responde 400 si el correo ya existe.",
    response_description="Usuario registrado",
)
def register(
    user_in: UserRegister = Depends(validate_new_registration),
    db: Session = Depends(get_db),
) -> User:
    user_create = UserCreate(
        name=user_in.name,
        email=user_in.email,
        role=user_in.role,
        password=user_in.password,
    )
    return user_service.create_user(db, user_create)


@router.post(
    "/login",
    response_model=Token,
    responses=error_responses(401),
    summary="Iniciar sesión",
    description="Autentica al usuario y devuelve un token JWT. Recibe las credenciales como formulario OAuth2 (`username` = correo, `password`), no como JSON.",
    response_description="Token de acceso",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token({"sub": str(user.id)}))


@router.get(
    "/me",
    response_model=UserResponse,
    responses=error_responses(401),
    summary="Consultar el perfil propio",
    description="Devuelve los datos del usuario autenticado, a partir del token enviado en `Authorization: Bearer <token>`.",
    response_description="Datos del usuario autenticado",
)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
