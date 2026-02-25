from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from src.books.book_data import books
from src.books.schemas import Book, BookCreate, BookUpdate

book_router = APIRouter(tags=["books"])


@book_router.get("/", response_model=list[Book])
async def books_index() -> list[Book]:
    return books


@book_router.post("/", response_model=Book)
async def create_book(book_data: BookCreate) -> Book:
    id = books[-1].id + 1
    new_book = Book(id=id, **book_data.model_dump())  # type: ignore
    books.append(new_book)
    return new_book


@book_router.get("/{id}", response_model=Book)
async def get_book(id: Annotated[int, Path(gt=0)]) -> Book:
    for b in books:
        if b.id == id:
            return b
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@book_router.patch("/{id}", response_model=Book)
async def update_book(id: Annotated[int, Path(gt=0)], book_data: BookUpdate) -> Book:
    update_data = book_data.model_dump(exclude_unset=True)
    for index, book in enumerate(books):
        if book.id == id:
            updated_book = book.model_copy(update=update_data)
            books[index] = updated_book
            return updated_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@book_router.delete("/{id}")
async def delete_book(id: Annotated[int, Path(gt=0)]) -> dict:
    global books
    books = [book for book in books if book.id != id]
    return {"message": "deleted"}
