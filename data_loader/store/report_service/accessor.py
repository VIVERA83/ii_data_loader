# from io import BytesIO
#
# from aiohttp import ClientSession
#
# ANALYSIS_REPORT_URL = ("http://{host}:{port}/analysis/get_report_from_date/"
#                        "?start_date={start_date}&end_date={end_date}&kip_empty=true")
# BASE_URL = ""
#
#
# async def fetch_report_by_date(start_date: str, end_date: str, host: str = None, port: int = None, ):
#     async with ClientSession() as session, session.get(ANALYSIS_REPORT_URL.format(start_date=start_date,
#                                                                                   end_date=end_date,
#                                                                                   host=host or "localhost",
#                                                                                   port=port or 8005
#                                                                                   )) as response:
#         file = BytesIO(await response.read())
#         return file
#
#
# async def clear_database():
#     url = "http://0.0.0.0:8005/analysis/clear_db/"
#     async with ClientSession() as session, session.get(url) as response:
#         return await response.json()
import os
from io import BytesIO

from aiohttp import ClientSession
from urllib.parse import urljoin

from core.settings import ServiceSettings

ANALYSIS_REPORT_URL = "/analysis/get_report_from_date/?start_date={start_date}&end_date={end_date}&kip_empty=true"
CLEAR_DATABASE_URL = "/analysis/clear_db/"
BASE_URL = ServiceSettings().base_url  # "http://{host}:{port}"


async def create_request_url(relative_url: str, **parameters):
    url = urljoin(BASE_URL, relative_url.format(**parameters))
    print(url)
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
    return response.json()
# hello 2024-02-01 2024-01-01
