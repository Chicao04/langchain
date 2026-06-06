import os
import sys
import json
import re
import glob
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# =====================================================================
# 0. CƠ CHẾ ĐỊNH VỊ ĐƯỜNG DẪN GỐC TỰ ĐỘNG (FIX LỖI PATH MODULE)
# =====================================================================
THU_MUC_HIEN_TAI = os.path.dirname(os.path.abspath(__file__))
THU_MUC_GOC_DU_AN = os.path.dirname(THU_MUC_HIEN_TAI)

if THU_MUC_GOC_DU_AN not in sys.path:
    sys.path.insert(0, THU_MUC_GOC_DU_AN)

# Tiến hành import module cấu hình AI chung một cách an toàn
from config.settings import AIConfig 

# =====================================================================
# KHỐI CẤU HÌNH HỆ THỐNG (BẠN CHỈ CẦN CHỈNH SỬA TẠI ĐÂY)
# =====================================================================
CONFIG = {
    # ĐƯỜNG DẪN THƯ MỤC ĐẦU VÀO: Nơi chứa các file bảng thô (*_bang_raw.txt) vừa được trích xuất ra
    "INPUT_DIR_PATH": os.path.join(THU_MUC_GOC_DU_AN, "output_data", "extract_transform_data_output"),
    
    # ĐƯỜNG DẪN THƯ MỤC ĐẦU RA: Nơi bạn muốn lưu trữ các file tri thức JSON cuối cùng
    "OUTPUT_DIR_PATH": os.path.join(THU_MUC_GOC_DU_AN, "output_data", "extract_transform_data_output"),
    
    # Tên mô hình Gemini sử dụng để phân tích cấu trúc dữ liệu bảng động
    "MODEL_NAME": "gemini-3.1-flash-lite",
    "TEMPERATURE": 0.1
}

# Tự động đảm bảo thư mục đầu ra tồn tại
os.makedirs(CONFIG["OUTPUT_DIR_PATH"], exist_ok=True)


# =====================================================================
# 1. THIẾT KẾ PYDANTIC SCHEMA ĐỂ ÉP KIỂU DỮ LIỆU ĐẦU RA (STRUCTURED OUTPUT)
# =====================================================================
class ChunkTriThuc(BaseModel):
    text_description: str = Field(
        description="Đoạn văn xuôi tự nhiên hoàn chỉnh, logic diễn giải toàn bộ con số, ngữ cảnh xuất hiện của dòng dữ liệu trong bảng để làm đầu vào tối ưu cho Vector Search RAG."
    )
    metadata: Dict[str, Any] = Field(
        description="Bảng ánh xạ chứa các trường dữ liệu thô lọc được từ dòng (ví dụ: ngành học, mã ngành, chỉ tiêu, điểm chuẩn, năm học) để phân loại."
    )

class DanhSachTriThuc(BaseModel):
    items: List[ChunkTriThuc] = Field(description="Danh sách tập hợp toàn bộ các chunk tri thức bóc tách từ phân đoạn.")


# =====================================================================
# 2. BỘ ĐIỀU PHỐI TỰ ĐỘNG PHÂN TÍCH BẢNG ĐỘNG BẰNG AI AGENT
# =====================================================================
class KnowledgeGraphBuilder:
    """Lớp điều phối xử lý logic chuyển đổi cấu trúc bảng Markdown sang tri thức AI."""

    @staticmethod
    def parse_table_via_gemini(table_text: str, llm_client) -> List[dict]:
        """Gửi dữ liệu bảng thô qua Gemini để tự nhận diện cột và chuyển đổi định dạng."""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "Bạn là một chuyên gia cao cấp chịu trách nhiệm chuẩn hóa dữ liệu RAG cho Chatbot Tuyển sinh.\n"
                "Nhiệm vụ của bạn là đọc và hiểu phân đoạn bảng Markdown thô, tự động nhận diện ý nghĩa bản chất của các cột "
                "(Ví dụ: cột nào chứa tên ngành học, mã số đào tạo, các chỉ tiêu và điểm trúng tuyển qua các năm).\n\n"
                "Sau đó duyệt qua từng hàng dữ liệu để chuyển dịch thành cấu trúc JSON chuẩn bao gồm:\n"
                "1. 'text_description': Chuỗi văn tự nhiên sâu sắc, không viết tắt, diễn đạt rõ nét toàn bộ số liệu của hàng đó để AI Embedding dễ tìm kiếm ngữ nghĩa.\n"
                "2. 'metadata': Tập hợp các key-value chứa từ khóa thô phục vụ chức năng lọc dữ liệu cứng.\n\n"
                "YÊU CẦU BẮT BUỘC:\n"
                "- KHÔNG ĐƯỢC thêm bớt hay suy đoán các con số không có thật trong bảng.\n"
                "- Tự động bỏ qua các dòng mang tính chất tiêu đề phụ lặp lại hoặc các hàng cộng 'Tổng'."
            )),
            ("user", "Dưới đây là nội dung phân đoạn bảng thô cần phân tích:\n\n{table_content}")
        ])

        # Kích hoạt tính năng ép kiểu đầu ra có cấu trúc (Structured Output) theo cấu hình Gemini
        structured_llm = llm_client.with_structured_output(DanhSachTriThuc)
        knowledge_chain = prompt_template | structured_llm
        
        try:
            response = knowledge_chain.invoke({ "table_content": table_text })
            return [item.model_dump() for item in response.items]
        except Exception as e:
            print(f"  [!] Gặp sự cố trong quá trình xử lý qua Gemini: {e}")
            return []

    @classmethod
    def build_knowledge_pipeline(cls):
        """Chu trình quét thư mục, đọc các file bảng thô và tạo tri thức JSON hàng loạt."""
        input_dir = CONFIG["INPUT_DIR_PATH"]
        
        if not os.path.exists(input_dir):
            print(f"[Lỗi] Thư mục chứa dữ liệu bảng thô không tồn tại: {input_dir}")
            return

        # Tìm tất cả các file có mẫu tên dạng '*_bang_raw.txt' trong thư mục đầu vào
        raw_table_files = glob.glob(os.path.join(input_dir, "*_bang_raw.txt"))
        
        if not raw_table_files:
            print(f"[Thông báo] Không tìm thấy file bảng thô '*_bang_raw.txt' nào tại: {input_dir}")
            return

        print(f"[*] Tìm thấy {len(raw_table_files)} file bảng thô cần nạp tri thức AI.")
        print("=" * 60)

        # Khởi tạo model Gemini động, sử dụng cơ chế cấu hình từ hệ thống settings của bạn
        gemini_model = AIConfig.get_gemini_model(
            model_name=CONFIG["MODEL_NAME"], 
            temperature=CONFIG["TEMPERATURE"]
        )

        # Vòng lặp xử lý hàng loạt từng file bảng thô
        for file_idx, file_path in enumerate(raw_table_files, start=1):
            filename = os.path.basename(file_path)
            # Tách chuỗi để lấy lại tên gốc của file tài liệu (ví dụ: 'KMA_De-an-TS-2025' từ 'KMA_De-an-TS-2025_bang_raw.txt')
            base_filename = filename.replace("_bang_raw.txt", "")
            
            print(f"\n[{file_idx}/{len(raw_table_files)}] AI đang xử lý bảng thô của tài liệu: {base_filename}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Phân mảnh tệp tin dựa trên ký hiệu đánh dấu phân tách các bảng
            table_chunks = re.split(r'--- BẢNG SỐ \d+ ---', content)
            tri_thuc_file_final = []

            for idx, chunk in enumerate(table_chunks):
                if "|" not in chunk.strip():
                    continue # Bỏ qua các phân đoạn text không có lưới bảng Markdown
                    
                print(f"   -> Đang điều phối Gemini phân tích cấu trúc động Bảng đoạn số {idx}...")
                processed_chunks = cls.parse_table_via_gemini(chunk, gemini_model)
                
                # Gán nhãn metadata truy vết dựa trên chính tên file gốc vừa bóc tách
                for item in processed_chunks:
                    item["metadata"]["source_document"] = base_filename
                    tri_thuc_file_final.append(item)

            # Xuất cơ sở tri thức JSON tương ứng cho từng file tài liệu vào thư mục đầu ra
            output_json_name = f"{base_filename}_tri_thuc.json"
            duong_dan_json_output = os.path.join(CONFIG["OUTPUT_DIR_PATH"], output_json_name)
            
            with open(duong_dan_json_output, "w", encoding="utf-8") as f:
                json.dump(tri_thuc_file_final, f, ensure_ascii=False, indent=4)
                
            print(f"  -> Tệp tri thức cấu trúc được xuất thành công: '{output_json_name}' ({len(tri_thuc_file_final)} chunks)")

        print("\n" + "=" * 60 + "\n[HOÀN TẤT] Hệ thống Agent AI đã tự động xây dựng xong toàn bộ cơ sở tri thức.\n" + "=" * 60)


if __name__ == "__main__":
    KnowledgeGraphBuilder.build_knowledge_pipeline()