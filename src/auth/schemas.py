import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


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
