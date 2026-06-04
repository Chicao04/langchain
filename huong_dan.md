learn-langchain/
│
├── .env                  # Lưu API Key (Đã tạo)
├── requirements.txt      # Danh sách thư viện (Đã tạo)
│
├── config/               # Cấu hình hệ thống
│   └── settings.py       # Khởi tạo model, cấu hình tham số LLM
│
├── core/                 # Logic chính của AI
│   ├── prompts.py        # Quản lý tất cả các Prompt Templates
│   └── chains.py         # Nơi nối các Node logic (LLM + Prompt)
│
└── app.py                # File chạy chính (Giao tiếp với user/hệ thống)