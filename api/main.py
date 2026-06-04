from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.chains import MiniAssistantChain


class ChatRequest(BaseModel):
    user_input: str = Field(..., min_length=1, description="Câu hỏi của người dùng")
    context: str = Field(default="", description="Bối cảnh bổ sung nếu có")


class ChatResponse(BaseModel):
    answer: str


app = FastAPI(title="Mini Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = MiniAssistantChain()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = assistant.run(request.user_input, request.context)
        return ChatResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
