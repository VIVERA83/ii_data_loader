import logging
import traceback
from logging import Logger

from core.utils import HTTP_EXCEPTION
from httpcore import URL
from icecream import ic
from starlette import status
from starlette.responses import JSONResponse


class ExceptionHandler:
    handlers = {}

    def __init__(
        self,
    ):
        self.exception = Exception("Unknown error...")
        self.logger = Logger(__name__)
        self.level = logging.WARNING
        self.message = "Unknown error..."
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.is_traceback = False

    def __call__(
        self,
        exception: Exception,
        url: URL,
        logger: Logger = None,
        is_traceback: bool = False,
    ) -> JSONResponse:
        self.exception = exception
        self.logger = logger
        self.is_traceback = is_traceback
        self.handler_exception()
        return self.error_response(url)

    def error_response(self, url: URL) -> JSONResponse:
        """Формирует и возвращает JSONResponse объект с ответом.

        Так же выдает лог сообщение об ошибке.
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
        """Обработчик исключений которые произошли в приложении.

        Выводится сообщение в лог, о том что нужно срочно решить проблему.
        """
        if self.exception.args:
            self.message = self.exception.args[0]
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.level = logging.WARNING
        message = self.exception.__class__.__name__
        if ex := getattr(self.exception, "exception", False):
            message += f" real exception={ex.args}"
        self.logger.warning(message)
