"""All application settings."""
import os

from pydantic import field_validator

from pydantic_settings import BaseSettings

from base.base_helper import LOG_LEVEL

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
    """Uvicorn settings class.

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
    def to_lower_case(cls, log_level: LOG_LEVEL) -> str:  # noqa:
        """Convert the log level to lower case.

        Args:
            log_level (str): The log level.

        Returns:
            str: The converted log level.
        """
        return log_level.lower()


class AppSettings(Base):
    """Application settings class.

    Args:
        title (str): The name of the application.
        description (str): The description of the application.
        version (str): The version of the application.
        docs_url (str): The URL for the application's documentation.
        redoc_url (str): The URL for the application's redoc.
        openapi_url (str): The URL for the application's openapi.json.
    """

    title: str = "Data Loader"
    description: str = "Data download service"
    version: str = "0.0.1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    app_host: str = "localhost"
    app_port: int = 8004

    @property
    def base_url(self) -> str:
        """The base URL for the application.

        Returns:
            str: The base URL for the application.
        """
        return f"http://{self.app_host}:{self.app_port}"  # noqa:


class LogSettings(Base):
    """Setting logging.

    level (str, optional): The level of logging. Defaults to "INFO".
    guru (bool, optional): Whether to enable guru mode. Defaults to True.
    traceback (bool, optional): Whether to include tracebacks in logs. Defaults to True.
    """

    level: LOG_LEVEL = "INFO"
    guru: bool = True
    traceback: bool = True


class FileSettings(Base):
    size: int = 1024 * 1024 * 10


class YaDiskSettings(Base):
    """Yandex Disk settings class.

    Args:
        ya_token (str): Yandex OAuth2 access token.
        ya_client_id (str): Yandex OAuth2 client ID.
        ya_dir (str, optional): Yandex Disk directory ID. Defaults to "temp_folder".
        ya_attempt_count (int, optional): Number of attempts to download a file. Defaults to 10.
    """

    ya_token: str
    ya_client_id: str
    ya_dir: str = "temp_folder"
    ya_attempt_count: int = 10
