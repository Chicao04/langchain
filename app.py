# app.py
from core.chains import ITAnalyzerChain

def main():
    print("=== HỆ THỐNG PHÂN TÍCH IT AGENT BẮT ĐẦU ===")
    
    # 1. Khởi tạo bộ phân tích
    analyzer = ITAnalyzerChain()
    
    # 2. Giả lập một đoạn log lỗi hoặc dữ liệu IT cần phân tích
    sample_error_log = """
    2026-06-04 15:00:12 [ERROR] Connect to Supabase database failed. 
    Reason: Connection timeout after 10000ms. 
    Target IP: 192.168.1.50:5432
    """
    
    print("\n[Hệ thống] Đang gửi dữ liệu phân tích tới Gemini...")
    
    # 3. Chạy phân tích
    result = analyzer.run(sample_error_log)
    
    print("\n=== KẾT QUẢ PHÂN TÍCH TỪ AI ===")
    print(result)
    print("=================================")

if __name__ == "__main__":
    main()