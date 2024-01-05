from core.components import Application
from store.ya_disk.accessor import YaDiskAccessor

class Store:
    """Store, data service and working with it."""

    ya_disk: YaDiskAccessor

    def __init__(self, app: Application):
        """
        Initialize the store.

        Args:
            app (Application): The main application component.
        """

def setup_store(app: Application):
    app.store = Store(app)
