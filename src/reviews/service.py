import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.reviews.models import Review
from src.reviews.schemas import ReviewCreate


class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_review_to_book(
        self,
        user_uid: uuid.UUID,
        book_uid: uuid.UUID,
        data: ReviewCreate,
    ) -> Review:
        review = Review(
            user_uid=user_uid,
            book_uid=book_uid,
            review_text=data.review_text,
            rating=data.rating,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(
            review,
            attribute_names=["user", "book", "created_at", "updated_at"],
        )
        return review

    async def check_user_reviewed_book(
        self,
        user_uid: uuid.UUID,
        book_uid: uuid.UUID,
    ) -> bool:
        stmt = (
            select(Review)
            .where(
                Review.user_uid == user_uid,
                Review.book_uid == book_uid,
            )
            .exists()
        )
        stmt = select(stmt)
        res = await self.session.execute(stmt)
        return res.scalar() or False
