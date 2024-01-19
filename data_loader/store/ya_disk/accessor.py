from io import BytesIO
from typing import Optional, Callable, AsyncIterator

from base.base_accessor import BaseAccessor
from core.settings import YaDiskSettings
from store.ya_disk.exception import YaTokenNotValidException
from yadisk import AsyncClient
from yadisk.exceptions import PathExistsError, ResourceIsLockedError


class YaDiskAccessor(BaseAccessor):
    settings: YaDiskSettings
    client: AsyncClient

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
        self.client = AsyncClient(
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
        if not await self.client.is_dir(self.settings.ya_dir):
            await self.client.mkdir(self.settings.ya_dir)

    @_check_token  # noqa:
    async def upload_file(
        self, file: BytesIO | bytes, file_name: str
    ) -> Optional[bool]:
        """Uploads a file to Yandex Disk.

        Args:
            file (BytesIO | bytes): The file to be uploaded.
            file_name (str): The name of the file.

        Returns:
            Optional[bool]: Returns True if the file was uploaded successfully, raises an exception otherwise.

        Raises:
            ValueError: If the file could not be uploaded after a certain number of attempts.
        """
        number = 0
        while number < self.settings.ya_attempt_count:
            upload_file = self.make_file_path(
                f"{file_name}", str(number) if number else ""
            )
            try:
                await self.client.upload(file, upload_file)
                return True
            except PathExistsError:
                self.logger.warning(f"File {upload_file} already exists")
            except ResourceIsLockedError:
                self.logger.warning(f"File {upload_file} is locked")
            number += 1
        raise ValueError(f"Please rename upload file")

    def make_file_path(self, upload_file_name: str, number: str = "") -> str:
        """Creates a unique path for the uploaded file on Yandex Disk.

        Args:
            upload_file_name (str): The name of the file to be uploaded.
            number (str, optional): A number to be appended to the file name to make it unique. Defaults to "".

        Returns:
            str: The unique path for the uploaded file on Yandex Disk.
        """
        name, *suf = upload_file_name.split(".")
        name += f"({number})" if number else ""
        name += f".{'.'.join(suf)}" if suf else ""
        return "/".join([self.settings.ya_dir, name])

    async def download_to_cloud(
        self, file_name: str, iter_download: Callable[[], AsyncIterator[bytes]]
    ):
        """Downloads a file to Yandex Disk.

        Parameters:
            file_name (str): The name of the file to download.
            iter_download (Callable[[], AsyncIterator[bytes]]): A function that returns an asynchronous iterator
            of bytes that represents the contents of the file to download.

        Returns:
            Any: The result of the Yandex Disk upload operation.
        """
        number = 0
        while True:
            path = self.make_file_path(file_name, str(number) if number else None)
            try:
                url = await self.client.get_upload_link(path)
                return await self.client.upload_by_link(iter_download, url)
            except PathExistsError:
                pass
            number += 1
