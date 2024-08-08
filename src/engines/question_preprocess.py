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

def tokenize_text(text):
    """
    Tokenizes the input text using underthesea.

    Args:
        text (str): The text to be tokenized.

    Returns:
        str: The tokenized text.
    """
    tokens = word_tokenize(text, format='text')
    return tokens

def classify_domain(text):
    """
    Classifies the domain of the input text using a pre-trained SVM model.

    Args:
        text (str): The text to classify.

    Returns:
        int: The predicted domain label of the text.
    """
    # Load model and vectorizer
    svm_model = joblib.load('C:/Users/ADMIN/Desktop/DSC/github/DSC2024/preprocess_module/Materials (removable)/Models/svm_model.joblib')
    tfidf_vectorizer = joblib.load('C:/Users/ADMIN/Desktop/DSC/github/DSC2024/preprocess_module/Materials (removable)/Models/tfidf_vectorizer.joblib')

    # Preprocess the text
    processed_text = tokenize_text(text)

    # Convert to TF-IDF features
    text_tfidf = tfidf_vectorizer.transform([processed_text])

    # Predict and measure time
    prediction = svm_model.predict(text_tfidf)
    return prediction[0]

def lang_detect(text):
    """
    Detects the language of the input text.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The detected language code.
    """
    lang = "vi" # or "en" or "vi_en" "no_tonemark_vi" "no_tonemark_vi_en"
    return lang

def is_prompt_injection(text):
    """
    Checks if the input text contains any prompt injection patterns.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if prompt injection is detected, False otherwise.
    """
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
    """
    Uses Google Generative AI to correct and add Vietnamese tone marks to the text.

    Args:
        text (str): The Vietnamese text to correct.

    Returns:
        str: The corrected Vietnamese text.
    """
    prompt = f"""Thêm dấu tiếng Việt và sửa lỗi chính tả, và xử lý các từ viết tắt (viết đầy đủ hơn) cho văn bản tiếng Việt dưới đây: {text}."""
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_en_text(text):
    """
    Translates English text to Vietnamese using Google Generative AI.

    Args:
        text (str): The English text to translate.

    Returns:
        str: The translated Vietnamese text.
    """
    prompt = f"""You have the role: 

    Translate the following English text into Vietnamese: {text}

    Return the output as the processed input."""
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_vi_en_text(text):
    """
    Translates a mixed Vietnamese-English text to Vietnamese using Google Generative AI.

    Args:
        text (str): The mixed Vietnamese-English text to translate.

    Returns:
        str: The fully translated and corrected Vietnamese text.
    """
    prompt = f"""You have the role: 

    Translate each english word in this sentence into Vietnamese and translate the whole sentence into Vietnamese. Besides, check and correct spelling errors, and
    add any missing punctuation to ensure the sentence has complete meaning and exactly Vietnamese form: {text}

    Return the output as the processed input."""
    response = model.generate_content(prompt)
    return response.text.strip()

def preprocess_text(text_input):
    """
    Processes the input text by performing language detection, correction/translation, 
    prompt injection detection, and domain classification.

    Args:
        text_input (str): The text to process.

    Returns:
        tuple: A tuple containing the processed query (str), a language flag (bool), and a prompt injection flag (bool).
    """
    query = ""
    language = True
    flag = False

    if text_input:
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

        s3 = time.time()
        if is_prompt_injection(corrected_text):
            flag = True
        e3 = time.time()
        print(f"Prompt injection detection time: {e3 - s3}")

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
    return query, language, flag