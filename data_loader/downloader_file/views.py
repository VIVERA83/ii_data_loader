from io import BytesIO
from typing import Any

from fastapi import APIRouter
from icecream import ic

from core.components import Request
from downloader_file.schemes import OkSchema, UploadFileSchema

downloader_file_route = APIRouter(prefix="/downloader", tags=["TOPIC"])


@downloader_file_route.post(
    "/add_pl_from_file",
    summary="Добавить пл из файла",
    description="Добавить данные пл из `excel` файла. Полученные данные начинают обрабатываться немедленно. <br>"
    "Обратите внимание:\n"
    " - обрабатывается только первый лист\n"
    " - размер файла ограничен 1 Мб\n",
    response_model=OkSchema,
)
async def add_data_from_excel(request: "Request", file: UploadFileSchema) -> Any:
    ic(
        await request.app.store.ya_disk.upload_file(
            BytesIO(await file.read()), file.filename
        )
    )
    return OkSchema(message=f"{request.client}")
