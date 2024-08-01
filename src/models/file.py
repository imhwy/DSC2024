"""
This module defines a Pydantic model for representing files with specific attributes.
"""
from pydantic import BaseModel


class File(BaseModel):
    """
    A Pydantic model representing a file with key attributes.

    Attributes:
        Id (str): A unique identifier for the file.
        name (str): The name of the file.
        file_type (str): The type or extension of the file (e.g., 'pdf', 'txt').
        time (str): A timestamp indicating when the file was created, modified, or accessed.
    """
    Id: str
    name: str
    file_type: str
    time: str
