from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float = 0.2
    user_id: str | None = None
    session_id: str | None = None
    tags: list[str] = Field(default_factory=lambda: ["fastapi", "openai"])


class ChatResponse(BaseModel):
    reply: str
    model: str
    trace_url: str | None = None
