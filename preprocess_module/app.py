import time
from text_correction import correct_vietnamese_text
from language_detection import is_vietnamese_text
from prompt_injection_detection import is_prompt_injection
from domain_clf_SavedModel import predict_label_from_text
from domain_clf_Gemini import classify_domain

# Paths to the model and tokenizer
model_path = "C:/Users/ADMIN/Desktop/DSC/Final/model"
tokenizer_path = "C:/Users/ADMIN/Desktop/DSC/Final/tokenizer"

def main():
    text_input = input("Nhập câu hỏi cần xử lý: ")
    
    if text_input:
        start_time = time.time()
        
        if not is_vietnamese_text(text_input):
            print("Xin lỗi, chúng tôi chỉ hỗ trợ tiếng Việt")
        else:
            corrected_text = correct_vietnamese_text(text_input)
            if is_prompt_injection(corrected_text):
                print("Xin lỗi, chúng tôi không hỗ trợ prompt injection")
            else:
                # Use the predict_label_from_text function for domain classification
                # domain = predict_label_from_text(corrected_text, model_path, tokenizer_path) # Use Local Model
                domain = classify_domain(corrected_text) # Use Gemini
                if domain == 0:
                    print("Xin lỗi, chúng tôi không hỗ trợ câu hỏi này")
                else:
                    print("Thuộc quy trình xử lý (In domain)")
                    print("Câu hỏi đã được xử lý:")
                    print(corrected_text)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Thời gian xử lý: {elapsed_time:.2f} giây")
    else:
        print("Vui lòng nhập câu hỏi để xử lý.")

if __name__ == "__main__":
    main()
