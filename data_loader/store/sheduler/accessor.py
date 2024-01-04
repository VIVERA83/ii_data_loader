import asyncio
from asyncio import CancelledError, Task, sleep
from typing import Optional
from uuid import UUID

from base.base_accessor import BaseAccessor

# from core.settings import SchedulerSettings
# from store.labor_protect.models import StatusTask, TaskModel
# from store.labor_protect_crawler.schemas import UpdateData


class SchedulerAccessor(BaseAccessor):
    is_running: Optional[bool] = False
    task: Optional[Task] = None
    settings: SchedulerSettings

    async def connect(self):
        self.settings = SchedulerSettings()
        self.is_running = True
        self.task = asyncio.create_task(self.worker())
        self.logger.info("Scheduler ready")

    async def disconnect(self):
        self.is_running = False
        self.task.cancel()
        await self.task
        self.logger.info("Scheduler closed")

    async def worker(self):
        while self.is_running:
            try:
                tasks = await self._get_planned_tasks()
                if tasks:
                    self.logger.info(
                        f"New tasks in progress {len(tasks)}: {[task.task for task in tasks]}"
                    )
                    await self._update_task_status_to_in_progress(
                        [task.id for task in tasks]
                    )
                    # TODO: снять коммит когда будет готово
                    # update_data = await self.run_tasks(tasks)
                    update_data = get_mock_update_data(tasks)
                    await self._update_task_status(update_data)
                    self.logger.info(
                        f"Tasks successful {len(tasks)}: {[task.task for task in tasks]}"
                    )
            except CancelledError:
                self.logger.warning("Scheduler cancelled")
                break
            await self.__refresh_delay()

    async def _get_planned_tasks(self) -> list[TaskModel]:
        return await self.app.store.labor_protect_service.get_planned_task(
            self.settings.limit
        )

    async def _update_task_status_to_in_progress(self, tasks_ids: list[UUID]):
        await self.app.store.labor_protect_service.update_status_task(
            tasks_ids, status=StatusTask.in_progress
        )

    async def _update_task_status(self, update_data: dict):
        for task_id, data in update_data.items():
            await self.app.store.labor_protect_service.update_task_by_id(
                task_id, UpdateData(**data).as_dict
            )

    async def __refresh_delay(self):
        try:
            await sleep(self.settings.refresh_delay)
        except CancelledError:
            self.logger.warning("Scheduler cancelled.")
            self.is_running = False


def get_mock_update_data(tasks: list[TaskModel]) -> dict:
    return {
        task.id: {
            "2310": "hidden",
            "2313": "hidden",
            "is_login": True,
        }
        for task in tasks
    }
