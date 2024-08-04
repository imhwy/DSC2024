<!-- (Clone/push)...

Mở CMD, cd tới folder này và chạy câu lệnh "pip install -r requirements.txt"

Sau đó điền API Key lần lượt vào file "text_correction.py", "domain_clf_Gemini.py" và "language_detection.py" (Key hiện tại của em là của Gemini free nên em để đó rồi push lên luôn ạ)

Tiếp theo chạy câu lệnh "streamlit run app_st.py" để có thể chạy FE streamlit để thử chức năng function

hoặc có thể "python app.py" để chạy trên terminal -->

(clone/pull/...)

AIO.py có hàm main với mục đích xử lý câu hỏi, nếu câu hỏi trong phạm vi trả lời của chatbot, thì xử lý. Nếu không, trả lời người đọc (hoặc trả về giá trị để phase sau của application thực hiện)

DÙng hàm main: (Như trong AIO_test.py)

from AIO import preprocess_text  
...
sau đó, lưu đoạn text là câu hỏi cần xử lý dưới 1 biến chuỗi, sau đó gọi hàm "preprocess_text(--biến--)"

kết quả sẽ trả về một đoạn text có thể là xử lý câu hỏi vì câu hỏi hợp lệ, hoặc có thể trả lời khác nếu câu hỏi ngoài tầm quan tâm chính quy