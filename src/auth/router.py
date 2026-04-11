import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.deps import (
    get_auth_service,
    get_current_user,
    get_user_from_refresh_token,
    oauth2_schema,
)
from src.auth.models import User
from src.auth.schemas import (
    RefreshTokenRequest,
    SendMailSchema,
    TokenResponse,
    UserBase,
    UserCreate,
    UserWithBooks,
)
from src.auth.service import AuthService
from src.auth.utils import (
    build_html_email,
    create_token,
    create_url_safe_token,
    decode_token,
    verify_password,
)
from src.celery import send_mail
from src.config import settings

router = APIRouter(tags=["auth"])


@router.post("/send-mail", status_code=status.HTTP_200_OK)
async def send_test_mail(
    data: SendMailSchema,
    # background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    # await auth_service.send_mail(data)
    # background_tasks.add_task(auth_service.send_mail, data)
    send_mail.delay(data.to_config_dict())  # type: ignore
    return {
        "message": "Test email sent",
    }


@router.post(
    "/signup",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserCreate,
    # background_tasks: BackgroundTasks,
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
    token = create_url_safe_token({"uid": str(res.uid)})
    link = f"{settings.APP_SCHEME}://{settings.DOMAIN}/api/v1/auth/verify/{token}"
    html_content = f"""
        <h1>Verify your email</h1>
        <p> Please click this <a href="{link}">link</a> to verify your email </p>
        """
    # background_tasks.add_task(
    #     service.send_mail,
    #     SendMailSchema(
    #         recipients=[res.email],
    #         body=html_content,
    #         subject="Please verify your email",
    #     ),
    # )
    send_mail.delay(  # type: ignore
        SendMailSchema(
            recipients=[res.email],
            body=html_content,
            subject="Please verify your email",
        ).to_config_dict(),
    )
    return res


@router.get("/verify/{token}")
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.verify_email(token)
    if user:
        return HTMLResponse(
            """
            <h2>Email Verified ✅</h2>
            <p>You can now return to the app.</p>
            """
        )
    return HTMLResponse("Something went wrong")


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


@router.get("/me", response_model=UserWithBooks)
async def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_user_with_books(current_user.uid)


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
