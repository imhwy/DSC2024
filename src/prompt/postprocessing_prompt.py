"""
This prompt for post processing.
"""

POST_PROCESS = """
{result}

## Nguồn thông tin
{source}
"""

SOURCE = """
### Tài liệu {idx}
{title_text}
{session_text}
{page_text}
{data_type_text}
{link_text}
"""

FAIL_CASES = [
    "Nội dung bạn đề cập không nằm trong phạm vi của nhà trường.",
    None,
    "None"
]

RESPONSE_FAIL_CASE = """
Xin chào! Rất tiếc, tôi chưa thể cung cấp thông tin mà bạn đang tìm kiếm vào lúc này. Nhưng đừng lo, tôi luôn sẵn sàng hỗ trợ bạn!

Để biết thêm thông tin chi tiết, bạn có thể liên hệ qua:

- **Hotline**: 090.883.1246
- **Website**: [tuyensinh.uit.edu.vn](https://tuyensinh.uit.edu.vn)

Cảm ơn bạn đã sử dụng dịch vụ của UITAdminBot! Nếu có thắc mắc khác, đừng ngần ngại hỏi tôi nhé.
"""

RESPONSE_UNSUPPORTED_LANGUAGE = """

"""

RESPONSE_PROMPT_INJECTION = """

"""
