"""Модуль начальных настроек приложения."""
import os

from pydantic import field_validator

# from base.type_hint import ALGORITHM, HEADERS, METHOD
# from core.utils import ALGORITHMS
# from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings
from logging import getLogger

from data_loader.base.type_hint import LOG_LEVEL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__name__)))


class Base(BaseSettings):
    class Config:
        """Settings for reading environment variables from a file.

        env_file - The path to the environment, to run locally
        """

        env_nested_delimiter = "__"
        env_file = os.path.join(BASE_DIR, ".env")
        enf_file_encoding = "utf-8"
        extra = "ignore"


class UvicornSettings(Base):
    """
    Uvicorn settings class.

    Args:
        host (str): Hostname.
        port (int): Port number.
        workers (int): Number of worker processes.
        log_level (str): Log level.
        reload (bool): Reload on code changes.
    """

    host: str
    port: int
    workers: int
    log_level: LOG_LEVEL = "INFO"
    reload: bool

    @field_validator("log_level")
    def to_lower_case(cls, log_level: LOG_LEVEL) -> str:
        """Convert the log level to lower case.

        Args:
            log_level (str): The log level.

        Returns:
            str: The converted log level.
        """
        return log_level.lower()


class FileSettings(Base):
    size: int = 1024 * 1024 * 10
