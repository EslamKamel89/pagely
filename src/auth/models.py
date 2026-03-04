import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, text
from sqlmodel import Column, Field, SQLModel

from src.db.models_base import created_at, uid, updated_at


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    uid: uuid.UUID = uid()

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
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    is_verified: bool = Field(
        default=False,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default=text("false"),
        ),
    )
    created_at: datetime = created_at()
    updated_at: datetime = updated_at()

    def __str__(self) -> str:
        return f"{self.username} - {self.email}"
