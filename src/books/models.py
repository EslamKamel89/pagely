import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.auth.models import User

import src.db.models_base as base
from src.reviews.models import Review


class Book(SQLModel, table=True):
    __tablename__ = "books"  # type: ignore
    uid: uuid.UUID = base.uid()
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str
    created_at: datetime = base.created_at()
    updated_at: datetime = base.updated_at()
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    user: "User" = Relationship(back_populates="books")
    reviewed_by: list["User"] = Relationship(
        back_populates="reviewed_books", link_model=Review
    )
    reviews: list["Review"] = Relationship(back_populates="book")

    def __str__(self):
        return f"{self.title} by {self.author}"
