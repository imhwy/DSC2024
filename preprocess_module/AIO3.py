import google.generativeai as genai
import re
import time

import joblib
from underthesea import word_tokenize

# Set up the API key for the Google Generative AI
genai.configure(api_key="")

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

# def classify_domain(text):
#     """
#     Classify the text as In Domain (1) or Out of Domain (0) based on whether it is about university admission programs.
#     """
#     prompt = f"Xác định xem đoạn văn dưới này có thuộc dạng câu hỏi về chương trình tuyển sinh của một trường đại học không, nếu có trả về 1, không trả về 0: {text}"
#     response = model.generate_content(prompt)
#     prediction = response.text.strip()
#     return int(prediction)


svm_model = joblib.load('C:/Users/ADMIN/Desktop/DSC/github/DSC2024/preprocess_module/Materials (removable)/Models/svm_model.joblib')
tfidf_vectorizer = joblib.load('C:/Users/ADMIN/Desktop/DSC/github/DSC2024/preprocess_module/Materials (removable)/Models/tfidf_vectorizer.joblib')
def tokenize_text(text):
    tokens = word_tokenize(text, format='text')
    return tokens
def classify_domain(text):
    # Preprocess the text
    processed_text = tokenize_text(text)

    # Convert to TF-IDF features
    text_tfidf = tfidf_vectorizer.transform([processed_text])

    # Predict and measure time
    prediction = svm_model.predict(text_tfidf)
    return prediction[0]


def lang_detect(text):

    lang = "vi" # or "en" or "vi_en" "no_tonemark_vi" "no_tonemark_vi_en"
    return lang

# def is_vietnamese_text(text):
#     prompt = f"Identify the language of the following text and return the language code: {text}. If it is Vietnamese, return 'vi', else return 'False'."
#     response = model.generate_content(prompt)
#     lang = response.text.strip()
#     return lang == 'vi'


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

# def correct_vietnamese_text(text):
#     prompt = f"""You have the following roles:

#     If the input {text} is in Vietnamese, please check and correct spelling errors, and add any missing punctuation to ensure the sentence has complete meaning.

#     If the input {text} is in English, please translate it into Vietnamese.

#     If the input {text} is a Vietnamese sentence containing English words, please translate it entirely into Vietnamese.

#     Finally, return the output as the processed input."""
#     response = model.generate_content(prompt)
#     return response.text.strip()

def correct_vietnamese_text(text):
    prompt = f"""Thêm dấu tiếng Việt và sửa lỗi chính tả cho văn bản tiếng Việt dưới đây: {text}."""
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_en_text(text):
    prompt = f"""You have the role: 

    Translate the following English text into Vietnamese: {text}

    Return the output as the processed input."""
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_vi_en_text(text):
    prompt = f"""You have the role: 

    Translate each english word in this sentence into Vietnamese and translate the who sentence into Vietnamese. Besides check and correct spelling errors, and
    add any mising punctuation to ensure the sentence has complete meaning and exactly Vietnamese form: {text}

    Return the output as the processed input."""
    response = model.generate_content(prompt)
    return response.text.strip()

def preprocess_text(text_input):
    """
    Process the input text and return a text result.
    """
    query = ""
    language = True
    flag = False

    if text_input:
        # s1 = time.time()
        # if not is_vietnamese_text(text_input):
        #     language = False
        # e1 = time.time()
        # print(f"Language detection time: {e1 - s1}")

        s1 = time.time()
        lang = lang_detect(text_input)
        e1 = time.time()
        print(f"Language detection time: {e1 - s1}")

        if lang == "vi" or lang == "no_tonemark_vi":
            language = True
            s2 = time.time()
            corrected_text = correct_vietnamese_text(text_input)
            e2 = time.time()
        if lang == "en":
            language = True
            s2 = time.time()
            corrected_text = translate_en_text(text_input)
            e2 = time.time()
        
        if lang == "vi_en" or lang == "no_tonemark_vi_en":
            language = True
            s2 = time.time()
            corrected_text = translate_vi_en_text(text_input)
            e2 = time.time()
        
        print(f"Text correction time: {e2 - s2}")

        s2 = time.time()
        corrected_text = correct_vietnamese_text(text_input)
        e2 = time.time()
        print(f"Text correction time: {e2 - s2}")

        s3 = time.time()
        if is_prompt_injection(corrected_text):
            flag = True
        e3 = time.time()
        print(f"Prompt injection time: {e3 - s3}")

        s4 = time.time()
        domain = classify_domain(corrected_text)
        e4 = time.time()
        print(f"Domain classification time: {e4 - s4}")

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
