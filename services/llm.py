from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.config import settings
from schemas.chat import ChatMessage


def _to_langchain(messages: list[ChatMessage]) -> list:
    mapping = {
        "system": SystemMessage,
        "user": HumanMessage,
        "assistant": AIMessage,
    }
    return [mapping[message.role](content=message.content) for message in messages]


def build_llm(model: str, temperature: float, *, timeout: float | None = None) -> ChatOpenAI:
    kwargs: dict = {
        "model": model,
        "temperature": temperature,
        "api_key": settings.openai_api_key,
        "max_retries": 0 if timeout is not None else 2,
    }
    if timeout is not None:
        kwargs["timeout"] = timeout
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return ChatOpenAI(**kwargs)


async def complete_chat(
    messages: list[ChatMessage],
    model: str,
    temperature: float,
    callbacks: list | None = None,
) -> str:
    if model == "force-error":
        raise RuntimeError("Simulated application failure for Langfuse error traces")

    timeout = 0.001 if model == "force-timeout" else None
    llm = build_llm(model=model, temperature=temperature, timeout=timeout)
    result = await llm.ainvoke(
        _to_langchain(messages),
        config={"callbacks": callbacks or [], "run_name": "openai-chat"},
    )
    return result.content if isinstance(result.content, str) else str(result.content)
