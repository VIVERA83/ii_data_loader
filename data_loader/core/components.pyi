import logging
from typing import Optional

from fastapi import FastAPI

# from base.type_hint import Public_access
# from core.settings import Settings
# from core.utils import Token
# from fastapi import Request as FastAPIRequest
# from store.database.postgres import Postgres
# from store.database.redis import RedisAccessor
# from store.store import Store

class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """

    store: Store
    settings: Settings
    logger: logging.Logger
    docs_url: str

class Request(FastAPIRequest):
    """Переопределения Request.

    Для корректной подсказки IDE по методам `Application`."""

    app: Optional["Application"] = None
