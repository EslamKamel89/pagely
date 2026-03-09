import uuid
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.models import User
from src.auth.schemas import UserCreate
from src.auth.utils import hash_password
from src.db.main import get_session


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_uuid(self, user_uuid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.uid == user_uuid)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
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


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)
