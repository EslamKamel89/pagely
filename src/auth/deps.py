import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import CurrentUser
from src.auth.service import AuthService
from src.auth.utils import decode_token
from src.db.main import get_session

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


async def get_current_user(
    token: str = Depends(oauth2_schema),
    service: AuthService = Depends(get_auth_service),
) -> CurrentUser:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can't use refresh token for normal authentication",
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
    user = service.get_user_by_uuid(user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return CurrentUser(uid=user_uuid)
