from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.models import User
from src.auth.schemas import SigninData, UserBase, UserCreate
from src.auth.service import AuthService, get_auth_service
from src.auth.utils import create_token, verify_password

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


@router.post("/signin")
async def signin(
    data: SigninData,
    service: AuthService = Depends(get_auth_service),
):
    user = await service.get_user_by_email(data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email invalid",
        )
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password invalid",
        )
    access_token = create_token(user)
    refresh_token = create_token(user, refresh=True)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "user": UserBase.model_validate(user),
    }
