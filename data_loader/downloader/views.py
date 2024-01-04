from io import BytesIO
from typing import Any

from fastapi import APIRouter

from core.components import Request
from downloader.schemes import OkSchema, UploadFileSchema

downloader_route = APIRouter(prefix="/downloader", tags=["FILE"])


@downloader_route.post(
    "/add_data_from_file",
    summary="Add data from file",
    description="Add `pl` or `can` data from an excel file. "
    "Received data is processed immediately. <br>"
    "Note: \n"
    " - Only the first sheet is processed.\n"
    " - The file size is limited.\n",
    response_model=OkSchema,
)
async def add_pl_from_file(request: "Request", file: UploadFileSchema) -> Any:
    """
    This function is used to add data file to the cloud.

    Args:
        request (Request): The request object.
        file (UploadFileSchema): The file to be uploaded.

    Returns:
        Any: Returns an OK schema with a message.

    """
    await request.app.store.ya_disk.upload_file(
        BytesIO(await file.read()), file.filename
    )
    return OkSchema()
