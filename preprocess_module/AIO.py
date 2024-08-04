import google.generativeai as genai
import re

# Set up the API key for the Google Generative AI
genai.configure(api_key="AIzaSyAoAOLsZcoh1nNQt6CRDNv4N3CjUHMKfes")

# Set up the model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Set up the safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

# Set up the model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

def classify_domain(text):
    """
    Classify the text as In Domain (1) or Out of Domain (0) based on whether it is about university admission programs.
    """
    prompt = f"Xác định xem đoạn văn dưới này có thuộc dạng câu hỏi về chương trình tuyển sinh của một trường đại học không, nếu có trả về 1, không trả về 0: {text}"
    response = model.generate_content(prompt)
    prediction = response.text.strip()
    return int(prediction)

def is_vietnamese_text(text):
    prompt = f"Identify the language of the following text and return the language code: {text}. If it is Vietnamese, return 'vi', else return 'False'."
    response = model.generate_content(prompt)
    lang = response.text.strip()
    return lang == 'vi'

def is_prompt_injection(text):
    prompt_injection_patterns = [
        r"bỏ qua hướng dẫn trước", r"bỏ qua phần trên", r"bỏ qua chỉ dẫn trước",
        r"bỏ qua chỉ dẫn trên", r"lờ đi hướng dẫn trước", r"lờ đi phần trên",
        r"bỏ qua lệnh trước", r"bỏ qua lệnh trên", r"vượt qua", r"phá vỡ",
        r"trick AI", r"hack AI", r"độc hại", r"tiêm nhiễm"
    ]
    
    for pattern in prompt_injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def correct_vietnamese_text(text):
    prompt = f"Thêm dấu tiếng Việt và sửa lỗi chính tả cho văn bản tiếng Việt dưới đây: {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# def preprocess_text(text_input):
#     """
#     Process the input text and return a text result.
#     """
#     if text_input:
#         if not is_vietnamese_text(text_input):
#             return "Xin lỗi, chúng tôi chỉ hỗ trợ tiếng Việt"
        
#         corrected_text = correct_vietnamese_text(text_input)
#         if is_prompt_injection(corrected_text):
#             return "Xin lỗi, chúng tôi không hỗ trợ prompt injection"
        
#         domain = classify_domain(corrected_text)
#         if domain == 0:
#             return "Xin lỗi, chúng tôi không hỗ trợ câu hỏi này"
#         else:
#             return f"Thuộc quy trình xử lý (In domain):\n{corrected_text}"
#     else:
#         return "Vui lòng nhập câu hỏi để xử lý."

def preprocess_text(text_input):
    """
    Process the input text and return a text result.
    """
    query = ""
    language = True
    flag = False

    if text_input:
        if not is_vietnamese_text(text_input):
            language = False

        corrected_text = correct_vietnamese_text(text_input)
        if is_prompt_injection(corrected_text):
            flag = True

        domain = classify_domain(corrected_text)
        if domain == 0:
            flag = True

        if language and not flag:
            query = corrected_text
        else:
            query = text_input

    else:
        query = ""
    #print(f"Query: {query}, Language: {language}, Flag: {flag}")
    # Return the result and the flags
    return query, language, flag
