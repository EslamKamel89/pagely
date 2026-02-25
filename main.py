from typing import Annotated, Any, Optional, TypedDict

from fastapi import Body, FastAPI, Header, HTTPException, Path, Query, status
from pydantic import BaseModel

app = FastAPI(title="Pagely")


@app.get("/")
async def read_root():
    return {"message": "Welcome To Pagely App"}


@app.get("/health")
async def health():
    return {"status": "ok"}


class Book(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


books: list[Book] = [
    Book(**book)
    for book in [
        {
            "id": 1,
            "title": "Think Python",
            "author": "Allen B. Downey",
            "publisher": "O'Reilly Media",
            "published_date": "2021-01-01",
            "page_count": 1234,
            "language": "English",
        },
        {
            "id": 2,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "published_date": "2008-08-01",
            "page_count": 464,
            "language": "English",
        },
        {
            "id": 3,
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "publisher": "Addison-Wesley",
            "published_date": "1999-10-30",
            "page_count": 352,
            "language": "English",
        },
        {
            "id": 4,
            "title": "Design Patterns",
            "author": "Erich Gamma",
            "publisher": "Addison-Wesley",
            "published_date": "1994-10-21",
            "page_count": 395,
            "language": "English",
        },
        {
            "id": 5,
            "title": "Refactoring",
            "author": "Martin Fowler",
            "publisher": "Addison-Wesley",
            "published_date": "2018-11-19",
            "page_count": 448,
            "language": "English",
        },
        {
            "id": 6,
            "title": "Deep Work",
            "author": "Cal Newport",
            "publisher": "Grand Central Publishing",
            "published_date": "2016-01-05",
            "page_count": 304,
            "language": "English",
        },
        {
            "id": 7,
            "title": "Atomic Habits",
            "author": "James Clear",
            "publisher": "Avery",
            "published_date": "2018-10-16",
            "page_count": 320,
            "language": "English",
        },
        {
            "id": 8,
            "title": "The Lean Startup",
            "author": "Eric Ries",
            "publisher": "Crown Business",
            "published_date": "2011-09-13",
            "page_count": 336,
            "language": "English",
        },
        {
            "id": 9,
            "title": "Zero to One",
            "author": "Peter Thiel",
            "publisher": "Crown Business",
            "published_date": "2014-09-16",
            "page_count": 224,
            "language": "English",
        },
        {
            "id": 10,
            "title": "You Don't Know JS Yet",
            "author": "Kyle Simpson",
            "publisher": "Independently Published",
            "published_date": "2020-01-28",
            "page_count": 143,
            "language": "English",
        },
        {
            "id": 11,
            "title": "Eloquent JavaScript",
            "author": "Marijn Haverbeke",
            "publisher": "No Starch Press",
            "published_date": "2018-12-04",
            "page_count": 472,
            "language": "English",
        },
        {
            "id": 12,
            "title": "Introduction to Algorithms",
            "author": "Thomas H. Cormen",
            "publisher": "MIT Press",
            "published_date": "2009-07-31",
            "page_count": 1312,
            "language": "English",
        },
        {
            "id": 13,
            "title": "Cracking the Coding Interview",
            "author": "Gayle Laakmann McDowell",
            "publisher": "CareerCup",
            "published_date": "2015-07-01",
            "page_count": 687,
            "language": "English",
        },
        {
            "id": 14,
            "title": "The Clean Coder",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "published_date": "2011-05-13",
            "page_count": 256,
            "language": "English",
        },
        {
            "id": 15,
            "title": "Domain-Driven Design",
            "author": "Eric Evans",
            "publisher": "Addison-Wesley",
            "published_date": "2003-08-30",
            "page_count": 560,
            "language": "English",
        },
        {
            "id": 16,
            "title": "Working Effectively with Legacy Code",
            "author": "Michael Feathers",
            "publisher": "Prentice Hall",
            "published_date": "2004-09-30",
            "page_count": 456,
            "language": "English",
        },
        {
            "id": 17,
            "title": "Soft Skills",
            "author": "John Sonmez",
            "publisher": "Manning Publications",
            "published_date": "2014-11-11",
            "page_count": 504,
            "language": "English",
        },
        {
            "id": 18,
            "title": "Code Complete",
            "author": "Steve McConnell",
            "publisher": "Microsoft Press",
            "published_date": "2004-06-09",
            "page_count": 960,
            "language": "English",
        },
        {
            "id": 19,
            "title": "The Mythical Man-Month",
            "author": "Frederick P. Brooks Jr.",
            "publisher": "Addison-Wesley",
            "published_date": "1995-08-12",
            "page_count": 322,
            "language": "English",
        },
        {
            "id": 20,
            "title": "Head First Design Patterns",
            "author": "Eric Freeman",
            "publisher": "O'Reilly Media",
            "published_date": "2004-10-25",
            "page_count": 694,
            "language": "English",
        },
    ]
]


class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    published_date: str | None = None
    page_count: int | None = None
    language: str | None = None


@app.get("/books", response_model=list[Book])
async def books_index() -> list[Book]:
    return books


@app.post("/books", response_model=Book)
async def create_book(book_data: BookCreate) -> Book:
    id = books[-1].id + 1
    new_book = Book(id=id, **book_data.model_dump())  # type: ignore
    books.append(new_book)
    return new_book


@app.get("/books/{id}", response_model=Book)
async def get_book(id: Annotated[int, Path(gt=0)]) -> Book:
    for b in books:
        if b.id == id:
            return b
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.patch("/books/{id}", response_model=Book)
async def put_book(id: Annotated[int, Path(gt=0)], book_data: BookUpdate) -> Book:
    update_data = book_data.model_dump(exclude_unset=True)
    for index, book in enumerate(books):
        if book.id == id:
            updated_book = book.model_copy(update=update_data)
            books[index] = updated_book
            return updated_book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/books/{id}")
async def delete_book(id: Annotated[int, Path(gt=0)]) -> dict:
    global books
    books = [book for book in books if book.id != id]
    return {"message": "deleted"}
