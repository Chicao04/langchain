# app.py
from core.loaders import load_pdf_document
from core.splitters import split_documents  # <-- THÊM DÒNG NÀY

def main():
    pdf_path = "data/Ngành Điện Tự Động Hóa.pdf"
    
    # 1. Đọc dữ liệu từ PDF
    raw_documents = load_pdf_document(pdf_path)
    if not raw_documents:
        print("Không có dữ liệu để xử lý.")
        return

    # 2. Chia nhỏ tài liệu (BƯỚC MỚI)
    print("\n" + "="*20 + " ĐANG TIẾN HÀNH CHIA NHỎ VĂN BẢN " + "="*20)
    chunks = split_documents(raw_documents, chunk_size=800, chunk_overlap=150)
    
    # In thử 2 đoạn (chunk) đầu tiên sau khi cắt để bạn xem sự khác biệt
    print("\n" + "-"*20 + " HIỂN THỊ CHUNK THỬ NGHIỆM " + "-"*20)
    for i in range(min(2, len(chunks))):
        print(f"\n[CHUNK THỨ {i+1}] - Nguồn: trang {chunks[i].metadata.get('page') + 1}")
        print(f"Độ dài: {len(chunks[i].page_content)} ký tự")
        print("Nội dung đoạn:")
        print(chunks[i].page_content)
        print("-" * 40)
    
    print("="*65 + "\n")

    # 3. Bước tiếp theo (Phác thảo bước kế tiếp):
    # Đẩy các 'chunks' này vào Vector DB bằng thư viện langchain-chroma
    # save_to_vector_db(chunks)

if __name__ == "__main__":
    main()