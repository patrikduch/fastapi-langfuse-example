from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from core.config import settings


@dataclass
class ChatTrace:
    callbacks: list = field(default_factory=list)


class LangfuseService:
    """Langfuse SDK facade. No instance state; the SDK client is already a singleton."""

    @staticmethod
    def disable_langsmith() -> None:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ.pop("LANGCHAIN_API_KEY", None)
        os.environ.pop("LANGSMITH_API_KEY", None)

    @staticmethod
    def client():
        return get_client()

    @staticmethod
    def auth_ok() -> bool:
        return bool(LangfuseService.client().auth_check())

    @staticmethod
    def public_base_url() -> str:
        return settings.langfuse_public_url.rstrip("/")

    @staticmethod
    def public_trace_url() -> str | None:
        trace_id = LangfuseService.client().get_current_trace_id()
        if not trace_id:
            return None
        return f"{LangfuseService.public_base_url()}/trace/{trace_id}"

    @staticmethod
    @contextmanager
    def trace_chat(
        *,
        name: str = "chat-request",
        user_id: str | None = None,
        session_id: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[ChatTrace]:
        attrs: dict[str, Any] = {
            "tags": tags or [],
            "metadata": metadata or {},
        }
        if user_id:
            attrs["user_id"] = user_id
        if session_id:
            attrs["session_id"] = session_id

        langfuse = LangfuseService.client()
        with langfuse.start_as_current_observation(as_type="span", name=name):
            with propagate_attributes(**attrs):
                yield ChatTrace(callbacks=[CallbackHandler()])

    @staticmethod
    def mark_success(*, output: dict[str, Any]) -> None:
        LangfuseService.client().update_current_span(output=output)

    @staticmethod
    def mark_error(
        exc: Exception,
        *,
        model: str,
        tags: list[str] | None = None,
    ) -> None:
        error_tags = list(dict.fromkeys([*(tags or []), "error", type(exc).__name__]))
        langfuse = LangfuseService.client()
        with propagate_attributes(
            tags=error_tags,
            metadata={"error": True, "model": model, "source": "fastapi"},
        ):
            langfuse.update_current_span(
                name="chat-request-error",
                level="ERROR",
                status_message=str(exc),
                output={"error": type(exc).__name__, "message": str(exc), "model": model},
            )
            langfuse.score_current_trace(
                name="success",
                value=0,
                data_type="BOOLEAN",
                comment=str(exc)[:240],
            )
        langfuse.flush()

    @staticmethod
    def record_validation_error(*, path: str, method: str, errors: list) -> None:
        langfuse = LangfuseService.client()
        with langfuse.start_as_current_observation(as_type="span", name="http-validation-error") as span:
            span.update(
                level="ERROR",
                input={"path": path, "method": method},
                output={"errors": errors},
                status_message="Request validation failed",
                metadata={"source": "fastapi", "status": 422},
            )
            langfuse.score_current_trace(
                name="success",
                value=0,
                data_type="BOOLEAN",
                comment="HTTP 422 validation error",
            )
        langfuse.flush()

    @staticmethod
    def flush() -> None:
        LangfuseService.client().flush()

    @staticmethod
    def shutdown() -> None:
        LangfuseService.client().shutdown()
