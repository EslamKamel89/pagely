import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.auth.models import User
from src.auth.schemas import CurrentUser
from src.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(
    user: User,
    extra: dict[str, Any] | None = None,
    refresh: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user.uid),
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "type": "refresh" if refresh else "access",
    }
    if extra:
        payload.update(extra)
    expire = now + (
        timedelta(days=settings.REFRESH_EXPIRE_DAYS)
        if refresh
        else timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


async def get_current_user(token: str = Depends(oauth2_schema)) -> CurrentUser:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user_id = payload.get("sub", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token",
        )
    return CurrentUser(uid=user_uuid)
