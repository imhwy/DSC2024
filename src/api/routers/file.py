"""
This module defines FastAPI endpoints for file.
"""

from fastapi import (status,
                     Depends,
                     APIRouter,
                     HTTPException,
                     Response)

from src.services.service import Service
from src.api.dependencies.dependency import get_service
from src.api.schemas.file import (FileUploadRequest)


file_router = APIRouter(
    tags=["File"],
    prefix="/file",
)


@file_router.post('/fileUpload', status_code=status.HTTP_200_OK)
async def file_upload(
    request_file: FileUploadRequest,
    service: Service = Depends(get_service)
) -> Response:
    """
    Endpoint to handle file uploads.

    Args:
        request_file (FileUploadRequest): The uploaded file data.
        service (Service): The service used for file management.

    Raises:
        HTTPException: If request data is missing or an error occurs.

    Returns:
        dict: Success message if the file is uploaded successfully.
    """
    if not request_file.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data is required"
        )
    try:
        service.file_management.add_file(
            data_list=request_file.data
        )
        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Adding file successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@file_router.delete('/fileDelete', status_code=status.HTTP_200_OK)
async def file_delete(
    file_name: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    Endpoint to handle file deletion.

    Args:
        file_name (str): The name of the file to be deleted.
        service (Service): The service used for file management and repository access.

    Raises:
        HTTPException: If the file is not found or an error occurs during deletion.

    Returns:
        Response: Success message if the file is deleted successfully.
    """
    record = service.file_repository.get_specific_file(
        file_name=file_name
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not found"
        )
    try:
        service.file_management.delete_file(
            file_name=file_name
        )
        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Deleted file successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
