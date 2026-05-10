from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt
from app.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_hex(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            raise ValueError("Tip de token incorect")
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token-ul nu conține user_id")
        return int(user_id)
    except JWTError as e:
        raise ValueError(f"Token invalid: {e}")
