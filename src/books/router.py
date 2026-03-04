import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.books.book_data import books as dummy_books
from src.books.models import Book
from src.books.schemas import BookBase, BookCreate, BookUpdate
from src.books.service import BookService, get_book_service

book_router = APIRouter(tags=["books"])


@book_router.post("/seed")
async def seed_books(service: BookService = Depends(get_book_service)) -> dict:
    existing = await service.get_all_books()
    await service.delete_all_books()
    for book in dummy_books:
        await service.create_book(book)
    return {
        "message": f"seed completed, {'data base was empty before seeding' if len(existing)==0 else 'database was filled before seeding'}",
    }


@book_router.get("/", response_model=list[BookBase])
async def books_index(
    service: BookService = Depends(get_book_service),
) -> Sequence[Book]:
    books = await service.get_all_books()
    return books


@book_router.post("/", response_model=BookBase)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_book_service),
) -> Book:
    book = await service.create_book(book_data)
    return book


@book_router.get("/{uid}", response_model=BookBase)
async def get_book(
    uid: Annotated[uuid.UUID, Path()],
    service: BookService = Depends(get_book_service),
) -> Book:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return book


@book_router.patch("/{uid}", response_model=BookBase)
async def update_book(
    uid: Annotated[uuid.UUID, Path()],
    book_data: BookUpdate,
    service: BookService = Depends(get_book_service),
) -> Book:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    book_updated = await service.update_book(book, book_data)
    return book


@book_router.delete("/{uid}")
async def delete_book(
    uid: Annotated[uuid.UUID, Path()],
    service: BookService = Depends(get_book_service),
) -> dict:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await service.delete_book(book)
    return {"message": "deleted"}
