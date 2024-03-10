from io import BytesIO
from re import Pattern
from typing import AsyncIterator, Awaitable, Callable, Coroutine, Optional, Any

from aiohttp import ClientConnectorError

from base.base_accessor import BaseAccessor
from core.settings import TgSettings

from telethon import TelegramClient, functions
from telethon.events import NewMessage
from telethon.tl.types import (
    BotCommand,
    BotCommandScopeDefault,
    InputDocumentFileLocation,
)

MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PATTERN = "[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01])"


class TgBotAccessor(BaseAccessor):
    """This class is responsible for managing the Telegram Bot connection and handling various events."""

    DOC_INVALID_MSG = "Invalid file format, expected an excel file."
    DOC_SUCCESS_MSG = "Document successfully added to the queue for database insertion."
    UNKNOWN_COMMAND_MSG = "Unknown command or document."
    ERROR_MSG = "Something went wrong. Please try again later."
    ACCESS_DENIED_MSG = "Access Denied. Please contact the administrator."

    settings: TgSettings
    _client: TelegramClient
    bot: TelegramClient
    __commands: list[tuple[str, str, Callable[[], Coroutine]]]
    __command_handlers: dict[str, Callable[[], Coroutine[None, None, None]]]
    __commands_regex_handler: dict[
        Pattern, Callable[[Any], Coroutine[None, None, None]]
    ]
    lang_codes = ["ru", "en"]

    async def connect(self):
        self.__commands = []
        self.__command_handlers = {}
        self.__commands_regex_handler = {}
        self.settings = TgSettings()
        self._client = TelegramClient(
            "bot", api_hash=self.settings.tg_api_hash, api_id=self.settings.tg_api_id
        )
        self.bot = await self._client.start(  # noqa
            bot_token=self.settings.tg_bot_token
        )
        self.bot.on(NewMessage())(self.event_handler)
        await self.add_commands(self.create_start_command())
        self.logger.info("Telegram Bot connected")

    async def disconnect(self):
        """Disconnects from the Yandex Disk API.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        self.logger.info("Telegram bot disconnected")

    async def event_handler(self, event):
        message = self.UNKNOWN_COMMAND_MSG
        file = None
        if event.document:
            message = await self.__document_loader(event)

        elif handler := self.get_handler(event.raw_text):
            try:
                data = await handler()
                if isinstance(data, BytesIO):
                    file = data
                    message = self.DOC_SUCCESS_MSG
                else:
                    message = data
            except ClientConnectorError:
                message = self.ERROR_MSG

        elif self.__commands_regex_handler:
            for pattern, handler in self.__commands_regex_handler.items():
                if pattern.fullmatch(event.raw_text):
                    try:
                        await handler(*event.raw_text.split()[1:])
                    except ClientConnectorError:
                        message = self.ERROR_MSG

        await event.reply(message, file=file)

    def get_handler(self, command: str) -> Optional[Callable[[], Awaitable]] | None:
        return self.__command_handlers.get(command)

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

    async def add_commands(
        self, commands: list[tuple[str, str, Callable[[], Coroutine]]]
    ):
        self.__commands.extend(commands)
        await self.__update_commands()
        self.__update_command_handlers()

    async def remove_commands(
        self, commands: list[tuple[str, str, Callable[[], Coroutine]]]
    ):
        for command in commands:
            if command in self.__commands:
                try:
                    self.__commands.remove(command)
                except ValueError:
                    self.logger.warning(f"Command {command[0]} not found")
                self.__command_handlers.pop(f"/{command[0]}")
        await self.__update_commands()

    async def __update_commands(self):
        [
            await self._client(
                functions.bots.SetBotCommandsRequest(
                    scope=BotCommandScopeDefault(),
                    lang_code=lang_code,
                    commands=[
                        BotCommand(command=command, description=description)
                        for command, description, _ in self.__commands
                    ],
                )
            )
            for lang_code in self.lang_codes
        ]

    def __update_command_handlers(self):
        self.__command_handlers = {
            f"/{command}": handler for command, _, handler in self.__commands
        }

    def update_regex_command_handler(
        self, command: dict[Pattern, Callable[[Any], Coroutine]]
    ):
        self.__commands_regex_handler.update(command)

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

    def create_start_command(self) -> list[tuple[str, str, Callable[[], Coroutine]]]:
        return [
            ("start", "знакомство с ботом", self.start),  # noqa
        ]

    @staticmethod
    async def start():
        return """Привет, я бот для выгрузки отчётов за любой отчетный переуд."""
