from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """
    This is the base exception for all exceptions in this app.
    """

    def __init__(self, status_code: int = 500, detail: str | None = None):
        self.status_code = status_code
        self.detail = detail


class InvalidTokenError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ServerError(AppError):
    pass


def register_exception_handler(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail or "Something went wrong"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = {}
        for err in exc.errors():
            field = err["loc"][-1]
            message = err["msg"]
            errors[field] = message
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation Failed", "errors": errors},
        )
