from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from src.auth.router import router as auth_router
from src.books.router import router as book_router
from src.db.main import dispose_db, init_db
from src.errors import AppError
from src.reviews.router import router as reviews_router

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


@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail or "Something went wrong"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for err in exc.errors():
        field = err["loc"][-1]
        message = err["msg"]
        errors[field] = message
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Failed", "errors": errors},
    )


@app.get("/")
async def read_root():
    return {"message": "Welcome To Pagely App"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(book_router, prefix=f"/api/{version}/books")
app.include_router(auth_router, prefix=f"/api/{version}/auth")
app.include_router(reviews_router, prefix=f"/api/{version}/reviews")
