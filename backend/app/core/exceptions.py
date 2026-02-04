import logging
from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error. Services raise these; the global handler converts them to HTTP responses."""

    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, code: str = "NOT_FOUND", message: str = "Resource not found"):
        super().__init__(code, message, status=404)


class ConflictError(AppError):
    def __init__(self, code: str = "CONFLICT", message: str = "Resource already exists"):
        super().__init__(code, message, status=409)


class ForbiddenError(AppError):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Forbidden"):
        super().__init__(code, message, status=403)


class UnauthorizedError(AppError):
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "Unauthorized"):
        super().__init__(code, message, status=401)


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"code": exc.code, "detail": exc.message})


async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"code": "INTERNAL_ERROR", "detail": "Internal server error"})
