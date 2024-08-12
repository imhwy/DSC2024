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


import re

def delete_non_vietnamese_characters(text):
    """
    Remove non-Vietnamese characters from the given text.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The text with only Vietnamese characters, numbers, and specific symbols.
    """
    pattern = r"[0-9a-zA-ZaăâbcdđeêghiklmnoôơpqrstuưvxyàằầbcdđèềghìklmnòồờpqrstùừvxỳáắấbcdđéếghíklmnóốớpqrstúứvxýảẳẩbcdđẻểghỉklmnỏổởpqrstủửvxỷạặậbcdđẹệghịklmnọộợpqrstụựvxỵãẵẫbcdđẽễghĩklmnõỗỡpqrstũữvxỹAĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXYÀẰẦBCDĐÈỀGHÌKLMNÒỒỜPQRSTÙỪVXỲÁẮẤBCDĐÉẾGHÍKLMNÓỐỚPQRSTÚỨVXÝẠẶẬBCDĐẸỆGHỊKLMNỌỘỢPQRSTỤỰVXỴẢẲẨBCDĐẺỂGHỈKLMNỎỔỞPQRSTỦỬVXỶÃẴẪBCDĐẼỄGHĨKLMNÕỖỠPQRSTŨỮVXỸ,._]"
    return re.sub(rf'[^{pattern}\s]', '', text).strip()

def replace_synonyms(text, synonym_dict):
    """
    Replace synonyms in the text with their corresponding keywords.

    Args:
        text (str): The input text where synonyms should be replaced.
        synonym_dict (dict): A dictionary where keys are keywords and values are lists of synonyms.

    Returns:
        str: The text with synonyms replaced by their respective keywords.
    """
    # Convert text to lowercase to make the replacement case-insensitive
    text = text.lower()

    # Iterate over each keyword and its associated synonyms
    for keyword, synonyms in synonym_dict.items():
        keyword = keyword.lower()
        for synonym in synonyms:
            synonym = synonym.strip().lower()
            # Use regex to replace only whole words to avoid partial matches
            text = re.sub(r'\b{}\b'.format(re.escape(synonym)), keyword, text)

    return text

def replace_symbols(text):
    """
    Replace specific symbols in the text with their word equivalents.

    Args:
        text (str): The input text containing symbols.

    Returns:
        str: The text with symbols replaced by their corresponding words.
    """
    replacements = {
        ">": " lớn hơn ",
        "<": " bé hơn ",
        "=": " bằng ",
        "$": " ",
        "#": " ",
        "^": " ",
        "/": " ",
        "!": " "
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    return " ".join(text.split())

def clean_text(text, term_dict):
    """
    Perform a series of text cleaning operations, including removing non-Vietnamese characters,
    replacing synonyms, symbols, and normalizing elongated words.

    Args:
        text (str): The input text to be cleaned.
        table_keyword (pd.DataFrame): A DataFrame containing 'Synonym' and 'Keyword' columns.

    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'\s+', ' ', text)
    text = delete_non_vietnamese_characters(text.lower())
    text = replace_synonyms(text, term_dict)
    text = replace_symbols(text)
    return text