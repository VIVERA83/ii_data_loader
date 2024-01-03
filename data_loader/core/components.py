"""Переназначенные компоненты Fast-Api."""

from fastapi import FastAPI


class Application(FastAPI):
    """Application главный класс.

    Описываем сервисы, которые будут использоваться в приложении.
    Так же это нужно для корректной подсказки IDE.
    """

    # settings: Settings
    # store: Store
    # redis: RedisAccessor
    # postgres: Postgres
    # logger: logging.Logger
    # docs_url: Url
    # public_access: Public_access
