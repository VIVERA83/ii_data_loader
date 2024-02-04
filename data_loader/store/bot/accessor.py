import re
from typing import Callable, AsyncIterator

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import InputDocumentFileLocation

from base.base_accessor import BaseAccessor
from core.settings import TgSettings
from store.report_service.accessor import fetch_report_by_date, clear_database

MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PATTERN = "[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01])"


class TgBotAccessor(BaseAccessor):
    """This class is responsible for managing the Telegram Bot connection and handling various events."""

    DOC_INVALID_MSG = "Invalid file format, expected an excel file."
    DOC_SUCCESS_MSG = "Document successfully added to the queue for database insertion."
    UNKNOWN_COMMAND_MSG = "Unknown command or document."

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
        self.bot.on(NewMessage())(self.event_handler)

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

    async def event_handler(self, event):
        message = self.UNKNOWN_COMMAND_MSG
        file = None
        if event.document:
            message = await self.__document_loader(event)
        elif re.fullmatch(f"hello {PATTERN} {PATTERN}", event.raw_text):
            start_date, end_date = event.raw_text.split()[1:]
            file = await fetch_report_by_date(start_date, end_date, )
            file.name = "hello.xlsx"
            message = "Cats is here 😺"
        elif event.raw_text == "clear":
            message = (await clear_database()).get("message")
        await event.reply(message, file=file)

    async def __document_loader(self, event) -> str:
        message = self.DOC_INVALID_MSG
        if event.document.mime_type == MIME_TYPE:
            await self.app.store.ya_disk.download_to_cloud(
                event.file.name, self.make_async_iterator(event.document)
            )
            message = self.DOC_SUCCESS_MSG
        self.logger.info(
            f"{message}: filename{event.file.name}, size : {event.file.size / 1024 / 1024:.2} Mb"
        )
        return message
