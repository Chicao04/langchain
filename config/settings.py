# config/settings.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Tải biến môi trường
load_dotenv()

class AIConfig:
    @staticmethod
    def get_gemini_model(model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """Khởi tạo và cấu hình model Gemini với cơ chế tự sửa lỗi RPM"""
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_retries=5, # Tự động thử lại nếu dính lỗi 429 hoặc 503
        )