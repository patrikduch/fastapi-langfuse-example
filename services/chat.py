from core.config import settings
from schemas.chat import ChatRequest, ChatResponse
from services.langfuse import LangfuseService
from services.llm import complete_chat


class ChatError(Exception):
    def __init__(self, message: str, *, model: str, trace_url: str | None = None):
        super().__init__(message)
        self.model = model
        self.trace_url = trace_url


class ChatService:
    @staticmethod
    def openai_configured() -> bool:
        key = settings.openai_api_key
        return bool(key) and not key.startswith("sk-your-")

    @staticmethod
    async def chat(body: ChatRequest) -> ChatResponse:
        model = body.model or settings.openai_model
        with LangfuseService.trace_chat(
            name="chat-request",
            user_id=body.user_id,
            session_id=body.session_id,
            tags=body.tags,
            metadata={"model": model, "source": "fastapi"},
        ) as trace:
            try:
                reply = await complete_chat(
                    messages=body.messages,
                    model=model,
                    temperature=body.temperature,
                    callbacks=trace.callbacks,
                )
            except Exception as exc:
                LangfuseService.mark_error(exc, model=model, tags=body.tags)
                raise ChatError(
                    str(exc),
                    model=model,
                    trace_url=LangfuseService.public_trace_url(),
                ) from exc

            LangfuseService.mark_success(output={"reply": reply, "model": model})
            return ChatResponse(
                reply=reply,
                model=model,
                trace_url=LangfuseService.public_trace_url(),
            )
