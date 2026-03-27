import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.auth.deps import get_current_user
from src.auth.models import User
from src.books.deps import get_book_service
from src.books.service import BookService
from src.reviews.deps import get_review_service
from src.reviews.schemas import ReviewBase, ReviewCreate
from src.reviews.service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/{uid}/book", response_model=ReviewBase)
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
