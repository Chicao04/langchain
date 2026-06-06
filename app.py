# app.py
from core.chains import RAGAssistantChain  # <-- IMPORT CLASS RAG MỚI

def main():
    print("=== BOT ĐỌC TÀI LIỆU (RAG) BẮT ĐẦU ===")
    print("[Hệ thống] Đang kết nối với cơ sở dữ liệu Vector...")
    
    try:
        # Khởi tạo trợ lý RAG (Nó sẽ tự tải dữ liệu từ thư mục vector_db lên)
        assistant = RAGAssistantChain()
        print("[Hệ thống] Sẵn sàng! Gõ 'exit', 'quit' hoặc 'thoat' để dừng.")
    except Exception as e:
        print(f"[Lỗi hệ thống] Không thể tải Vector DB: {str(e)}")
        return

    while True:
        try:
            user_input = input("\nBạn hỏi: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Hệ thống] Đã thoát.") 
            break

        if not user_input: 
            continue

        if user_input.lower() in {"exit", "quit", "thoat"}:
            print("[Hệ thống] Tạm biệt.")
            break

        print("Trợ lý đang đọc tài liệu và trả lời... ")
        result = assistant.run(user_input)
        print(f"\nTrợ lý: {result}")

if __name__ == "__main__":
    main()