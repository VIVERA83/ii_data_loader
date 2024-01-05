import asyncio
import os

import aiofiles
import yadisk
from core.settings import BASE_DIR
from icecream import ic
from yadisk.exceptions import PathExistsError

ya_token = "y0_AgAAAAABo1wMAAsTvgAAAAD3AGxAgdTeBafNQVmF-8JM3lycdXRhpE8"
ya_client_id = "af20c4eb971f409eab78fd72cc6274b6"
ya_dir = "temp_folder"
client = yadisk.AsyncClient(ya_client_id, token=ya_token)
ya_attempt_count = 10


def make_upload_file_path(upload_file_name: str, number: str = "") -> str:
    """
    Creates a unique path for the uploaded file on Yandex Disk.

    Args:
        upload_file_name (str): The name of the file to be uploaded.
        number (str, optional): A number to be appended to the file name to make it unique. Defaults to "".

    Returns:
        str: The unique path for the uploaded file on Yandex Disk.
    """
    name, *suf = os.path.split(upload_file_name)[-1].split(".")
    name += f"({number})" if number else ""
    name += f".{'.'.join(suf)}" if suf else ""
    return "/".join([ya_dir, name])


class YandexDisk:
    def check_token(self):
        async def inner(cls: "YandexDisk", *args, **kwargs):
            assert await cls.client.check_token(
                ya_token
            ), "The Yandex disk token failed verification, update token."
            return await self(cls, *args, **kwargs)

        return inner

    def __init__(self):
        self.ya_token = ya_token
        self.client = yadisk.AsyncClient(self.ya_token, token=ya_token)

    @check_token
    async def main(self, filename: str = os.path.join(BASE_DIR, "pl.xlsx")):
        async with aiofiles.open(filename, "rb") as f:
            number = 0
            while True:
                upload_file = make_upload_file_path(
                    f"{f.name}", str(number) if number else ""
                )
                try:
                    await self.client.upload(f, upload_file)
                    break
                except PathExistsError as e:
                    number += 1
                    ic(f"File {upload_file} already exists", e)
            if number > ya_attempt_count:
                ValueError(f"Please rename upload file")
        return "OK"


async def main():
    disk = YandexDisk()
    ic(await disk.main())


if __name__ == "__main__":
    asyncio.run(main())
