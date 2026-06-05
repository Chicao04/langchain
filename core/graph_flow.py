# core/graph_flow.py
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from config.settings import AIConfig
from core.knowledge import KnowledgeBase
from core.prompts import AIPrompts

# 1. Định nghĩa trạng thái (State) của Đồ thị
class AssistantState(TypedDict):
    text_input: str          # Văn bản đầu vào hoặc câu hỏi
    task_type: str           # Loại nhiệm vụ: 'translate' hoặc 'summarize'
    context: Optional[str]   # Ngữ cảnh tìm được từ tài liệu
    final_output: Optional[str] # Kết quả đầu ra cuối cùng

# Khởi tạo mô hình LLM và Vector DB
llm = AIConfig.get_gemini_model()
kb = KnowledgeBase()
retriever = kb.get_retriever()

# 2. Định nghĩa các Node (Nút xử lý logic)

def retrieve_context_node(state: AssistantState):
    """Nút bốc dữ liệu liên quan từ Vector DB"""
    print("[Node] Đang truy xuất tài liệu liên quan...")
    query = state["text_input"]
    
    # Tìm kiếm 3 đoạn tài liệu liên quan nhất
    docs = retriever.invoke(query)
    context_text = "\n\n".join([doc.page_content for doc in docs])
    
    return {"context": context_text}

def translate_node(state: AssistantState):
    """Nút xử lý dịch thuật chuyên sâu"""
    print("[Node] Đang thực hiện dịch thuật...")
    prompt_template = AIPrompts.get_translator_prompt()
    
    # Dựng prompt chứa ngữ cảnh và văn bản cần dịch
    chain = prompt_template | llm
    response = chain.invoke({
        "context": state.get("context", "Không có ngữ cảnh bổ sung."),
        "text": state["text_input"]
    })
    
    return {"final_output": response.content}

def summarize_node(state: AssistantState):
    """Nút xử lý tóm tắt tài liệu"""
    print("[Node] Đang tiến hành tóm tắt văn bản...")
    prompt_template = AIPrompts.get_summarizer_prompt()
    
    chain = prompt_template | llm
    response = chain.invoke({
        "context": state.get("context", "Không có bối cảnh."),
        "task": state["text_input"]
    })
    
    return {"final_output": response.content}

# 3. Định nghĩa hàm Router (Cung điều hướng có điều kiện)
def route_task(state: AssistantState):
    """Hàm phân nhánh dựa trên lựa chọn tác vụ của bạn"""
    if state["task_type"] == "translate":
        return "go_to_translate"
    else:
        return "go_to_summarize"

# 4. Lắp ráp sơ đồ Graph (StateGraph)
workflow = StateGraph(AssistantState)

# Thêm các Node vào sơ đồ
workflow.add_node("retrieve_context", retrieve_context_node)
workflow.add_node("translate_task", translate_node)
workflow.add_node("summarize_task", summarize_node)

# Thiết lập điểm bắt đầu (Entry Point)
workflow.set_entry_point("retrieve_context")

# Thêm đường nối có điều kiện (Conditional Edges) từ nút tìm kiếm sang các nút chức năng
workflow.add_conditional_edges(
    "retrieve_context",
    route_task,
    {
        "go_to_translate": "translate_task",
        "go_to_summarize": "summarize_task"
    }
)

# Kết nối các nút chức năng về điểm KẾT THÚC (END)
workflow.add_edge("translate_task", END)
workflow.add_edge("summarize_task", END)

# Biên dịch (Compile) đồ thị thành ứng dụng thực thi
app_graph = workflow.compile()

if __name__ == "__main__":
    print("=== TRỢ LÝ LANGGRAPH DỊCH THUẬT & TÓM TẮT BẮT ĐẦU ===")
    print("Gõ 'exit', 'quit' hoặc 'thoat' bất kỳ lúc nào để dừng.\n")
    
    while True:
        try:
            # 1. Nhập lựa chọn tác vụ
            print("Chọn tác vụ bạn muốn thực hiện:")
            print("1. Dịch thuật (translate)")
            print("2. Tóm tắt văn bản (summarize)")
            choice = input("Lựa chọn của bạn (1 hoặc 2): ").strip().lower()
            
            # Hỗ trợ thoát chương trình nhanh
            if choice in {"exit", "quit", "thoat"}:
                print("[Hệ thống] Tạm biệt.")
                break
                
            if choice not in {"1", "2", "translate", "summarize"}:
                print("[!] Lựa chọn không hợp lệ, vui lòng chọn lại.\n")
                continue
                
            # Chuẩn hóa giá trị task_type cho đúng định dạng State định nghĩa
            task_type = "translate" if choice in {"1", "translate"} else "summarize"
            
            # 2. Nhập văn bản hoặc nội dung yêu cầu câu hỏi
            if task_type == "translate":
                text_input = input("Nhập đoạn văn bản cần dịch: ").strip()
            else:
                text_input = input("Nhập yêu cầu tóm tắt (Ví dụ: Hãy tóm tắt nội dung chính): ").strip()
                
            if text_input.lower() in {"exit", "quit", "thoat"}:
                print("[Hệ thống] Tạm biệt.")
                break
                
            if not text_input:
                print("[!] Văn bản nhập vào không được để trống.\n")
                continue
            
            # 3. Tạo trạng thái ban đầu và kích hoạt LangGraph
            initial_state = {
                "text_input": text_input,
                "task_type": task_type
            }
            
            print("\n[*] Đang xử lý qua hệ thống Đồ thị (Graph)...")
            result = app_graph.invoke(initial_state)
            
            # 4. Hiển thị kết quả xử lý
            print("\n=== KẾT QUẢ TỪ LANGGRAPH ===")
            print(result.get("final_output", "Không nhận được phản hồi."))
            print("=" * 30 + "\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\n[Hệ thống] Đã ngắt kết nối. Tạm biệt.") 
            break
        except Exception as e:
            print(f"[!] Đã xảy ra lỗi trong quá trình thực thi Graph: {str(e)}\n")