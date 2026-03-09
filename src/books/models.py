import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

import src.db.models_base as base


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

    def __str__(self):
        return f"{self.title} by {self.author}"
