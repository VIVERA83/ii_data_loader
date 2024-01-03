from core.components import Application
from store.sheduler.accessor import SchedulerAccessor


class Store:
    """Store, data service and working with it."""

    scheduler = SchedulerAccessor

    def __init__(self, app: Application):
        """
        Initialize the store.

        Args:
            app (Application): The main application component.
        """
        ...


def setup_store(app: Application):
    """
    Set up the store.

    Args:
        app (Application): The main application component.
    """
    ...
