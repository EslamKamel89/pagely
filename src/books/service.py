import uuid
from typing import Optional, Sequence

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import desc, select

from src.books.models import Book
from src.books.schemas import BookCreate, BookUpdate
from src.db.main import get_session


class BookService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_books(self) -> Sequence[Book]:
        stmt = select(Book).order_by(desc(Book.created_at))
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_book(self, book_uuid: uuid.UUID) -> Optional[Book]:
        stmt = select(Book).where(Book.uid == book_uuid)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_book(self, book_data: BookCreate) -> Book:
        book = Book(**book_data.model_dump())
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def update_book(self, book: Book, book_data: BookUpdate) -> Book:
        update_dict = book_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(book, field, value)
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def delete_book(self, book: Book) -> None:
        await self.session.delete(book)
        await self.session.commit()

    async def delete_all_books(self) -> None:
        await self.session.execute(delete(Book))
        await self.session.commit()


def get_book_service(session: AsyncSession = Depends(get_session)):
    return BookService(session)
