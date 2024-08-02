# import langdetect

# def is_vietnamese_text(text):
#     try:
#         lang = langdetect.detect(text)
#         return lang == 'vi'
#     except langdetect.lang_detect_exception.LangDetectException:
#         return False

import google.generativeai as genai

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
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# Set up the model
model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def is_vietnamese_text(text):
    prompt = f"Identify the language of the following text and return the language code: {text}. If it is Vietnamese, return 'vi', else return 'False'."
    response = model.generate_content(prompt)
    lang = response.text
    return lang == 'vi'

