from io import BytesIO
from re import Pattern
from typing import Any, Awaitable, Callable, Coroutine, Optional

from aiohttp import ClientConnectorError
from base.base_accessor import BaseAccessor
from core.settings import TgSettings
from telethon import TelegramClient, functions
from telethon.events import NewMessage
from telethon.tl.types import BotCommand, BotCommandScopeDefault


class TgBotAccessor(BaseAccessor):
    """This class is responsible for managing the Telegram Bot connection and handling various events."""

    UNKNOWN_COMMAND_MSG = "Unknown command or document."
    SUCCESS_MSG = "Command executed successfully."
    ERROR_MSG = "Something went wrong. Please try again later."

    settings: TgSettings
    bot: TelegramClient
    lang_codes = ["ru", "en"]
    _client: TelegramClient
    __commands: list[tuple[str, str, Callable[[], Coroutine]]]
    __document_handlers: dict[str, Callable[[], Coroutine[None, None, None]]]
    __command_handlers: dict[str, Callable[[], Coroutine[None, None, None]]]
    __commands_regex_handler: dict[
        Pattern, Callable[[Any], Coroutine[None, None, None]]
    ]

    async def connect(self):
        self.__commands = []
        self.__document_handlers = {}
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
        self.logger.info(f"{self.__class__.__name__} connected.")

    async def event_handler(self, event: NewMessage.Event):
        message = self.UNKNOWN_COMMAND_MSG
        file = None
        if event.document:
            handler = self.get_document_handler(event.document.mime_type)
        else:
            handler = self.get_handler(event.raw_text)
            if handler is None:
                for pattern, _handler in self.__commands_regex_handler.items():
                    if pattern.fullmatch(event.raw_text):
                        handler = _handler
                        break
        self.logger.warning(f"handler: {handler} {event.raw_text.split()[1:]}")
        if handler:
            try:
                result = await handler(*event.raw_text.split()[1:])  # noqa
                if isinstance(result, BytesIO):
                    file = result
                    message = self.SUCCESS_MSG
                else:
                    message = result
            except ClientConnectorError:
                message = self.ERROR_MSG

        await event.reply(message, file=file)

    def get_handler(self, command: str) -> Optional[Callable[[], Awaitable]] | None:
        return self.__command_handlers.get(command)

    def get_document_handler(self, command: str) -> Callable[[], Awaitable]:
        return self.__document_handlers.get(command)

    async def add_commands(
        self, commands: list[tuple[str, str, Callable[[], Coroutine]]]
    ):
        self.__commands.extend(commands)
        await self.__update_commands()
        self.__update_command_handlers()

    async def update_document_command_handler(
        self, commands: dict[str, Callable[[], Coroutine]]
    ):
        self.__document_handlers.update(commands)

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

    def update_regex_command_handler(
        self, command: dict[Pattern, Callable[[Any], Coroutine]]
    ):
        self.__commands_regex_handler.update(command)

    def get_regex_command_handler(self) -> dict[Pattern, Callable[[Any], Coroutine]]:
        return self.__commands_regex_handler

    def create_start_command(self) -> list[tuple[str, str, Callable[[], Coroutine]]]:
        return [
            ("start", "знакомство с ботом", self.start),  # noqa
        ]

    @staticmethod
    async def start(*_, **__):
        return """Привет, я бот для выгрузки отчётов за отчетный период."""

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
