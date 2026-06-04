# core/chains.py
from config.settings import AIConfig
from core.prompts import AIPrompts

class ITAnalyzerChain:
    def __init__(self):
        # Gọi model và prompt từ các module đã cấu trúc
        self.model = AIConfig.get_gemini_model(temperature=0.2) # Thấp để phân tích chính xác
        self.prompt = AIPrompts.get_analyzer_prompt()
        
        # Tạo chuỗi xử lý bằng toán tử Pipe (|) của LangChain
        self.chain = self.prompt | self.model

    def run(self, data: str) -> str:
        """Hàm thực thi chuỗi phân tích dữ liệu"""
        try:
            response = self.chain.invoke({"input_data": data})
            return response.content
        except Exception as e:
            return f"Lỗi trong quá trình xử lý Chain: {str(e)}"