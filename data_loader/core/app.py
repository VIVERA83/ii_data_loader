"""The location of the final assembly of the application."""

from core.components import Application
from core.logger import setup_logging
from core.middelware import setup_middleware
from core.routes import setup_routes
from core.settings import AppSettings
from store.store import setup_store


def setup_app() -> "Application":
    """Creates and configures the main FastAPI application.

    Returns:
        Application: The main FastAPI application.
    """
    settings = AppSettings()
    app = Application(
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        version=settings.version,
        title=settings.title,
        description=settings.description,
    )
    app.settings = settings
    setup_logging(app)
    setup_store(app)
    setup_middleware(app)
    setup_routes(app)
    app.logger.info(f"Swagger link: {app.settings.base_url}{app.docs_url}")
    return app
