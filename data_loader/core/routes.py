from core.components import Application
from downloader.views import downloader_file_route


def setup_routes(app: Application):
    """Configuring the connected routes to the application."""
    app.include_router(downloader_file_route)
