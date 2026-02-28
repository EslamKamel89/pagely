from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from src.books.router import book_router
from src.db.main import dispose_db, init_db

version = "v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup: performing lightweight app checks and actions")
    await init_db()
    print("startup COMPLETED")
    yield
    print("shutdown: cleaning up")
    await dispose_db()
    print("shutdown COMPLETED")


app = FastAPI(
    title="Pagely",
    description="A REST API for a book review web service",
    version=version,
    lifespan=lifespan,
)


@app.get("/")
async def read_root():
    return {"message": "Welcome To Pagely App"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(book_router, prefix=f"/api/{version}/books")
