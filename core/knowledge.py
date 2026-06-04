# core/knowledge.py
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
    from langchain_community.document_loaders.word_document import Docx2txtLoader
except ImportError:
    from langchain.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, Docx2txtLoader

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
except ImportError:
    from langchain.vectorstores import Chroma

class KnowledgeBase:
    def __init__(self, data_dir: str = "data", persist_dir: str = "vector_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        
        # Sử dụng Google Embeddings (Cần GOOGLE_API_KEY trong .env giống config/settings.py)
        # Khởi tạo embedding model tương thích với tài khoản Gemini của bạn
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
        self.vector_store = None

    def load_and_index_documents(self):
        """Bước 1 & 2: Đọc file PDF/Word và nạp vào thư viện"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"[*] Đã tạo thư mục '{self.data_dir}'. Hãy bỏ các file PDF/Word vào đây.")
            return

        print("[*] Đang đọc các file tài liệu...")
        documents = []
        
        # 1. Đọc file PDF
        pdf_loader = PyPDFDirectoryLoader(self.data_dir)
        documents.extend(pdf_loader.load())
        
        # 2. Đọc file Word (.docx)
        word_loader = DirectoryLoader(self.data_dir, glob="**/*.docx", loader_cls=Docx2txtLoader)
        documents.extend(word_loader.load())

        if not documents:
            print("[!] Không tìm thấy tài liệu nào trong thư mục data/.")
            return

        print(f"[+] Đã đọc {len(documents)} trang/văn bản gốc.")

        # 3. Chia nhỏ văn bản (Text Splitting)
        # Chia mỗi đoạn khoảng 1000 ký tự, gối đầu lên nhau 200 ký tự để không mất ngữ cảnh
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f"[+] Đã chia nhỏ thành {len(chunks)} đoạn văn bản.")

        # 4. Tạo Vector và lưu vào cơ sở dữ liệu ChromaDB
        print("[*] Đang tiến hành Vector hóa (Embedding) và lưu vào DB...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print(f"[OK] Đã lưu dữ liệu Vector thành công vào thư mục '{self.persist_dir}'!")

    def get_retriever(self):
        """Hàm lấy bộ truy xuất dữ liệu sau này dùng cho Chain"""
        if not self.vector_store:
            # Nếu đã có DB lưu trên ổ đĩa, chỉ cần load lên lại
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        # Thiết lập tìm kiếm lấy ra top 3 đoạn văn bản liên quan nhất k=3
        return self.vector_store.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    # Test nhanh chạy độc lập file này để nạp dữ liệu
    kb = KnowledgeBase()
    kb.load_and_index_documents()