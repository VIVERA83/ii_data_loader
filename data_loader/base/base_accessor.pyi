from logging import Logger
from typing import Optional

from core.components import Application

class BaseAccessor:
    """
    Base class for all accessors.

    An accessor is a class that provides an interface to a specific system or resource, such as a database or a file system.
    It is responsible for connecting to the system, managing the connection, and providing methods for interacting with it.

    Accessors are designed to be used by multiple components within the application, and should be treated as a black box by other components.
    They should not be instantiated directly by components, but rather through the application's dependency injection container.

    Attributes:
        logger (logging.Logger): The logger for the accessor.
        app (core.components.Application): The application instance.

    """

    logger: Optional[Logger]
    app: Optional[Application]

    def __init__(self, app: Application):
        """
        Initialize the accessor.

        Args:
            app (core.components.Application): The application instance.

        """
        self.app = app
        self.logger = app.logger.getChild(self.__class__.__name__)

    def _init(self):
        """
        Perform any additional initialization actions.

        This method is called after the accessor is instantiated, but before the connection is established.
        It provides an opportunity for the accessor to perform any initialization tasks that are specific to its implementation.

        """
        pass

    async def connect(self):
        """
        Establish a connection to the system.

        This method is responsible for connecting to the system and configuring it for use.
        It should be implemented as an asynchronous function, to allow for potential asynchronous operations.

        """
        pass

    async def disconnect(self):
        """
        Close the connection to the system.

        This method is responsible for closing the connection to the system, and cleaning up any resources that were allocated.
        It should be implemented as an asynchronous function, to allow for potential asynchronous operations.

        """
        pass
