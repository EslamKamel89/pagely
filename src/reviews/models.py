import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.auth.models import User
    from src.books.models import Book

import src.db.models_base as base


class Review(SQLModel, table=True):
    __tablename__ = "reviews"  # type: ignore
    user_uid: uuid.UUID = Field(foreign_key="users.uid", primary_key=True)
    book_uid: uuid.UUID = Field(foreign_key="books.uid", primary_key=True)
    review_text: str
    rating: int = Field(ge=1, le=5)
    created_at: datetime = base.created_at()
    updated_at: datetime = base.updated_at()
    user: "User" = Relationship(back_populates="reviews")
    book: "Book" = Relationship(back_populates="reviews")

    def __str__(self):
        return f"user:{self.user_uid} review book:{self.book_uid}"
