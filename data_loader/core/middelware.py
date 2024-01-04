"""Middleware."""
import re

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from icecream import ic
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from core.components import Application
from fastapi import Request as FastApiRequest, Response, status
from fastapi.responses import JSONResponse
from core.exception_handler import ExceptionHandler
from core.settings import LogSettings


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Обработка ошибок при выполнении обработчиков запроса."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_traceback = LogSettings().traceback
        self.exception_handler = ExceptionHandler()

    async def dispatch(
            self, request: FastApiRequest, call_next: RequestResponseEndpoint
    ) -> Response:
        """Обработка ошибок при исполнении handlers (views)."""
        try:
            self.is_endpoint(request)
            response = await call_next(request)
            return response
        except Exception as error:
            return self.exception_handler(
                error,
                request.url,
                request.app.logger,
                is_traceback=self.is_traceback,
            )

    @staticmethod
    def is_endpoint(request: FastApiRequest) -> bool:
        """Checking if there is a requested endpoint.

        Args:
            request: Request object

        Returns:
            object: True if there is a endpoint
        """
        detail = "{message}, See the documentation: http://{host}:{port}{uri}" # noqa
        message = "Not Found"
        status_code = status.HTTP_404_NOT_FOUND
        for route in request.app.routes:
            if re.match(route.path_regex, request.url.path):
                if request.method.upper() in route.methods:
                    return True
                status_code = status.HTTP_405_METHOD_NOT_ALLOWED
                message = "Method Not Allowed"
                break
        raise HTTPException(
            status_code,
            detail.format(
                message=message,
                host=request.app.settings.app_server_host,
                port=request.app.settings.app_port,
                uri=request.app.docs_url,
            ),
        )


async def validation_exception_handler(
        _: FastApiRequest, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle RequestValidationError exceptions.

    Args:
        _ (Request): The incoming request.
        exc (RequestValidationError): The exception that was raised.

    Returns:
        JSONResponse: A JSON response with an error message.
    """

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Bad request", "message": exc.errors()[0].get("msg")}
        ),
    )


def setup_middleware(app: Application):
    """Setup Middleware."""
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.add_middleware(ErrorHandlingMiddleware)
