"""A module describing services for working with data."""

from store.bot.accessor import TgBotAccessor
from store.report_service.accessor import TGReportService
from store.ya_disk.accessor import YaDiskAccessor


class Store:
    """Store, data service and working with it."""

    def __init__(self, app):
        """Initializing data sources.

        Args:
            app: The application
        """
        self.ya_disk = YaDiskAccessor(app)
        self.tg_report = TGReportService(app)
        # self.bot = TgBotAccessor(app)


def setup_store(app):
    """Configuring the connection and disconnection of storage.

    Here we inform the application about the databases of the database and other
    data sources which we run when the application is launched,
    and how to disable them.

    Args:
        app: The application
    """
    app.bot = TgBotAccessor(app)
    app.store = Store(app)
