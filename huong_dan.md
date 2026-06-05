learn-langchain/
│
├── .env                  # Lưu API Key, ví dụ: GOOGLE_API_KEY=...
├── .gitignore            # Chặn commit .env và file tạm
├── requirements.txt      # Danh sách thư viện cần cài
├── api/                  # FastAPI backend cho trợ lý mini
│   └── main.py           # Tạo endpoint /chat và /health
│
├── config/               # Cấu hình hệ thống
│   └── settings.py       # Khởi tạo model, cấu hình tham số LLM
│
├── core/                 # Logic chính của AI
│   ├── prompts.py        # Quản lý prompt cho trợ lý và bản phân tích
│   └── chains.py         # Nơi nối Prompt + LLM thành chuỗi xử lý
│
└── app.py                # File chạy chính (trợ lý mini dạng chat)

## Mục tiêu hiện tại

Project này đang được dùng như một "mini assistant" bằng LangChain + Gemini. Ý tưởng là:

- Người dùng nhập câu hỏi ở terminal.
- `app.py` nhận input và gửi vào chain trong `core/chains.py`.
- `core/prompts.py` giữ prompt hệ thống cho trợ lý.
- `config/settings.py` tạo model Gemini từ biến môi trường.

## Cách dùng nhanh

1. Đảm bảo `.env` có API key của Google Gemini:

```env
GOOGLE_API_KEY=your_api_key_here
```

2. Cài thư viện:

```bash
pip install -r requirements.txt
```

3. Chạy chương trình:

```bash
python app.py
```

4. Gõ câu hỏi trực tiếp trong terminal. Có thể thoát bằng `exit`, `quit` hoặc `thoat`.

## Ý nghĩa các file chính

- `config/settings.py`: nơi tạo `ChatGoogleGenerativeAI`.
- `core/prompts.py`: nơi định nghĩa prompt cho trợ lý mini.
- `core/chains.py`: nơi ghép prompt và model để xử lý input.
- `app.py`: vòng lặp hỏi đáp trong terminal.
- `api/main.py`: backend FastAPI để gọi trợ lý qua HTTP.
- `core/loaders.py`: nơi đọc các file docs/pdf ra số kiểu như scan 
- `core/splitters.py`: Chia nhỏ văn bản (Text Splitting)

## Ghi chú thêm

- `ITAnalyzerChain` vẫn được giữ lại như một lớp tương thích ngược, nhưng luồng chính hiện tại là `MiniAssistantChain`.
- Nếu sau này muốn mở rộng, có thể thêm memory, tool calling, hoặc tách riêng các chế độ như chat, phân tích log, tra cứu tài liệu.

## Chạy FastAPI

1. Cài thêm FastAPI và Uvicorn nếu chưa có:

```bash
pip install -r requirements.txt
```

2. Chạy server:

```bash
uvicorn api.main:app --reload
```

3. Kiểm tra server:

```bash
curl http://127.0.0.1:8000/health
```

4. Gửi câu hỏi tới `/chat`:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
	-H "Content-Type: application/json" \
	-d "{\"user_input\": \"Hãy chào tôi bằng tiếng Việt\"}"
```

Nếu bạn dùng Postman hoặc frontend, body JSON có thể như sau:

```json
{
	"user_input": "Hãy tóm tắt dự án này",
	"context": "Người dùng đang học LangChain"
}
```