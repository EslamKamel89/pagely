import uuid
from typing import Any, Sequence

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import Role, User
from src.auth.schemas import RefreshTokenRequest
from src.auth.service import AuthService
from src.auth.utils import decode_token
from src.db.main import get_session
from src.errors import InvalidTokenError, ServerError, UnauthorizedError

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


async def get_current_user(
    token: str = Depends(oauth2_schema),
    service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as e:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    jti = payload.get("jti")
    if jti is None:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    blocked = await service.token_in_blocklist(jti)
    if blocked:
        raise UnauthorizedError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="your token in the blacklist",
        )
    if payload.get("type") != "access":
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can't use refresh token for normal authentication",
        )
    user_id = payload.get("sub", None)
    if user_id is None:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token",
        )
    user = await service.get_user_by_uuid(user_uuid)
    if user is None:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_user_from_refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if payload.get("type") != "refresh":
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token payload",
        )
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token",
        )
    user: User | None = await service.get_user_by_uuid(user_uuid)
    if user is None:
        raise InvalidTokenError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )
    return user


async def get_admin(user: User = Depends(get_current_user)):
    if user.role != Role.ADMIN:
        raise UnauthorizedError(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )
    return user


class RequireRoles:
    def __init__(self, roles: Sequence[Role]) -> None:
        self.roles = roles

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.roles:
            raise UnauthorizedError(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
            )
        return user
