import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.auth.models import User
from src.reviews.models import Review
from src.reviews.schemas import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_reviews(self, user: User):
        stmt = (
            select(Review)
            .where(Review.user == user)
            .options(selectinload(Review.user), selectinload(Review.book))  # type: ignore
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

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

    async def get_review(
        self,
        user_uid: uuid.UUID,
        book_uid: uuid.UUID,
    ) -> Optional[Review]:
        stmt = (
            select(Review)
            .where(
                Review.user_uid == user_uid,
                Review.book_uid == book_uid,
            )
            .options(selectinload(Review.user), selectinload(Review.book))  # type: ignore
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_review(
        self,
        review: Review,
        data: ReviewUpdate,
    ) -> Review:
        update_data = data.model_dump(exclude_unset=True)
        allowed_fields = {"review_text", "rating"}
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(review, key, value)
        await self.session.commit()
        await self.session.refresh(
            review,
            attribute_names=["user", "book", "created_at", "updated_at"],
        )
        return review

    async def delete_review(self, review: Review):
        await self.session.delete(review)
        await self.session.commit()
