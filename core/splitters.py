# core/splitters.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Hàm chia nhỏ các Document lớn thành các đoạn (chunks) nhỏ hơn.
    - chunk_size: Độ dài tối đa của mỗi đoạn (tính theo ký tự).
    - chunk_overlap: Đoạn gối đầu giữa 2 đoạn liên tiếp để tránh mất ngữ cảnh ở ranh giới cắt.
    """
    # Khởi tạo bộ chia thông minh. 
    # Các ký tự separators giúp nó ưu tiên cắt ở hàng trống, dấu chấm, dấu phẩy rồi mới đến khoảng trắng.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Thêm ". " và ", " vào danh sách ưu tiên cắt sau dấu xuống dòng
        separators=["\n\n", "\n", ". ", ", ", " ", ""] 
    )
    
    # Tiến hành chia nhỏ tài liệu
    chunks = text_splitter.split_documents(documents)
    
    print(f"[INFO] Đã chia {len(documents)} trang gốc thành {len(chunks)} đoạn nhỏ (chunks).")
    return chunks