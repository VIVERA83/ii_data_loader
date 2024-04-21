from typing import AsyncIterator, Callable

from base.base_accessor import BaseAccessor
from telethon.events.newmessage import NewMessage
from telethon.tl.types import InputDocumentFileLocation


class TGUpLoadService(BaseAccessor):
    MIME_TYPE = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # noqa
    )
    DOC_INVALID_MSG = "Invalid file format, expected an excel file."
    DOC_SUCCESS_MSG = "Document successfully added to the queue for database insertion."

    async def connect(self):
        # await self.app.bot.update_document_command_handler(
        #     {self.MIME_TYPE: self.__document_loader}
        # )
        self.logger.info(f"{self.__class__.__name__} connected.")

    async def __document_loader(self, event: NewMessage.Event) -> str:
        message = self.DOC_INVALID_MSG
        if event.document.mime_type == self.MIME_TYPE:
            await self.app.store.ya_disk.download_to_cloud(
                event.file.name, self.make_async_iterator(event.document)
            )
            message = self.DOC_SUCCESS_MSG
        self.logger.info(
            f"{message}: filename{event.file.name}, size : {event.file.size / 1024 / 1024:.2} Mb"
        )
        return message

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
            async for chunk in self.app.bot.bot.iter_download(
                document, chunk_size=1024 * 1024 * 1
            ):
                yield chunk

        return iter_download
