import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.deps import (
    get_auth_service,
    get_current_user,
    get_user_from_refresh_token,
    oauth2_schema,
)
from src.auth.models import User
from src.auth.schemas import RefreshTokenRequest, TokenResponse, UserBase, UserCreate
from src.auth.service import AuthService
from src.auth.utils import create_token, decode_token, verify_password

router = APIRouter(tags=["auth"])


@router.post(
    "/signup",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> User:
    res = await service.create_user(user_data)
    if not isinstance(res, User):
        username_exist, email_exist = res
        messages = []
        if username_exist:
            messages.append("User with this username already exist")
        if email_exist:
            messages.append("User with this email already exist")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=", ".join(messages)
        )

    return res


@router.post("/signin", response_model=TokenResponse)
async def signin(
    payload: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    user: User | None = await service.get_user_by_email(payload.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email invalid",
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password invalid",
        )
    access_token = create_token(user)
    refresh_token = create_token(user, refresh=True)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserBase.model_validate(user),
    )


@router.get("/me", response_model=UserBase)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    user: User = Depends(get_user_from_refresh_token),
):
    access_token = create_token(user, refresh=False)
    return TokenResponse(
        refresh_token=data.refresh_token,
        access_token=access_token,
        user=UserBase.model_validate(user),
        token_type="bearer",
    )


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    token: str = Depends(oauth2_schema),
    service: AuthService = Depends(get_auth_service),
):

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
            detail="Invalid token type",
        )
    jti = payload.get("jti")
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload"
        )
    await service.add_jti_to_blocklist(jti)
    return {"message": "you Logged out successfully"}
