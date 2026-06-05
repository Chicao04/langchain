# core/loaders.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from typing import List
import os

def load_pdf_document(file_path: str) -> List[Document]:
    """
    Hàm đọc file PDF và trả về danh sách các Document (mỗi trang là một Document).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file tại đường dẫn: {file_path}")
        
    try:
        # Khởi tạo PyPDFLoader với đường dẫn file
        loader = PyPDFLoader(file_path)
        
        # Hàm load() sẽ đọc toàn bộ các trang và chuyển thành List[Document]
        pages = loader.load()
        
        print(f"[INFO] Đã đọc thành công file: {os.path.basename(file_path)}")
        print(f"[INFO] Tổng số trang: {len(pages)}")
        
        return pages
    except Exception as e:
        print(f"[ERROR] Có lỗi xảy ra khi đọc file PDF: {str(e)}")
        return []

# Đoạn code này dùng để bạn chạy thử nghiệm (test local) độc lập file này
if __name__ == "__main__":
    # Giả sử bạn tạo 1 thư mục data/ chứa file test.pdf
    test_file = "data/test.pdf" 
    
    # Tạo file giả lập nếu chưa có để test không bị lỗi
    if os.path.exists(test_file):
        docs = load_pdf_document(test_file)
        if docs:
            # In thử nội dung trang đầu tiên để kiểm tra
            print("\n--- Demo nội dung trang 1 ---")
            print(docs[0].page_content[:500]) # Lấy 500 ký tự đầu tiên
            print("\n--- Demo Metadata trang 1 ---")
            print(docs[0].metadata)