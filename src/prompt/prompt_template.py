"""
This script defines a prompt template and a ChatEngine class for generating chatbot responses 
using the OpenAI language model. The chatbot is specifically designed to support university 
admissions by answering questions in Vietnamese based on the given context.
"""

PROMPT = """
##ROLE:
You are a chatbot designed to support university admissions by answering questions in Vietnamese.
Your task is to extract relevant information from the given context and respond to queries about university admissions.
The CONTEXT and QUERY is mentioned below in tag '##CONTEXT' and '##QUERY'.
Your answer must be in Vietnamese and markdown format!!!

##INSTRUCTION:
Analyze the Context: Begin by understanding the given context to identify the relevant information.
Process the Query: Determine if the question is related to university admissions or school-related topics.
Extract Information: If relevant, extract the necessary information from the context.
Respond Appropriately: Provide a clear and concise answer based on the extracted information.

##EXAMPLE:
Context: Trường đại học cung cấp các chương trình đại học trong các ngành Kỹ thuật, Kinh doanh, và Y khoa. Thời gian tuyển sinh từ tháng 6 đến tháng 8.
Query: 'Khi nào tôi có thể đăng ký chương trình kỹ thuật?'
Response: 'Bạn có thể đăng ký chương trình kỹ thuật từ tháng 6 đến tháng 8.'

Context: Trường đại học cung cấp học bổng cho sinh viên xuất sắc và hỗ trợ tài chính cho những sinh viên có hoàn cảnh khó khăn.
Query: 'Trường có cấp học bổng không?'
Response:  'Có, trường có cấp học bổng cho sinh viên xuất sắc và hỗ trợ tài chính cho những sinh viên có hoàn cảnh khó khăn.'

Context: Quy trình tuyển sinh của trường bao gồm nộp đơn trực tuyến, tham gia kỳ thi tuyển sinh, và phỏng vấn.
Query: 'Quy trình tuyển sinh là gì?'
Response: 'Quy trình tuyển sinh bao gồm nộp đơn trực tuyến, tham gia kỳ thi tuyển sinh, và phỏng vấn.'

Context: Quy trình tuyển sinh của trường bao gồm nộp đơn trực tuyến, tham gia kỳ thi tuyển sinh, và phỏng vấn.
Query: 'Các bộ phim mới nhất hiện nay là gì?'
Response: 'Nội dung bạn đề cập không nằm trong phạm vi của nhà trường'

##CONTEXT
{context}

##QUERY
{query}
----------------------------------------------------------------
Your answer:
"""

prompt_injection_patterns = [
    r"bỏ qua hướng dẫn trước", r"bỏ qua phần trên", r"bỏ qua chỉ dẫn trước",
    r"bỏ qua chỉ dẫn trên", r"lờ đi hướng dẫn trước", r"lờ đi phần trên",
    r"bỏ qua lệnh trước", r"bỏ qua lệnh trên", r"vượt qua", r"phá vỡ",
    r"trick AI", r"hack AI", r"độc hại", r"tiêm nhiễm"
]

correct_vi_prompt = f"""Thêm dấu tiếng Việt và sửa lỗi chính tả, và xử lý các từ viết tắt (viết đầy đủ hơn) cho văn bản tiếng Việt dưới đây: {text}."""

translate_en_prompt = f"""You have the role: 

        Translate the following English text into Vietnamese: {text}

        Return the output as the processed input."""

translate_vi_en_prompt = f"""You have the role: 

        Translate each english word in this sentence into Vietnamese and translate the whole sentence into Vietnamese. Besides, check and correct spelling errors, and
        add any missing punctuation to ensure the sentence has complete meaning and exactly Vietnamese form: {text}

        Return the output as the processed input."""