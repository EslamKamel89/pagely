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
