import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, text
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.books.models import Book

import src.db.models_base as base
from src.reviews.models import Review


class Role(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    uid: uuid.UUID = base.uid()

    username: str = Field(
        sa_column=Column(
            String(50),
            unique=True,
            index=True,
            nullable=False,
        )
    )
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )
    password_hash: str = Field(
        exclude=True, sa_column=Column(String(255), nullable=False)
    )
    is_verified: bool = Field(
        default=False,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=text("false"),
        ),
    )
    role: Role = Field(
        sa_column=Column(
            SAEnum(Role),
            default=Role.USER,
        ),
    )
    created_at: datetime = base.created_at()
    updated_at: datetime = base.updated_at()
    books: list["Book"] = Relationship(back_populates="user")
    reviewed_books: list["Book"] = Relationship(
        back_populates="reviewed_by", link_model=Review
    )
    reviews: list["Review"] = Relationship(back_populates="user")

    def __str__(self) -> str:
        return f"{self.username} - {self.email}"
