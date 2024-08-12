"""
this module provides utility functions
"""

import json
from typing import Optional
from datetime import datetime
import uuid
import time
import re

from src.prompt.postprocessing_prompt import (SOURCE,
                                              POST_PROCESS)


def convert_value(value):
    """
    Convert the string value from the environment variable to the appropriate type.

    Args:
        value: The string value from the environment variable.

    Returns:
        The converted value.
    """
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    try:
        int_value = int(value)
        return int_value
    except ValueError:
        pass
    try:
        float_value = float(value)
        return float_value
    except ValueError:
        pass
    try:
        json_value = json.loads(value)
        return json_value
    except (ValueError, json.JSONDecodeError):
        pass
    return value


def create_new_id(prefix: Optional[str] = 'req') -> str:
    """
    Create a new unique id value

    Args:
        Any

    Returns:
        new_id: Unique id value
    """
    new_id = prefix + '-' + str(uuid.uuid4()) + str(int(time.time()))[-4:]
    return str(new_id)


def get_datetime() -> str:
    """
    Retrieves the current date and time as a formatted string.

    Args:
        None

    Returns:
        str: The current date and time formatted as 'YYYY-MM-DD HH:MM:SS'.
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time


def get_last_part_of_url(url: str) -> str:
    """
    Extracts the last part of a URL path.

    Args:
        url (str): The URL string.

    Return:
        str: The last part of the URL path.
    """
    return url.rstrip('/').split('/')[-1]


def format_document(
    result,
    title,
    session,
    page,
    data_type,
    link
):
    """
    Formats the document with the given information.

    Args:
        result (str): The result of the document.
        title (str): The title of the document.
        session_name (str): The name of the session.
        page_number (str): The page number of the document.
        data_type (str): The type of the data.
        link (str): The link to the document.

    Returns:
        str: The formatted document.
    """
    title_section = f"**Nguồn tài liệu:** {title}" if title else ""
    session_section = f"**Chương:** {session}" if session else ""
    page_section = f"**Trang:** {page}" if page else ""
    data_type_section = f"**Dạng dữ liệu:** {data_type}" if data_type else ""
    link_section = f"**Đường dẫn:** {link}" if link else ""

    source = SOURCE.format(
        title_text=title_section,
        session_text=session_section,
        page_text=page_section,
        data_type_text=data_type_section,
        link_text=link_section
    )
    cleaned_source = re.sub(r'\n+', '\n', source.strip())
    cleaned_document = POST_PROCESS.format(
        result=result,
        source=cleaned_source
    )

    return cleaned_document
