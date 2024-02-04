from io import BytesIO

from aiohttp import ClientSession
from urllib.parse import urljoin

from core.settings import ServiceSettings

ANALYSIS_REPORT_URL = "/analysis/report/?start_date={start_date}&end_date={end_date}&kip_empty=true"
CLEAR_DATABASE_URL = "/analysis/clear_db/"
BASE_URL = ServiceSettings().base_url


async def create_request_url(relative_url: str, **parameters):
    url = urljoin(BASE_URL, relative_url.format(**parameters))
    return url


async def make_request(url: str) -> bytes:
    async with ClientSession() as session, session.get(url) as response:
        return await response.read()


async def fetch_report_by_date(start_date: str, end_date: str) -> BytesIO:
    url = await create_request_url(ANALYSIS_REPORT_URL, start_date=start_date, end_date=end_date)
    response = await make_request(url)
    return BytesIO(response)


async def clear_database():
    url = await create_request_url(CLEAR_DATABASE_URL)
    response = await make_request(url)
    return response
