# core/knowledge.py
import os
import time  # Thư viện quản lý delay ngắn chống nghẽn Rate Limit khi gọi API
from dotenv import load_dotenv

load_dotenv()

# Sử dụng giải pháp kết hợp chuẩn hóa để tránh lỗi Import trên các phiên bản LangChain nhau
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# ĐÃ XÓA DÒNG IMPORT HUGGINGFACE GÂY TREO MÁY TRÊN WINDOWS
# Import module Embedding chính thức để kết nối với Gemini Embedding 2 qua API
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class KnowledgeBase:
    def __init__(self, use_api: bool = False, data_dir: str = "data", persist_dir: str = "vector_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.use_api = use_api
        
        if not self.use_api:
            # Chế độ 1: Sử dụng mô hình local BAAI
            # Sử dụng giải pháp nạp động (Dynamic Import) để chỉ khi nào chọn mới tải thư viện, tránh bị treo máy ngay từ đầu
            print("[*] Đang khởi tạo mô hình nhúng local (BAAI/bge-small-en-v1.5)...")
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        else:
            # Chế độ 2: Sử dụng mô hình nhúng đám mây Gemini Embedding 2 qua API chính thức
            print("[*] Đang khởi tạo mô hình nhúng Google Gemini API (text-embedding-005)...")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="text-embedding-005",  # CHUẨN HÓA: Bỏ "models/" để tránh lỗi trùng lặp đường dẫn của SDK
                google_api_key=os.environ.get("GOOGLE_API_KEY")
            )
                        
        self.vector_store = None

    def load_and_index_documents(self):
        """Bước 1, 2 & 3: Đọc tài liệu và chia nhỏ văn bản"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"[*] Đã tạo thư mục '{self.data_dir}'. Hãy bỏ các file PDF/Word vào đây.")
            return

        print("[*] Đang đọc các file tài liệu từ thư mục data/...")
        documents = []
        
        # 1. ĐỌC FILE PDF: Dùng DirectoryLoader quét tất cả file .pdf và bóc bằng PyMuPDFLoader
        pdf_loader = DirectoryLoader(
            self.data_dir, 
            glob="**/*.pdf", 
            loader_cls=PyMuPDFLoader
        )
        documents.extend(pdf_loader.load())
        
        # 2. Đọc file Word (.docx)
        word_loader = DirectoryLoader(
            self.data_dir, 
            glob="**/*.docx", 
            loader_cls=Docx2txtLoader
        )
        documents.extend(word_loader.load())

        if not documents:
            print("[!] Không tìm thấy tài liệu nào trong thư mục data/.")
            return

        print(f"[+] Đã đọc {len(documents)} trang/văn bản gốc.")

        # 3. Chia nhỏ văn bản (Text Splitting) - TỐI ƯU CHO BẢNG BIỂU TIẾNG VIỆT
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        print(f"[+] Đã chia nhỏ thành {len(chunks)} đoạn văn bản (chunks).")

        # 4. Tạo Vector và lưu trực tiếp vào ChromaDB local theo từng chế độ chọn
        if not self.use_api:
            # Nếu dùng Local: Tiến hành xử lý dồn tất cả cùng lúc trực tiếp trên CPU
            print("[*] Đang tiến hành xử lý Vector hóa (Embedding) trực tiếp trên CPU...")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
        else:
            # Nếu dùng Gemini API: Đẩy dữ liệu theo từng nhóm (batch) thông minh để tránh lỗi cạn token
            print("[*] Đang gửi dữ liệu theo nhóm (Batch) lên Gemini API để tạo Embedding...")
            
            # Khởi tạo instance database ban đầu với chunk đầu tiên
            self.vector_store = Chroma.from_documents(
                documents=[chunks[0]],
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
            
            # Đẩy các chunk còn lại theo từng cụm (Mỗi lần gửi 20 chunks lên API)
            batch_size = 20 
            for i in range(1, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                print(f" -> Đang xử lý nhóm chunks từ {i} đến {min(i + batch_size, len(chunks))}...")
                self.vector_store.add_documents(documents=batch)
                
                # Delay 1 giây ngắn ngủi dựa theo hạn ngạch 100 RPM để reset an toàn TPM cho Google Studio
                time.sleep(1)

        print(f"[OK] Đã lưu dữ liệu Vector thành công vào thư mục '{self.persist_dir}'!")

    def get_retriever(self):
        """Hàm lấy bộ truy xuất dữ liệu sau này dùng cho Chain và Luồng Đồ thị LangGraph"""
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        return self.vector_store.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    print("=== HỆ THỐNG QUẢN LÝ VECTOR HÓA TRI THỨC ===")
    print("Chọn phương thức khởi tạo mô hình nhúng (Embedding):")
    print("1. Sử dụng mô hình Local (BAAI/bge-small-en-v1.5)")
    print("2. Sử dụng mô hình đám mây qua Gemini Embedding 2 API (text-embedding-005)")
    
    while True:
        choice = input("Lựa chọn của bạn (Nhập 1 hoặc 2): ").strip()
        if choice == "1":
            use_api = False
            break
        elif choice == "2":
            use_api = True
            break
        else:
            print("[!] Lựa chọn không hợp lệ. Vui lòng thao tác nhập lại số 1 hoặc số 2.")

    # Hiển thị cảnh báo nhắc nhở clear DB cũ tránh crash chương trình do lệch số chiều vector
    print("\n[⚠️ CẢNH BÁO QUAN TRỌNG]")
    print("Nếu bạn vừa đổi phương thức nhúng khác biệt hoàn toàn với lần chạy trước đó,")
    print(f"vui lòng xóa thủ công thư mục '{KnowledgeBase().persist_dir}' hiện tại trước khi tiếp tục.")
    confirm = input("Bạn đã dọn dẹp DB cũ (nếu có thay đổi) và sẵn sàng chạy chưa? (y/n): ").strip().lower()
    
    if confirm in {"y", "yes"}:
        kb = KnowledgeBase(use_api=use_api)
        kb.load_and_index_documents()
    else:
        print("[Hệ thống] Hủy bỏ tiến trình thực thi.")