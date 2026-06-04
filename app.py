# app.py
from core.chains import MiniAssistantChain

def main():
    print("=== MINI ASSISTANT BẮT ĐẦU ===")
    print("Gõ 'exit', 'quit' hoặc 'thoat' để dừng.")
    
    assistant = MiniAssistantChain()

    while True:
        try:
            user_input = input("Bạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[Hệ thống] đã thoát.") 
            break

        if not user_input: 
            continue

        if user_input.lower() in {"exit", "quit", "thoat"}:
            print("[Hệ thống] Tạm biệt.")
            break

        print("Trợ lý: ", end="")
        result = assistant.run(user_input)
        print(result)

if __name__ == "__main__":
    main()