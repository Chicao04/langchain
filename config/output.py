from collections.abc import Mapping, Sequence
from typing import Any


class OutputConfig:
    assistant_label = "Trợ lý"
    fallback_message = "Xin lỗi, mình chưa tạo được câu trả lời."

    @staticmethod
    def normalize(value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        if hasattr(value, "content"):
            return OutputConfig.normalize(getattr(value, "content"))

        if isinstance(value, Mapping):
            for key in ("text", "content", "answer", "output", "message"):
                item = value.get(key)
                if item:
                    return OutputConfig.normalize(item)
            return str(value).strip()

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            parts = [OutputConfig.normalize(item) for item in value]
            parts = [part for part in parts if part]
            return "\n".join(parts).strip()

        return str(value).strip()

    @staticmethod
    def format_assistant_text(value: Any) -> str:
        text = OutputConfig.normalize(value)
        return text if text else OutputConfig.fallback_message