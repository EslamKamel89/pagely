import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.common.schemas import BookBase, UserBase


class ReviewBase(BaseModel):
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    review_text: str
    rating: int
    created_at: datetime
    updated_at: datetime
    user: UserBase
    book: BookBase
    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    review_text: str = Field(min_length=2)
    rating: int = Field(ge=1, le=5)


class ReviewUpdate(BaseModel):
    review_text: str | None = Field(min_length=2, default=None)
    rating: int | None = Field(ge=1, le=5, default=None)
