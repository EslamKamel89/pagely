from fastapi import FastAPI

from src.books.router import book_router

version = "v1"
app = FastAPI(title="Pagely", version=version)


@app.get("/")
async def read_root():
    return {"message": "Welcome To Pagely App"}


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(book_router, prefix=f"/api/{version}/books")
