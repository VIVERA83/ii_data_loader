from base.base_accessor import BaseAccessor
from core.settings import YaDiskSettings
from yadisk import AsyncClient as YaDiskAsyncClient

from store.ya_disk.exception import YaTokenNotValidException


class YaDiskAccessor(BaseAccessor):
    settings: YaDiskSettings
    client: YaDiskAsyncClient

    def _check_token(func):  # noqa:
        """A decorator that verifies the Yandex disk token before executing the decorated function.

        Args:
            func (function): The function to be decorated.

        Returns:
            function: The decorated function.
        """

        async def inner(self, *args, **kwargs):
            """
            The inner function that is executed by the decorator.

            Args:
                self (YandexDisk): The YandexDisk instance.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                object: The return value of the decorated function.
            """
            if await self.client.check_token(self.settings.ya_token):
                return await func(self, *args, **kwargs)
            raise YaTokenNotValidException()

        return inner

    async def connect(self):
        """Connects to the Yandex Disk API using the provided client ID and access token.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        self.settings = YaDiskSettings()
        self.client = YaDiskAsyncClient(
            self.settings.ya_client_id, token=self.settings.ya_token
        )
        await self.__setup()
        self.logger.info("Yandex disk client connected")

    async def disconnect(self):
        """Disconnects from the Yandex Disk API.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        await self.client.close()
        self.logger.info("Yandex disk client disconnected")

    @_check_token  # noqa:
    async def __setup(self):
        """Sets up the Yandex Disk client by verifying the access token and creating the directory if it does not exist.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        # disk_info = await self.client.get_disk_info()

        if not await self.client.is_dir(self.settings.ya_dir):
            await self.client.mkdir(self.settings.ya_dir)
