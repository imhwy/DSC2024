import re

def is_prompt_injection(text):
    prompt_injection_patterns = [
        r"bỏ qua hướng dẫn trước",
        r"bỏ qua phần trên",
        r"bỏ qua chỉ dẫn trước",
        r"bỏ qua chỉ dẫn trên",
        r"lờ đi hướng dẫn trước",
        r"lờ đi phần trên",
        r"bỏ qua lệnh trước",
        r"bỏ qua lệnh trên",
        r"vượt qua",
        r"phá vỡ",
        r"trick AI",
        r"hack AI",
        r"độc hại",
        r"tiêm nhiễm"
    ]
    
    for pattern in prompt_injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
