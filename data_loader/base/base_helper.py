from typing import Literal

from starlette import status

LOG_LEVEL = Literal[
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]

HTTP_EXCEPTION = {
    status.HTTP_400_BAD_REQUEST: "400 Bad Request",
    status.HTTP_401_UNAUTHORIZED: "401 Unauthorized",
    status.HTTP_403_FORBIDDEN: "403 Forbidden",
    status.HTTP_404_NOT_FOUND: "404 Not Found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "405 Method Not Allowed",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "422 Unavailable Entity",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "500 Internal server error",
}
