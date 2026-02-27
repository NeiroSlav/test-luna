from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = getLogger(__name__)


async def handle_unexpected_error(_: Request, exc: Exception):
    """Обработка неожиданных исключений."""

    error_hash = hash(str(exc))
    logger.exception(f"Unexpected exception (id:{error_hash}):\n")
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error, id:'{error_hash}'"},
    )


def setup_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, handle_unexpected_error)
