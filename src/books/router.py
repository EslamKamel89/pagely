import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.params import Query

from src.auth.deps import RequireRoles, get_auth_service, get_current_user
from src.auth.models import Role, User
from src.auth.service import AuthService
from src.books.book_data import books as dummy_books
from src.books.deps import get_book_service
from src.books.models import Book
from src.books.schemas import BookCreate, BookUpdate, BookWithUser
from src.books.service import BookService
from src.common.schemas import BookBase

router = APIRouter(tags=["books"])


@router.post("/seed")
async def seed(
    delete_books_only: Annotated[bool, Query()] = False,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(RequireRoles([Role.ADMIN])),
) -> dict:
    existing = await service.get_all_books()
    await service.delete_all_books()
    if delete_books_only:
        return {"message": "all data is deleted"}
    for book in dummy_books:
        await service.create_book(book, user_uid=current_user.uid)
    return {
        "message": f"seed completed, {'data base was empty before seeding' if len(existing)==0 else 'database was filled before seeding'}",
    }


@router.get("/", response_model=list[BookWithUser])
async def books_index(
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> Sequence[Book]:
    books = await service.get_all_books()
    return books


@router.post("/", response_model=BookBase)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> Book:
    book = await service.create_book(book_data, current_user.uid)
    return book


@router.get("/user/{uid}", response_model=list[BookBase])
async def get_book_by_user(
    uid: Annotated[uuid.UUID, Path()],
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    user = await service.get_user_with_books(uid)
    return user.books


@router.get("/{uid}", response_model=BookWithUser)
async def get_book(
    uid: Annotated[uuid.UUID, Path()],
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> Book:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return book


@router.patch("/{uid}", response_model=BookBase)
async def update_book(
    uid: Annotated[uuid.UUID, Path()],
    book_data: BookUpdate,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> Book:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    book_updated = await service.update_book(book, book_data)
    return book_updated


@router.delete("/{uid}")
async def delete_book(
    uid: Annotated[uuid.UUID, Path()],
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    book = await service.get_book(uid)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await service.delete_book(book)
    return {"message": "deleted"}
