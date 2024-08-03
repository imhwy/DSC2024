"""
This module defines FastAPI endpoints for file.
"""
import os
import requests
from dotenv import load_dotenv
from fastapi import (status,
                     Depends,
                     APIRouter,
                     HTTPException)

from src.services.service import Service
from src.api.dependencies.dependency import get_service
from src.api.schemas.file import (RequestFileUpload,
                                  ResponseFileUpload)
from src.utils.utility import convert_value

load_dotenv()

TIME_OUT = convert_value(os.getenv('TIME_OUT'))

file_router = APIRouter(
    tags=["File"],
    prefix="/file",
)


@file_router.post('/fileUpload', status_code=status.HTTP_200_OK, response_model=ResponseFileUpload)
async def file_upload(
    request_file: RequestFileUpload,
    service: Service = Depends(get_service)
) -> ResponseFileUpload:
    """
    """
    if not request_file.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
    try:
        urls = service.file_management.add_file(
            urls=request_file.url
        )
        return ResponseFileUpload(
            file_type=urls,
            message="File added successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e


@file_router.delete('/fileDelete', status_code=status.HTTP_200_OK, response_model=ResponseFileUpload)
async def file_delete(
    file_name: str = None,
    service: Service = Depends(get_service)
) -> ResponseFileUpload:
    """
    """
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
    if not service.file_repository.get_file(
        file_name=file_name
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file found in database"
        )
    try:
        service.file_management.delete_file(
            file_name=file_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e
