from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.main import get_session
from src.reviews.service import ReviewService


def get_review_service(session: AsyncSession = Depends(get_session)):
    return ReviewService(session)
