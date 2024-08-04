"""
This schemas is used for file
"""

from typing import List
from pydantic import BaseModel


class FileUpload(BaseModel):
    """
    Represents a file upload with its URL, type, and name.
    """
    url: str
    file_type: str
    file_name: str


class FileUploadRequest(BaseModel):
    """
    Represents a list of file uploads.
    """
    data: List[FileUpload]


class FileUploadResponse(BaseModel):
    """
    Represents a response message for a file upload operation.
    """
    message: str
