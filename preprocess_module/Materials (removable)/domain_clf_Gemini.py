import google.generativeai as genai

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

def classify_domain(text):
    """
    Classify the text as In Domain (1) or Out of Domain (0) based on whether it is about university admission programs.
    """
    prompt = f"Xác định xem đoạn văn dưới này có thuộc dạng câu hỏi về chương trình tuyển sinh của một trường đại học không, nếu có trả về 1, không trả về 0: {text}"
    response = model.generate_content(prompt)
    prediction = response.text.strip()
    return int(prediction)