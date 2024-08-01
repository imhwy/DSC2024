"""
"""

from typing import List
from pydantic import BaseModel


class RequestFileUpload(BaseModel):
    """
    """
    url: List[str]
    file_type: List[str]


class ResponseFileUpload(BaseModel):
    """
    """
    file_type: List[str]
    message: str
