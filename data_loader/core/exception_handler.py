import traceback
from logging import Logger

from base.base_helper import HTTP_EXCEPTION, LOG_LEVEL
from httpcore import URL
from starlette import status
from starlette.responses import JSONResponse


class ExceptionHandler:
    def __init__(self, log_level: LOG_LEVEL = "INFO", is_traceback: bool = False):
        self.exception = Exception("Unknown error...")
        self.level = log_level
        self.logger = Logger(__name__)
        self.message = "Unknown error..."
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.is_traceback = is_traceback

    def __call__(
        self,
        exception: Exception,
        url: URL,
        logger: Logger = None,
        is_traceback: bool = False,
    ) -> JSONResponse:
        """This method is used to handle an exception.

        Args:
            exception (Exception): The exception that was raised.
            url (URL): The URL of the request that caused the exception.
            logger (Logger, optional): The logger to use. Defaults to None.
            is_traceback (bool, optional): Whether or not to include a traceback in the response. Defaults to False.

        Returns:
            JSONResponse: A JSON response containing the error details.
        """
        self.exception = exception
        self.logger = logger
        self.is_traceback = is_traceback
        self.handler_exception()
        return self.error_response(url)

    def error_response(self, url: URL) -> JSONResponse:
        """This method is used to create an error response.

        Args:
            url (URL): The URL of the request that caused the exception.

        Returns:
            JSONResponse: A JSON response containing the error details.
        """
        content_data = {
            "detail": HTTP_EXCEPTION.get(self.status_code),
            "message": self.message,
        }
        if self.is_traceback:
            msg = traceback.format_exc()
        else:
            msg = f"url={url}, exception={self.exception.__class__}, message_to_user={self.exception}"
        match self.level:
            case "CRITICAL" | 50:
                msg = (
                    f" \n_____________\n "
                    f"WARNING: an error has occurred to which there is no correct response of the application."
                    f" WE NEED TO RESPOND URGENTLY"
                    f" \nExceptionHandler:  {str(self.exception)}\n"
                    f" _____________\n" + traceback.format_exc()
                )
                self.logger.critical(msg)
            case "ERROR" | 40:
                self.logger.error(msg)
            case "WARNING" | 30:
                self.logger.warning(msg)
            case _:
                self.logger.info(msg)
        return JSONResponse(content=content_data, status_code=self.status_code)

    def handler_exception(self):
        """This method is used to handle the exception.

        It sets the status code, message, and level based on the exception.
        """
        if self.exception.args:
            self.message = self.exception.args[0]
        self.status_code = status.HTTP_400_BAD_REQUEST
        message = self.exception.__class__.__name__
        if ex := getattr(self.exception, "exception", False):
            message += f" real exception={ex.args}"
