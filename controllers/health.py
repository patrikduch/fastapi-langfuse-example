from fastapi import APIRouter

from services import ChatService, LangfuseService

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "ok": True,
        "langfuse_base_url": LangfuseService.public_base_url(),
        "langfuse_auth": LangfuseService.auth_ok(),
        "langsmith_disabled": True,
        "openai_configured": ChatService.openai_configured(),
    }
