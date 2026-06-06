# core/knowledge.py
import os
from dotenv import load_dotenv

load_dotenv()

# Sử dụng giải pháp kết hợp chuẩn hóa để tránh lỗi Import trên các phiên bản LangChain khác nhau
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class KnowledgeBase:
    def __init__(self, data_dir: str = "data", persist_dir: str = "vector_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        
        # Sử dụng mô hình local BAAI (Chạy hoàn toàn trên máy của bạn)
        print("[*] Đang khởi tạo mô hình nhúng local (BAAI/bge-small-en-v1.5)...")
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
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

        # 4. Tạo Vector và lưu trực tiếp vào ChromaDB local
        print("[*] Đang tiến hành xử lý Vector hóa (Embedding) trực tiếp trên CPU...")
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print(f"[OK] Đã lưu dữ liệu Vector thành công vào thư mục '{self.persist_dir}'!")

    def get_retriever(self):
        """Hàm lấy bộ truy xuất dữ liệu sau này dùng cho Chain"""
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        return self.vector_store.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    kb = KnowledgeBase()
    kb.load_and_index_documents()