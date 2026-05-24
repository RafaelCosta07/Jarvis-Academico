from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list[dict[str, Any]]
    stream: bool = True


class ChatResponse(BaseModel):
    type: str
    content: str
