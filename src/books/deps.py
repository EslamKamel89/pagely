from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.service import BookService
from src.db.main import get_session


def get_book_service(session: AsyncSession = Depends(get_session)):
    return BookService(session)
