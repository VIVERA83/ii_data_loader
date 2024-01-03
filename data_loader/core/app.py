"""Место окончательной сборки приложения."""
from core.components import Application
from core.logger import setup_logging
from core.middelware import setup_middleware
from core.routes import setup_routes
from core.settings import AppSettings


# from core.logger import setup_logging
# from core.middelware import setup_middleware
# from core.routes import setup_routes
# from core.settings import Settings
# from store.store import setup_store


def setup_app() -> "Application":
    """The place where the application is built, database connections, routes, etc."""
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
    # setup_store(application)
    setup_middleware(app)
    setup_routes(app)
    app.logger.info(
        f"Swagger link: {app.settings.base_url}{app.docs_url}"
    )
    return app


# application = setup_app()
