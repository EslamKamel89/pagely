from datetime import datetime

from sqlmodel import Field, SQLModel

from src.db.models_base import DatetimeMixin, IdMixin


class Book(SQLModel, IdMixin, DatetimeMixin, table=True):
    __tablename__ = "books"  # type: ignore
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str

    def __str__(self):
        return f"{self.title} by {self.author}"

    def __repr__(self) -> str:
        return super().__str__()
