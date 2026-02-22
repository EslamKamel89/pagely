from typing import Annotated, Any, Optional
from fastapi import status
from fastapi import Body, FastAPI, Header, Path, Query
from pydantic import BaseModel

app = FastAPI(title="Pagely")


@app.get("/")
async def read_root():
    return {"message": "Welcome To Pagely App"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/greet/{name}")
async def greet(
    name: Annotated[
        str, Path(description="Enter Your name", min_length=2, max_length=100)
    ],
    age: Annotated[
        Optional[int], Query(gt=6, lt=100, description="Enter Your Age")
    ] = None,
):
    return {"message": f"Welcome {name}", "age": age or "Not specified"}


class BookCreateModel(BaseModel):
    title: str
    author: Optional[str] = None


@app.post("/books/create", status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: Annotated[
        BookCreateModel,
        Body(
            examples=[
                {"title": "Python for dummies", "author": "Eslam Kamel"},
                {"title": "FastAPI from zero to hero"},
            ]
        ),
    ],
    secret: str = Header(description="Enter 123456", example=123456),
):
    if secret != "123456":
        return {"message": "not authorized"}
    return {"title": book_data.title, "author": book_data.author or "Not specified"}


@app.post("/get_headers")
async def get_headers(accept: str = Header(None)):
    headers = {}
    headers["Accept"] = accept
    return headers
