import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.auth.models import User
from src.auth.schemas import SendMailSchema, UserCreate
from src.auth.utils import build_html_email, decode_urlsafe_token, hash_password
from src.config import settings
from src.db.redis import redis_client
from src.mail import create_message_schema, fm


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_uuid(self, user_uuid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.uid == user_uuid)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        return user

    async def get_user_with_books(self, user_uuid: uuid.UUID) -> User:
        stmt = (
            select(User)
            .options(selectinload(User.books))  # type: ignore
            .where(User.uid == user_uuid)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        return user

    async def check_username_email_unique(
        self, username: str, email: str
    ) -> tuple[bool, bool]:
        stmt = select(User).where(User.username == username)
        res = await self.session.execute(stmt)
        username_exist = res.scalar_one_or_none() is not None
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        email_exist = res.scalar_one_or_none() is not None
        return (username_exist, email_exist)

    async def create_user(self, user_data: UserCreate) -> User | tuple[bool, bool]:
        username_exist, email_exist = await self.check_username_email_unique(
            user_data.username, user_data.email
        )
        if username_exist or email_exist:
            return (username_exist, email_exist)
        password_hash = hash_password(user_data.password)
        raw_data = user_data.model_dump(exclude={"password"})
        raw_data["password_hash"] = password_hash
        user = User(**raw_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def verify_email(self, token: str) -> Optional[User]:
        data = decode_urlsafe_token(token)
        if data is not None:
            uid = data.get("uid", None)
            if uid:
                user = await self.get_user_by_uuid(uuid.UUID(uid))
                if user is not None:
                    if user.is_verified:
                        return user
                    user.is_verified = True
                    await self.session.commit()
                    await self.session.refresh(user)
                    return user
        return None

    async def add_jti_to_blocklist(self, jti: str) -> None:
        await redis_client.set(
            name=f"auth:blocklist:{jti}",
            value=1,
            ex=settings.ACCESS_EXPIRE_MINUTES * 60,
        )

    async def token_in_blocklist(self, jti: str) -> bool:
        res = await redis_client.get(f"auth:blocklist:{jti}")
        return res is not None

    async def send_mail(self, data: SendMailSchema):
        html_content = build_html_email(data.body)
        message = create_message_schema(
            recipients=data.recipients,
            subject=data.subject,
            body=html_content,
        )
        await fm.send_message(message)
