import time
import streamlit as st
from text_correction import correct_vietnamese_text
from language_detection import is_vietnamese_text
from prompt_injection_detection import is_prompt_injection
from domain_clf_SavedModel import predict_label_from_text
from domain_clf_Gemini import classify_domain

# Paths to the model and tokenizer
model_path = "C:/Users/ADMIN/Desktop/DSC/Final/model"
tokenizer_path = "C:/Users/ADMIN/Desktop/DSC/Final/tokenizer"

# Streamlit application
st.title("Vietnamese Text Correction and Classification using Local Model")

text_input = st.text_area("Nhập câu hỏi cần xử lý:")

if st.button("Xử lý câu hỏi"):
    if text_input:
        start_time = time.time()
        
        if not is_vietnamese_text(text_input):
            st.write("Xin lỗi, chúng tôi chỉ hỗ trợ tiếng Việt")
        else:
            corrected_text = correct_vietnamese_text(text_input)
            if is_prompt_injection(corrected_text):
                st.write("Xin lỗi, chúng tôi không hỗ trợ prompt injection")
            else:
                s1 = time.time()
                # Use the predict_label_from_text function for domain classification
                domain = predict_label_from_text(corrected_text, model_path, tokenizer_path) # Use Local Model
                # domain = classify_domain(corrected_text) # Use Gemini
                e1 = time.time()
                t1 = s1 - e1
                st.write(f"Thời gian xử lý: {t1:.2f} giây")
                if domain == 0:
                    st.write("Xin lỗi, chúng tôi không hỗ trợ câu hỏi này")
                else:
                    st.write("Thuộc quy trình xử lý (In domain)")
                    st.write("Câu hỏi đã được xử lý:")
                    st.write(corrected_text)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        st.write(f"Thời gian xử lý: {elapsed_time:.2f} giây")
    else:
        st.write("Vui lòng nhập câu hỏi để xử lý.")
