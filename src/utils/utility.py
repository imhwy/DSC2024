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
    subject_a_name: str,
    subject_b_name: str,
    subject_c_name: str,
    subject_a_point: float,
    subject_b_point: float,
    subject_c_point: float
) -> tuple:
    """
    """
    subject_aliases = {
        "Toán": ["Toán", "Toán học", "Toán cao cấp", "toan", "toán"],
        "Vật lý": ["vật lý", "Vật lý học", "Lý", "lý", "lí", "li", "ly"],
        "Hóa học": ["Hóa", "Hóa học", "hoa", "hoa hoc", "hóa"],
        "Tiếng Anh": ["Tiếng Anh", "Anh văn", "Anh ngữ", "anh", "Anh"],
        "Ngữ văn": ["Ngữ văn", "Văn học", "van", "văn", "Văn"],
        "Tiếng Nhật": ["Tiếng Nhật", "Nhật ngữ", "nhat", "nhật", "Nhật"]
    }
    valid_combinations = {
        "A00": ["Toán", "Vật lý", "Hóa học"],
        "A01": ["Toán", "Vật lý", "Tiếng Anh"],
        "D01": ["Toán", "Ngữ văn", "Tiếng Anh"],
        "D06": ["Toán", "Ngữ văn", "Tiếng Nhật"],
        "D07": ["Toán", "Hóa học", "Tiếng Anh"]
    }

    def normalize_subject(subject_name: str) -> str:
        for official_name, aliases in subject_aliases.items():
            if subject_name in aliases:
                return official_name
        return None

    # Chuẩn hóa các môn học đầu vào
    subject_a_normalized = normalize_subject(subject_a_name)
    subject_b_normalized = normalize_subject(subject_b_name)
    subject_c_normalized = normalize_subject(subject_c_name)

    if None in [subject_a_normalized, subject_b_normalized, subject_c_normalized]:
        raise ValueError("Có môn học không hợp lệ.")

    # Tạo một danh sách các môn và sắp xếp chúng để so sánh với các tổ hợp hợp lệ
    entered_subjects = sorted(
        [subject_a_normalized, subject_b_normalized, subject_c_normalized])

    # Kiểm tra xem các môn nhập vào có thuộc một tổ hợp hợp lệ không
    for combination_name, combination in valid_combinations.items():
        if sorted(combination) == entered_subjects:
            return subject_a_point + subject_b_point + subject_c_point, combination_name
    raise ValueError("Tổ hợp môn học không hợp lệ.")


def compare_uit_national_high_school_graduation_scores(
    user_score: float,
    user_combination: str,
    year: int = 2024
) -> List[Dict]:
    """
    Compare user's score and combination with UIT majors.
    """
    # Get the graduation scores for the specified year
    if year > 2024:
        all_major_info = get_uit_national_high_school_graduation_scores_2024()
    elif year == 2024:
        all_major_info = get_uit_national_high_school_graduation_scores_2024()
    elif year == 2023:
        all_major_info = get_uit_national_high_school_graduation_scores_2023()
    elif year == 2022:
        all_major_info = get_uit_national_high_school_graduation_scores_2022()
    else:
        return []

    result = []
    for major_info in all_major_info:
        # Check if the user's score is greater than or equal to the major's required score
        is_score_pass = user_score >= major_info['score']

        # Check if the user's subject combination matches any valid combination for the major
        is_combination_valid = user_combination in major_info['combination']

        # The user passes if both the score and combination are valid
        is_pass = is_score_pass and is_combination_valid

        # Append the result for each major
        result.append({
            "major": major_info['major'],
            "is_pass": is_pass,
            "required_score": major_info['score'],
            "valid_combinations": major_info['combination']
        })

    return result


def compare_uit_competency_assessment_scores(
    user_score: float,
    year: int = 2024
) -> List[Dict]:
    """
    """
    if year > 2024:
        all_major_info = get_uit_competency_assessment_scores_2024()
    elif year == 2024:
        all_major_info = get_uit_competency_assessment_scores_2024()
    elif year == 2023:
        all_major_info = get_uit_competency_assessment_scores_2023()
    elif year == 2022:
        all_major_info = get_uit_competency_assessment_scores_2022()
    else:
        return []
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
            "score": 26.12,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "KHOA HỌC DỮ LIỆU",
            "major_code": "7460108",
            "score": 27.5,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "KHOA HỌC MÁY TÍNH",
            "major_code": "7480101",
            "score": 27.3,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "TRÍ TUỆ NHÂN TẠO",
            "major_code": "7480107",
            "score": 28.3,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "MẠNG MÁY TÍNH VÀ TRUYỀN THÔNG DỮ LIỆU",
            "major_code": "7480102",
            "score": 25.7,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "KỸ THUẬT PHẦN MỀM",
            "major_code": "7480103",
            "score": 26.85,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "HỆ THỐNG THÔNG TIN",
            "major_code": "7480104",
            "score": 26.25,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "HỆ THỐNG THÔNG TIN (CT TIÊN TIẾN)",
            "major_code": "7480104_TT",
            "score": 25.55,
            "combination": ["A01", "D01", "D07"]
        },
        {
            "major": "KỸ THUẬT MÁY TÍNH",
            "major_code": "7480106",
            "score": 26.25,
            "combination": ["A00", "A01"]
        },
        {
            "major": "CÔNG NGHỆ THÔNG TIN",
            "major_code": "7480201",
            "score": 27.1,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "CÔNG NGHỆ THÔNG TIN (VIỆT NHẬT)",
            "major_code": "7480201_N",
            "score": 25.55,
            "combination": ["A00", "A01", "D01", "D06", "D07"]
        },
        {
            "major": "AN TOÀN THÔNG TIN",
            "major_code": "7480202",
            "score": 26.77,
            "combination": ["A00", "A01", "D01", "D07"]
        },
        {
            "major": "THIẾT KẾ VI MẠCH",
            "major_code": "75202a1",
            "score": 26.5,
            "combination": ["A00", "A01"]
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
            "major": "Công nghệ thông tin",
            "major_code": "7480201",
            "score": 915
        },
        {
            "major": "Công nghệ thông tin (Việt Nhật)",
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


def get_uit_national_high_school_graduation_scores_2023() -> List[Dict[str, float]]:
    """
    Return a list of dictionaries containing the national high school graduation scores
    for each major in UIT in 2023.
    """
    return [
        {
            "major": "Computer Science",
            "major_code": "7480101",
            "score": 26.9
        },
        {
            "major": "Artificial Intelligence",
            "major_code": "7480107",
            "score": 27.8
        },
        {
            "major": "Network and Data Communications",
            "major_code": "7480102",
            "score": 25.4
        },
        {
            "major": "Software Engineering",
            "major_code": "7480103",
            "score": 26.9
        },
        {
            "major": "Information Systems",
            "major_code": "7480104",
            "score": 26.1
        },
        {
            "major": "Information Systems (Advanced)",
            "major_code": "7480104_TT",
            "score": 25.4
        },
        {
            "major": "E-Commerce",
            "major_code": "7340122",
            "score": 25.8},
        {
            "major": "Information Technology",
            "major_code": "7480201",
            "score": 26.9
        },
        {
            "major": "Information Technology (Vietnam-Japan)",
            "major_code": "7480201_N",
            "score": 25.9
        },
        {
            "major": "Data Science",
            "major_code": "7480108",
            "score": 27.1
        },
        {
            "major": "Information Security",
            "major_code": "7480202",
            "score": 26.3
        },
        {
            "major": "Computer Engineering",
            "major_code": "7480106",
            "score": 25.6
        },
        {
            "major": "Computer Engineering (IoT and Embedded Systems)",
            "major_code": "7480106_IOT",
            "score": 25.6
        },
        {
            "major": "Computer Engineering (Microelectronics)",
            "major_code": "7480106_TKVM",
            "score": 25.4
        }
    ]


def get_uit_competency_assessment_scores_2023() -> List[Dict[str, Any]]:
    """
    Return a list of dictionaries containing the competency assessment scores
    for each major in UIT in 2023.
    """
    return [
        {
            "major": "KHOA HỌC MÁY TÍNH",
            "major_code": "7480101",
            "score": 915
        },
        {
            "major": "TRÍ TUỆ NHÂN TẠO",
            "major_code": "7480107",
            "score": 970
        },
        {
            "major": "MẠNG MÁY TÍNH VÀ TRUYỀN THÔNG DỮ LIỆU",
            "major_code": "7480102",
            "score": 845
        },
        {
            "major": "KỸ THUẬT PHẦN MỀM",
            "major_code": "7480103",
            "score": 925
        },
        {
            "major": "HỆ THỐNG THÔNG TIN",
            "major_code": "7480104",
            "score": 855
        },
        {
            "major": "HỆ THỐNG THÔNG TIN (TIÊN TIẾN)",
            "major_code": "7480104_TT",
            "score": 825
        },
        {
            "major": "THƯƠNG MẠI ĐIỆN TỬ",
            "major_code": "7340122",
            "score": 860},
        {
            "major": "CÔNG NGHỆ THÔNG TIN",
            "major_code": "7480201",
            "score": 920
        },
        {
            "major": "CÔNG NGHỆ THÔNG TIN (VIỆT - NHẬT)",
            "major_code": "7480201_N",
            "score": 845
        },
        {
            "major": "KHOA HỌC DỮ LIỆU",
            "major_code": "7480108",
            "score": 915
        },
        {
            "major": "AN TOÀN THÔNG TIN",
            "major_code": "7480202",
            "score": 890
        },
        {
            "major": "KỸ THUẬT MÁY TÍNH",
            "major_code": "7480106",
            "score": 870
        },
        {
            "major": "KỸ THUẬT MÁY TÍNH (HỆ THỐNG NHÚNG VÀ IOT)",
            "major_code": "7480106_IOT",
            "score": 870
        },
        {
            "major": "KỸ THUẬT MÁY TÍNH (THIẾT KẾ VI MẠCH)",
            "major_code": "7480106_TKVM",
            "score": 810
        }
    ]


def get_uit_national_high_school_graduation_scores_2022() -> List[Dict[str, Any]]:
    """
    Return a list of dictionaries containing the national high school graduation scores 
    for each major in UIT in 2023.
    """
    return [
        {
            "major": "Khoa học máy tính",
            "major_code": "7480101",
            "score": 27.1},
        {
            "major": "Trí tuệ nhân tạo",
            "major_code": "7480107",
            "score": 28
        },
        {
            "major": "Mạng máy tính và truyền thông dữ liệu",
            "major_code": "7480102",
            "score": 26.3
        },
        {
            "major": "Kỹ thuật phần mềm",
            "major_code": "7480103",
            "score": 28.05
        },
        {
            "major": "Hệ thống thông tin",
            "major_code": "7480104",
            "score": 26.7},
        {
            "major": "Hệ thống thông tin (CT tiên tiến)",
            "major_code": "7480104_TT",
            "score": 26.2},
        {
            "major": "Thương mại điện tử",
            "major_code": "7340122",
            "score": 27.05},
        {
            "major": "Công nghệ thông tin",
            "major_code": "7480201",
            "score": 27.9},
        {
            "major": "Công nghệ thông tin (Việt - Nhật)",
            "major_code": "7480201_N",
            "score": 26.3},
        {
            "major": "Khoa học dữ liệu",
            "major_code": "7480109",
            "score": 27.05},
        {
            "major": "An toàn thông tin",
            "major_code": "7480202",
            "score": 26.95},
        {
            "major": "Kỹ thuật máy tính",
            "major_code": "7480106",
            "score": 26.55},
        {
            "major": "Kỹ thuật máy tính (Hướng hệ thống nhúng và IoT)",
            "major_code": "7480106_IOT",
            "score": 26.5
        },
    ]


def get_uit_competency_assessment_scores_2022() -> List[Dict[str, Any]]:
    """
    Return a list of dictionaries containing the competency assessment scores
    for each major in UIT in 2023.
    """
    return [
        {"major": "Khoa học máy tính", "major_code": "7480101", "score": 888},
        {"major": "Trí tuệ nhân tạo", "major_code": "7480107", "score": 940},
        {"major": "Mạng máy tính và truyền thông dữ liệu",
            "major_code": "7480102", "score": 810},
        {"major": "Kỹ thuật phần mềm", "major_code": "7480103", "score": 895},
        {"major": "Hệ thống thông tin", "major_code": "7480104", "score": 825},
        {"major": "Hệ thống thông tin (CT tiên tiến)",
         "major_code": "7480104_TT", "score": 800},
        {"major": "Thương mại điện tử", "major_code": "7340122", "score": 852},
        {"major": "Công nghệ thông tin", "major_code": "7480201", "score": 892},
        {"major": "Công nghệ thông tin (Việt - Nhật)",
         "major_code": "7480201_N", "score": 805},
        {"major": "Khoa học dữ liệu", "major_code": "7480109", "score": 880},
        {"major": "An toàn thông tin", "major_code": "7480202", "score": 858},
        {"major": "Kỹ thuật máy tính", "major_code": "7480106", "score": 843},
        {"major": "Kỹ thuật máy tính (Hướng hệ thống nhúng và IoT)",
         "major_code": "7480106_IOT", "score": 842},
    ]
