from datetime import datetime, timedelta
from io import BytesIO
from typing import Coroutine, Callable
from urllib.parse import urljoin

from aiohttp import ClientSession

from base.base_accessor import BaseAccessor
from core.settings import ServiceSettings
from store.report_service.time_utils import (
    get_week_number,
    get_start_end_of_week,
    get_first_and_last_day_of_month,
    get_first_day_of_month,
)


class TGReportService(BaseAccessor):
    CLEAR_DATABASE_URL = "/analysis/clear_db/"
    ANALYSIS_REPORT_URL = (
        "/analysis/report/?start_date={start_date}&end_date={end_date}&kip_empty=true"
    )
    bot_report_commands: list[tuple[str, str, Callable[[], Coroutine]]] = None
    settings: ServiceSettings = None

    async def connect(self):
        self.settings = ServiceSettings()
        self.bot_report_commands = self.create_report_commands()
        await self.app.bot.add_commands(self.bot_report_commands)
        self.logger.info("Telegram Report Service connected")

    async def disconnect(self):
        await self.app.bot.remove_commands(self.bot_report_commands)
        self.logger.info("Telegram Report Service disconnected")

    def create_request_url(self, relative_url: str, **parameters) -> str:
        url = urljoin(self.settings.base_url, relative_url.format(**parameters))
        return url

    @staticmethod
    async def make_request(url: str) -> bytes:
        async with ClientSession() as session, session.get(url) as response:
            return await response.read()

    async def clear_database(self):
        """
        Asynchronously clears the database by sending a request to the specified URL and returning the response.
        """
        url = self.create_request_url(self.CLEAR_DATABASE_URL)
        response = await self.make_request(url)
        return response

    async def get_report_by_date(self, start_date: str, end_date: str) -> BytesIO:
        """
        Asynchronously retrieves a report for a given date range.

        Args:
            start_date (str): The start date of the report.
            end_date (str): The end date of the report.

        Returns:
            BytesIO: A stream containing the report data.
        """
        url = self.create_request_url(
            self.ANALYSIS_REPORT_URL, start_date=start_date, end_date=end_date
        )
        response = await self.make_request(url)
        return BytesIO(response)

    async def get_report(self, start_date: str, end_date: str, name: str) -> BytesIO:
        """
        Async function to get a report within a specific date range and assign a name to the report file.
        Takes in start_date (str), end_date (str), and name (str) as parameters and returns a BytesIO object.

        Args:
            start_date (str): The start date of the report.
            end_date (int): The end date of the report.
            name (str): The name of the report.

        Returns:
            BytesIO: A stream containing the report data.
        """
        file = await self.get_report_by_date(start_date, end_date)
        file.name = name
        return file

    async def get_report_week(self) -> BytesIO:
        """
        Asynchronous function that retrieves a report for the past week and returns it as a BytesIO object.
        No parameters are accepted.

        Returns:
             BytesIO: A BytesIO object containing the report.
        """
        today = datetime.now()
        start = (today - timedelta(6)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_month(self) -> BytesIO:
        """
        Asynchronous function to get the report for the current month.
        It returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        today = datetime.now()
        start = (today - timedelta(29)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_current_day(self) -> BytesIO:
        """
        Asynchronously gets the report for the current day.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        start = datetime.now().strftime("%Y-%m-%d")
        return await self.get_report(start, start, f"report_from {start}.xlsx")

    async def get_report_current_week(self) -> BytesIO:
        """
        Asynchronously gets the report for the current week.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        year = datetime.now().year
        week_number = get_week_number()
        start, end = get_start_end_of_week(year, week_number)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_current_month(self) -> BytesIO:
        """
        Asynchronously gets the report for the current month.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        start, end = get_first_and_last_day_of_month()
        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_last_week(self) -> BytesIO:
        """
        Asynchronously gets the report for the last week.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        year = datetime.now().year
        week_number = get_week_number() - 1
        start, end = get_start_end_of_week(year, week_number)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_last_month(self) -> BytesIO:
        """
        Asynchronously gets the report for the last month.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """

        first_day = get_first_day_of_month()
        end = (datetime.fromisoformat(first_day) - timedelta(days=1)).isoformat()[:10]
        start = get_first_day_of_month(end)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    def create_report_commands(self) -> list[tuple[str, str, Callable[[], Coroutine]]]:
        return [
            ("report_week", "Отчет за неделю", self.get_report_week),
            ("report_month", "Отчет за месяц", self.get_report_month),
            ("report_current_day", "Отчет за текущий день", self.get_report_week),
            (
                "report_current_week",
                "Отчет за текущею неделю",
                self.get_report_current_week,
            ),
            (
                "report_current_month",
                "Отчет за текущий месяц",
                self.get_report_current_month,
            ),
            (
                "report_last_week",
                "Отчет за предыдущею неделю",
                self.get_report_last_week,
            ),
            ("report_last_month", "Отчет за прошлый месяц", self.get_report_last_month),
            ("clear", "Очисть базу данных", self.get_report_week),
        ]
