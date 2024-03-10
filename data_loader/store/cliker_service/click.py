from urllib.parse import urljoin

from aiohttp import ClientSession
from core.settings import ServiceSettings

BASE_URL = ServiceSettings().clicker_base_url


async def create_request_url(relative_url: str, **parameters):
    url = urljoin(BASE_URL, relative_url.format(**parameters))
    return url


async def make_request(url: str) -> bytes:
    async with ClientSession() as session, session.get(url) as response:
        return await response.read()


async def test_request(test_data: str):
    test_url = f"/test?hello={test_data}"
    url = await create_request_url(test_url)
    response = await make_request(url)
    return response
