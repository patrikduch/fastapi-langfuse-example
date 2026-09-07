from fastapi import APIRouter, HTTPException

from schemas.chat import ChatRequest, ChatResponse
from services import ChatError, ChatService

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    if not ChatService.openai_configured():
        raise HTTPException(
            status_code=503,
            detail="Set OPENAI_API_KEY in .env, then recreate the api container.",
        )
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")
    try:
        return await ChatService.chat(body)
    except ChatError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": str(exc),
                "model": exc.model,
                "trace_url": exc.trace_url,
            },
        ) from exc
