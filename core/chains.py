# core/chains.py
from config.settings import AIConfig
from core.prompts import AIPrompts

class MiniAssistantChain:
    def __init__(self):
        # Gọi model và prompt từ các module đã cấu trúc
        self.model = AIConfig.get_gemini_model(temperature=0.4)
        self.prompt = AIPrompts.get_assistant_prompt()
        
        # Tạo chuỗi xử lý bằng toán tử Pipe (|) của LangChain
        self.chain = self.prompt | self.model

    def run(self, user_input: str, context: str = "") -> str:
        """Hàm thực thi chuỗi hội thoại cho trợ lý mini"""
        try:
            response = self.chain.invoke({
                "user_input": user_input,
                "context": context or "Không có bối cảnh bổ sung."
            })
            return response.content
        except Exception as e:
            return f"Lỗi trong quá trình xử lý Chain: {str(e)}"


class ITAnalyzerChain(MiniAssistantChain):
    """Giữ lại tên cũ để không làm hỏng các chỗ import đang có."""
    pass