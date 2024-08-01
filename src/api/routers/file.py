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
        response = requests.get(
            request_file.url,
            stream=True,
            timeout=TIME_OUT
        )
        response.raise_for_status()

        # Check content type and handle accordingly
        content_type = response.headers['Content-Type']
        file_content = response.content
        print(f"file_content: {content_type}")
        return ResponseFileUpload(
            file_type=content_type,
            message="succesfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e
