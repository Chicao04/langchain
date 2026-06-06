import os
import pdfplumber
from docx import Document
import pandas as pd

# =====================================================================
# 1. HÀM ĐỌC BẢNG TỪ FILE WORD (.docx)
# =====================================================================
def doc_bang_tu_docx(file_path):
    """Trích xuất tất cả các bảng từ file Word thành danh sách DataFrame"""
    print(f"[*] Đang đọc file Word: {file_path}")
    doc = Document(file_path)
    danh_sach_bang = []
    
    for idx, table in enumerate(doc.tables):
        data = []
        for row in table.rows:
            # Lấy text sạch của từng ô trong hàng
            text_in_row = [cell.text.strip() for cell in row.cells]
            data.append(text_in_row)
        
        if data:
            # Tạo DataFrame với dòng đầu tiên làm Tiêu đề cột (Header)
            df = pd.DataFrame(data[1:], columns=data[0])
            danh_sach_bang.append(df)
            print(f" -> Đã tìm thấy bảng số {idx+1} ({len(df)} hàng)")
            
    return danh_sach_bang

# =====================================================================
# 2. HÀM ĐỌC BẢNG TỪ FILE PDF (.pdf)
# =====================================================================
def doc_bang_tu_pdf(file_path):
    """Trích xuất tất cả các bảng từ file PDF thành danh sách DataFrame"""
    print(f"[*] Đang đọc file PDF: {file_path}")
    danh_sach_bang = []
    
    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # Tự động dò tìm cấu trúc bảng trên từng trang
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if table and len(table) > 1:
                    # Tiền xử lý: Thay thế giá trị None bằng chuỗi rỗng
                    cleaned_table = [[str(cell).strip() if cell is not None else "" for cell in row] for row in table]
                    
                    # Tạo DataFrame (Dòng đầu làm header)
                    df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                    danh_sach_bang.append(df)
                    print(f" -> Tìm thấy bảng tại Trang {page_idx+1}, Vị trí {t_idx+1} ({len(df)} hàng)")
                    
    return danh_sach_bang

# =====================================================================
# 3. HÀM LƯU DỮ LIỆU BẢNG THÔ RA FILE TXT
# =====================================================================
def luu_du_lieu_raw_thanh_txt(danh_sach_bang, output_path="du_lieu_bang_raw.txt"):
    """Lưu cấu trúc các bảng tìm được ra file .txt dưới dạng Markdown để xem thô"""
    if not danh_sach_bang:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("Không tìm thấy dữ liệu dạng bảng nào trong file tài liệu.")
        print(f"[!] Không có dữ liệu để lưu.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write("       KẾT QUẢ TRÍCH XUẤT DỮ LIỆU BẢNG THÔ       \n")
        f.write("==================================================\n\n")
        
        for idx, df in enumerate(danh_sach_bang):
            f.write(f"--- BẢNG SỐ {idx+1} ---\n")
            f.write(f"Kích thước: {df.shape[0]} hàng x {df.shape[1]} cột\n")
            f.write(f"Danh sách các cột tìm thấy: {list(df.columns)}\n\n")
            
            # Xuất bảng ra định dạng lưới Markdown trực quan vào file txt
            f.write(df.to_markdown(index=False))
            f.write("\n\n" + "-"*60 + "\n\n")
            
    print(f"\n[*] Đã lưu thành công cấu trúc toàn bộ bảng vào file: '{output_path}'")

# =====================================================================
# 4. HÀM CHÍNH ĐIỀU PHỐI HỆ THỐNG (PIPELINE)
# =====================================================================
def pipeline_doc_va_xuat_txt(file_path):
    # Kiểm tra file có tồn tại không
    if not os.path.exists(file_path):
        print(f"[Lỗi] File không tồn tại tại đường dẫn: {file_path}")
        return
        
    # Lấy đuôi file (.pdf hoặc .docx)
    _, file_extension = os.path.splitext(file_path.lower())
    danh_sach_bang = []
    
    # Rẽ nhánh xử lý theo định dạng file
    if file_extension == ".docx":
        danh_sach_bang = doc_bang_tu_docx(file_path)
    elif file_extension == ".pdf":
        danh_sach_bang = doc_bang_tu_pdf(file_path)
    else:
        print("[Lỗi] Định dạng file không được hỗ trợ. Chỉ nhận .pdf hoặc .docx")
        return

    # Lưu thẳng dữ liệu thô bóc được ra file txt
    luu_du_lieu_raw_thanh_txt(danh_sach_bang, output_path="du_lieu_bang_raw.txt")

# =====================================================================
# 5. CHẠY THỬ NGHIỆM
# =====================================================================
if __name__ == "__main__":
    # Thay đường dẫn file PDF hoặc DOCX thực tế của bạn vào đây
    duong_dan_tai_lieu = "D:\\Công việc\\learn-langchain\\read_table\\KMA_De-an-TS-2025-24.02.25_Dang-Web.pdf"
    
    pipeline_doc_va_xuat_txt(duong_dan_tai_lieu)