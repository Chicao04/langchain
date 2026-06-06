# core/chains.py
from config.output import OutputConfig
from config.settings import AIConfig
from core.prompts import AIPrompts
from core.knowledge import KnowledgeBase  # <-- IMPORT KNOWLEDGEBASE VÀO ĐÂY

class MiniAssistantChain:
    def __init__(self):
        self.model = AIConfig.get_gemini_model(temperature=0.4)
        self.prompt = AIPrompts.get_assistant_prompt()
        self.chain = self.prompt | self.model

    def run(self, user_input: str, context: str = "") -> str:
        try:
            response = self.chain.invoke({
                "user_input": user_input,
                "context": context or "Không có bối cảnh bổ sung."
            })
            return OutputConfig.format_assistant_text(response)
        except Exception as e:
            return f"Lỗi trong quá trình xử lý Chain: {str(e)}"


# === CLASS MỚI: TRỢ LÝ ĐỌC TÀI LIỆU (RAG) ===
class RAGAssistantChain(MiniAssistantChain):
    def __init__(self):
        super().__init__()
        # Khởi tạo tri thức và lấy bộ retriever từ cơ sở dữ liệu ChromaDB
        self.kb = KnowledgeBase()
        self.retriever = self.kb.get_retriever()

    def run(self, user_input: str) -> str:
        """Hàm tự động tìm tài liệu liên quan rồi mới trả lời"""
        try:
            # 1. Tự động truy vấn Vector DB để lấy ra 3 đoạn văn bản liên quan nhất k=3
            relevant_docs = self.retriever.invoke(user_input)            
            # 2. Gộp nội dung các đoạn văn bản đó lại làm bối cảnh (Context)
            context_list = []
            for doc in relevant_docs:
                page_info = f"[Nguồn: Trang {doc.metadata.get('page', 0) + 1}]"
                context_list.append(f"{page_info}\n{doc.page_content}")
                
            context = "\n\n".join(context_list)
            
            if not context:
                context = "Không tìm thấy thông tin liên quan trong tài liệu."

            # 3. Gửi cả câu hỏi và bối cảnh lấy từ PDF qua cho Gemini xử lý
            response = self.chain.invoke({
                "user_input": user_input,
                "context": context
            })
            
            return OutputConfig.format_assistant_text(response)
            
        except Exception as e:
            return f"Lỗi trong quá trình xử lý RAG Chain: {str(e)}"

class ITAnalyzerChain(MiniAssistantChain):
    pass