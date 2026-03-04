import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from src.db.models_base import created_at, uid, updated_at


class Book(SQLModel, table=True):
    __tablename__ = "books"  # type: ignore
    uid: uuid.UUID = uid()
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str
    created_at: datetime = created_at()
    updated_at: datetime = updated_at()

    def __str__(self):
        return f"{self.title} by {self.author}"
