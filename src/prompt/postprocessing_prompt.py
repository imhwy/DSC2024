"""
This prompt for post processing.
"""

POST_PROCESS = """
{result}

{source}
"""

SOURCE = """
### Tài liệu
{title_text}
{session_text}
{page_text}
{data_type_text}
{link_text}
"""

FAIL_CASE = "Nội dung bạn đề cập không nằm trong phạm vi của nhà trường."
