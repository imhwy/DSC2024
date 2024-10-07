"""
this module provides utility functions
"""

import json
from typing import (Optional,
                    List,
                    Dict,
                    Any)
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


def sum_subjects(
    subject_a: float,
    subject_b: float,
    subject_c: float
) -> float:
    """
    """
    return subject_a + subject_b + subject_c


def compare_score(
    user_score: float,
    all_major_info: List[Dict]
) -> List[Dict]:
    """
    """
    result = []
    for major_info in all_major_info:
        is_pass = user_score >= major_info['score']
        result.append({
            "major": major_info['major'],
            "is_pass": is_pass
        })
    return result


def get_uit_national_high_school_graduation_scores_2024() -> List[Dict[str, Any]]:
    """
    """
    return [
        {
            "major": "THƯƠNG MẠI ĐIỆN TỬ",
            "major_code": "7340122",
            "score": 26.12
        },
        {
            "major": "KHOA HỌC DỮ LIỆU",
            "major_code": "7460108",
            "score": 27.5
        },
        {
            "major": "KHOA HỌC MÁY TÍNH",
            "major_code": "7480101",
            "score": 27.3
        },
        {
            "major": "TRÍ TUỆ NHÂN TẠO",
            "major_code": "7480107",
            "score": 28.3
        },
        {
            "major": "MẠNG MÁY TÍNH VÀ TRUYỀN THÔNG DỮ LIỆU",
            "major_code": "7480102",
            "score": 25.7
        },
        {
            "major": "KỸ THUẬT PHẦN MỀM",
            "major_code": "7480103",
            "score": 26.85
        },
        {
            "major": "HỆ THỐNG THÔNG TIN",
            "major_code": "7480104",
            "score": 26.25
        },
        {
            "major": "HỆ THỐNG THÔNG TIN (CT TIÊN TIẾN)",
            "major_code": "7480104_TT",
            "score": 25.55
        },
        {
            "major": "KỸ THUẬT MÁY TÍNH",
            "major_code": "7480106",
            "score": 26.25
        },
        {
            "major": "CÔNG NGHỆ THÔNG TIN",
            "major_code": "7480201",
            "score": 27.1
        },
        {
            "major": "CÔNG NGHỆ THÔNG TIN (VIỆT NHẬT)",
            "major_code": "7480201_N",
            "score": 25.55
        },
        {
            "major": "AN TOÀN THÔNG TIN",
            "major_code": "7480202",
            "score": 26.77
        },
        {
            "major": "THIẾT KẾ VI MẠCH",
            "major_code": "75202a1",
            "score": 26.5
        },
    ]


def get_uit_competency_assessment_scores_2024() -> List[Dict[str, Any]]:
    """
    Return a list of dictionaries containing the competency assessment scores
    for each major in UIT in 2024.
    """
    return [
        {
            "major": "Thương mại điện tử",
            "major_code": "7340122",
            "score": 870
        },
        {
            "major": "Khoa học dữ liệu",
            "major_code": "7460108",
            "score": 935
        },
        {
            "major": "Khoa học máy tính",
            "major_code": "7480101",
            "score": 925
        },
        {
            "major": "Mạng máy tính và truyền thông dữ liệu",
            "major_code": "7480102",
            "score": 855
        },
        {
            "major": "Kỹ thuật phần mềm",
            "major_code": "7480103",
            "score": 926
        },
        {
            "major": "Hệ thống thông tin",
            "major_code": "7480104",
            "score": 880
        },
        {
            "major": "Hệ thống thông tin (CT Tiên tiến)",
            "major_code": "7480104_TT",
            "score": 850
        },
        {
            "major": "Kỹ thuật máy tính",
            "major_code": "7480106",
            "score": 888
        },
        {
            "major": "Trí tuệ nhân tạo",
            "major_code": "7480107",
            "score": 980
        },
        {
            "major": "Cơ sở dữ liệu",
            "major_code": "7480201",
            "score": 915
        },
        {
            "major": "Cơ sở dữ liệu (Việt Nhật)",
            "major_code": "7480201_N",
            "score": 850
        },
        {
            "major": "An toàn thông tin",
            "major_code": "7480202",
            "score": 910
        },
        {
            "major": "Thiết kế vi mạch",
            "major_code": "75202a1",
            "score": 910
        },
    ]
