from typing import Callable, AsyncIterator

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import InputDocumentFileLocation

from base.base_accessor import BaseAccessor
from core.settings import TgSettings

MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class TgBotAccessor(BaseAccessor):
    settings: TgSettings
    _client: TelegramClient
    bot: TelegramClient

    async def connect(self):
        self.settings = TgSettings()
        self._client = TelegramClient(
            "bot", api_hash=self.settings.tg_api_hash, api_id=self.settings.tg_api_id
        )
        self.bot = await self._client.start(  # noqa
            bot_token=self.settings.tg_bot_token
        )
        await self.setup_handler()
        self.logger.info("Telegram Bot connected")

    async def disconnect(self):
        """Disconnects from the Yandex Disk API.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        self.logger.info("Telegram bot disconnected")

    async def setup_handler(self):
        self.bot.on(NewMessage())(self.document_loader)

    def make_async_iterator(
        self, document: InputDocumentFileLocation
    ) -> Callable[[], AsyncIterator[bytes]]:
        """Creates an asynchronous iterator that can be used to download a file from Telegram's cloud storage.

        Parameters:
            document (telethon.tl.types.InputDocumentFileLocation): A Telethon object that
            represents the location of the file to download.

        Returns:
            Callable[[], AsyncIterator[bytes]]: A function that returns an asynchronous
            iterator of bytes that can be used to download the file.
        """

        async def iter_download():
            async for chunk in self.bot.iter_download(
                document, chunk_size=1024 * 1024 * 1
            ):
                yield chunk

        return iter_download

    async def document_loader(self, event):
        if document := event.document:
            """
            Checks if the incoming event contains a document
            :param event: the incoming event
            :type event: NewMessage
            :return: True if the event contains a document, False otherwise
            :rtype: bool
            """
            message = "Invalid file format, expected an excel file."
            if document.mime_type == MIME_TYPE:
                """
                Downloads the document to the cloud and saves it to the specified file name
                :param file_name: the name of the file to save the document as
                :type file_name: str
                :param document: the incoming document
                :type document: Document
                :return: None
                """
                await self.app.store.ya_disk.download_to_cloud(
                    event.file.name, self.make_async_iterator(document)
                )
                message = (
                    "Document successfully added to the queue for database insertion."
                )
            await event.reply(message)
            self.logger.info(
                f"{message}: filename{event.file.name}, size : {event.file.size / 1024 / 1024:.2} Mb"
            )
