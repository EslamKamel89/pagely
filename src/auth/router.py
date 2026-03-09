from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.models import User
from src.auth.schemas import UserBase, UserCreate
from src.auth.service import AuthService, get_auth_service

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
