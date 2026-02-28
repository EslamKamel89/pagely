from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel, text

from src.config import settings

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)


SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        print("Database connection test:")
        statement = text("SELECT 'it works';")
        result = await conn.execute(statement)
        print(result.all())
        from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)


async def dispose_db():
    return await engine.dispose()
