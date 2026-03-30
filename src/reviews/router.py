import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.auth.deps import get_current_user
from src.auth.models import User
from src.books.deps import get_book_service
from src.books.service import BookService
from src.reviews.deps import get_review_service
from src.reviews.schemas import Message, ReviewBase, ReviewCreate, ReviewUpdate
from src.reviews.service import ReviewService

router = APIRouter(tags=["reviews"])


@router.get("/", response_model=list[ReviewBase], status_code=status.HTTP_200_OK)
async def get_all_reviews(
    review_service: ReviewService = Depends(get_review_service),
    user: User = Depends(get_current_user),
):
    return await review_service.get_all_reviews(user)


@router.post(
    "/{uid}/book", response_model=ReviewBase, status_code=status.HTTP_201_CREATED
)
async def add_review_to_book(
    uid: Annotated[uuid.UUID, Path()],
    body: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
    book_service: BookService = Depends(get_book_service),
    user: User = Depends(get_current_user),
):
    book = await book_service.get_book(uid)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No book found with this uuid",
        )
    if book.user_uid == user.uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can't review your own book",
        )
    if await review_service.check_user_reviewed_book(user.uid, book.uid):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this book",
        )
    review = await review_service.add_review_to_book(user.uid, book.uid, body)
    return review


@router.patch("/{uid}/book", response_model=ReviewBase, status_code=status.HTTP_200_OK)
async def update_review(
    uid: Annotated[uuid.UUID, Path()],
    body: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
    book_service: BookService = Depends(get_book_service),
    user: User = Depends(get_current_user),
):
    book = await book_service.get_book(uid)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No book found with this uuid",
        )
    review = await review_service.get_review(user.uid, book.uid)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No review found by you for {book.title}",
        )
    review = await review_service.update_review(review, body)
    return review


@router.delete("/{uid}/book", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_review(
    uid: Annotated[uuid.UUID, Path()],
    review_service: ReviewService = Depends(get_review_service),
    book_service: BookService = Depends(get_book_service),
    user: User = Depends(get_current_user),
):
    book = await book_service.get_book(uid)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No book found with this uuid",
        )
    review = await review_service.get_review(user.uid, book.uid)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No review found by you for {book.title}",
        )
    await review_service.delete_review(review)
    return Message(message="Review deleted")
