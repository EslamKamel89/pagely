import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class BookBase(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
