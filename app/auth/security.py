"""Utilidades de seguridad: hash de contraseñas y tokens JWT."""

import logging
import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# passlib registra un error inofensivo al detectar bcrypt >= 5; como el proyecto
# fija bcrypt < 5, se silencia para no ensuciar los logs ni las capturas.
logging.getLogger("passlib").setLevel(logging.CRITICAL)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no está configurada. Copia .env.example a .env y genera una clave con: "
        'uv run python -c "import secrets; print(secrets.token_hex(32))"'
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Crea un token JWT firmado, con expiración."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un token JWT. Devuelve None si es inválido o expiró."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
