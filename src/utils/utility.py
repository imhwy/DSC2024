"""
this module provides utility functions
"""

import json
from typing import Optional, List
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
    result: str,
    titles: List[str],
    sessions: List[str],
    pages: List[str],
    data_types: List[str],
    links: List[str]
) -> str:
    """
    Format the document based on the provided metadata.

    Args:
        result (str): The API response.
        titles (List[str]): The list of titles.
        sessions (List[str]): The list of sessions.
        pages (List[str]): The list of pages.
        data_types (List[str]): The list of data types.
        links (List[str]): The list of links.

    Returns:
        str: The formatted document.
    """
    sources = ""
    for index, _ in enumerate(sessions):
        sources += "\n" + SOURCE.format(
            idx=index + 1,
            title_text=f"**Tên tài liệu:** {titles[index]}" if titles[index] else "",
            session_text=f"**Chương:** {sessions[index]}" if sessions[index] else "",
            page_text=f"**Trang:** {pages[index]}" if pages[index] else "",
            data_type_text=f"**Dạng dữ liệu:** {data_types[index]}" if data_types[index] else "",
            link_text=f"**Đường dẫn:** {links[index]}" if links[index] else ""
        )

    cleaned_source = re.sub(r'\n+', '\n', sources.strip())
    cleaned_document = POST_PROCESS.format(
        result=result,
        source=cleaned_source
    )
    return cleaned_document
