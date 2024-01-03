import logging

from fastapi import FastAPI

from core.settings import AppSettings
from store.store import Store


class Application(FastAPI):
    """The main application class.

    This class is responsible for initializing the FastAPI application,
    as well as managing the dependencies and configuration of the application.

    Attributes:
        store (Store): The store instance.
        settings (AppSettings): The application settings.
        logger (logging.Logger): The application logger.
        docs_url (str): The URL of the documentation.
    """

    store: Store
    settings: AppSettings
    logger: logging.Logger
    docs_url: str

    # settings: Settings
    # store: Store
    # redis: RedisAccessor
    # postgres: Postgres
    # logger: logging.Logger
    # docs_url: Url
    # public_access: Public_access
