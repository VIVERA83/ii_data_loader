class BaseAccessor:
    """The base class responsible for linking logic to the base application."""

    def __init__(self, app):
        """Initialization of the connected service in the main Fast-Api application.

        Args:
            app (FastAPI): The application
        """
        self.app = app
        self.logger = app.logger
        app.on_event("startup")(self.connect)
        app.on_event("shutdown")(self.disconnect)
        self._init()

    def _init(self):
        """Description of additional actions for initialization."""

    async def connect(self):
        """The logic responsible for connecting and configuring.

        Sets up the connection to the third-party API as an example.
        """

    async def disconnect(self):
        """The logic responsible for disconnecting and cleaning up.

        Ensures that all connections are closed correctly.
        """
