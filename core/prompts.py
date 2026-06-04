# core/prompts.py
from langchain_core.prompts import ChatPromptTemplate

class AIPrompts:
    @staticmethod
    def get_analyzer_prompt():
        """Prompt mẫu dùng để phân tích dữ liệu hoặc lỗi IT"""
        return ChatPromptTemplate.from_messages([
            (
                "system", 
                "Bạn là một chuyên gia phân tích dữ liệu hệ thống IT cao cấp. "
                "Hãy phân tích thông tin đầu vào một cách logic, ngắn gọn và đưa ra giải pháp kỹ thuật cụ thể."
            ),
            (
                "user", 
                "Hãy phân tích giúp tôi vấn đề/dữ liệu sau đây:\n{input_data}"
            )
        ])