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


def check_token(func):
    async def inner(*args, **kwargs):
        assert await client.check_token(
            ya_token
        ), "The Yandex disk token failed verification, update token."
        return await func(*args, **kwargs)

    return inner


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


@check_token
async def main(filename: str = os.path.join(BASE_DIR, "pl.xlsx")):
    async with aiofiles.open(filename, "rb") as f:
        number = 0
        while True:
            upload_file = make_upload_file_path(
                f"{f.name}", str(number) if number else ""
            )
            try:
                await client.upload(f, upload_file)
                break
            except PathExistsError as e:
                number += 1
                ic(f"File {upload_file} already exists", e)
        if number > ya_attempt_count:
            ValueError(f"Please rename upload file")


if __name__ == "__main__":
    asyncio.run(main())

# https://oauth.yandex.ru/verification_code#
# access_token=y0_AgAAAAABo1wMAAsTvgAAAAD3AGxAgdTeBafNQVmF-8JM3lycdXRhpE8
# &token_type=bearer&
# expires_in=31536000 # 365

# def make_upload_file_path(upload_file_name: str, suffix: bool = True) -> str:
#     """
#     Creates a unique path for the uploaded file on Yandex Disk.
#
#     Args:
#         upload_file_name (str): The name of the file to be uploaded.
#         suffix (bool, optional): Whether to add a timestamp to the file name to make it unique. Defaults to True.
#
#     Returns:
#         str: The unique path for the uploaded file on Yandex Disk.
#     """
#     name, *suf = os.path.split(upload_file_name)[-1].split(".")
#     ic(name)
#     name += str(datetime.now().timestamp())[-5::] if suffix else ""
#     ic(name)
#     name = ".".join([name, *suf]) if suf else name
#     return ic("/".join([ya_dir, name]))

# def test_make_upload_file_path():
#     assert make_upload_file_path("test.txt") == "/temp_folder/test.txt"
#     assert make_upload_file_path("test.txt", "1") == "/temp_folder/test(1).txt"
#     assert make_upload_file_path("/test/test.txt") == "/temp_folder/test/test.txt"
#     assert make_upload_file_path("/test/test.txt", "1") == "/temp_folder/test/test(1).txt"
#     assert make_upload_file_path("test.txt", "a") == "/temp_folder/test(a).txt"
#     assert make_upload_file_path("test.txt.bak") == "/temp_folder/test.txt.bak"
#     assert make_upload_file_path("test.txt.bak", "1") == "/temp_folder/test(1).txt.bak"
#     assert make_upload_file_path("test.1.txt.bak", "a") == "/temp_folder/test.1(a).txt.bak"

# ic(await client.is_file("temp_folder"))
# ic(await client.is_dir("temp_folder"))
# ic(await client.mkdir("temp_folder"))
# ic(await client.mkdir("temp_folder"))  # DiskPathPointsToExistentDirectoryError

# https://oauth.yandex.ru/authorize?response_type=token&client_id=af20c4eb971f409eab78fd72cc6274b6
# url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={client_id}"
# session = ClientSession()
# ic(session.headers)
# async with session.get(url) as response:
#     ic(response.status)
#     # ic(await response.text())
#     print(await response.text())
# await session.close()
# token = "y0_AgAAAAABo1wMAAsTvgAAAAD3AGxAgdTeBafNQVmF-8JM3lycdXRhpE8"
# client = yadisk.AsyncClient(token=token)
# ic(await client.check_token(token))
# # https://5.149.157.87:8004/auth
# from aiohttp import ClientSession
# from fake_useragent import UserAgent
# def create_session() -> ClientSession:
#     headers = {"User-Agent": UserAgent().random}
#     session = ClientSession()
#     session.headers.update(headers)
#     return session
