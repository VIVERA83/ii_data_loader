"""Middleware."""
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from icecream import ic

from core.components import Application
from fastapi import Request, status
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle RequestValidationError exceptions.

    Args:
        _ (Request): The incoming request.
        exc (RequestValidationError): The exception that was raised.

    Returns:
        JSONResponse: A JSON response with an error message.
    """
    ic(exc.args)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Bad request", "message": exc.errors()[0].get("msg")}
        ),
    )


def setup_middleware(app: Application):
    """Setup Middleware."""
    app.exception_handler(RequestValidationError)(validation_exception_handler)
