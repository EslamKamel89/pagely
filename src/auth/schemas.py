import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, TypedDict

from pydantic import BaseModel, EmailStr, Field

from src.common.schemas import BookBase, UserBase


class UserWithBooks(UserBase):
    books: list[BookBase]


class UserCreate(BaseModel):
    username: str = Field(max_length=20)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)
    email: EmailStr
    password: str = Field(max_length=255)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=20)
    first_name: Optional[str] = Field(None, max_length=20)
    last_name: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class SigninData(BaseModel):
    email: EmailStr
    password: str = Field(max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBase


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SendMailSchema(BaseModel):
    recipients: list[EmailStr]
    subject: str
    body: str

    def to_config_dict(self) -> "SendMailConfig":
        return {
            "recipients": self.recipients,
            "subject": self.subject,
            "body": self.body,
        }


class SendMailConfig(TypedDict):
    recipients: list[str]
    subject: str
    body: str
