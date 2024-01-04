import re

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from core.components import Application
from fastapi import Request as FastApiRequest, Response, status
from fastapi.responses import JSONResponse
from core.exception_handler import ExceptionHandler
from core.settings import LogSettings


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware to handle exceptions and errors in the application.

    Args:
        app (ASGIApp): The ASGI application.

    Attributes:
        is_traceback (bool): Whether to include stack tracing in the application log.
        exception_handler (ExceptionHandler): The exception handler.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_traceback = LogSettings().traceback
        self.exception_handler = ExceptionHandler()

    async def dispatch(
        self, request: FastApiRequest, call_next: RequestResponseEndpoint
    ) -> Response:
        """Dispatch the request to the next middleware or the application.

        Args:
            request (FastApiRequest): The incoming request.
            call_next (RequestResponseEndpoint): The next middleware or the
                application.

        Raises:
            Exception: Any exception raised by the next middleware or the
                application.

        Returns:
            Response: The response from the next middleware or the application.
        """
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
        """Check if the request is an endpoint.

        Args:
            request (FastApiRequest): The incoming request.

        Raises:
            HTTPException: If the request is not an endpoint.

        Returns:
            bool: Whether the request is an endpoint.
        """
        detail = "{message}, See the documentation: http://{host}:{port}{uri}"  # noqa
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
    """Custom exception handler for FastAPI RequestValidationError.

    Args:
        _ (FastApiRequest): The incoming request.
        exc (RequestValidationError): The raised exception.

    Returns:
        JSONResponse: A JSON response with the error details.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Bad request", "message": exc.errors()[0].get("msg")}
        ),
    )


def setup_middleware(app: Application):
    """Sets up the middleware for the FastAPI application.

    Args:
        app (Application): The FastAPI application.

    Raises:
        Exception: If the middleware cannot be set up.
    """
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.add_middleware(ErrorHandlingMiddleware)
