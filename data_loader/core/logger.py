import logging
import sys

from core.settings import LogSettings
from loguru import logger


def setup_logging(app) -> None:
    """Setting up logging in the application.

    In this case, there is an option to use logo ru.
    https://github.com/Delgan/loguru
    """
    settings = LogSettings()
    if settings.guru:
        logger.configure(
            **{
                "handlers": [
                    {
                        "sink": sys.stderr,
                        "level": settings.level,
                        "backtrace": settings.traceback,
                    },
                ],
            }
        )
        app.logger = logger
    else:
        logging.basicConfig(level=settings.log_level)
        app.logger = logging
    app.logger.info("Starting logging")
