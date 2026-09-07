from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

load_dotenv(Path(__file__).resolve().parent / ".env")

from controllers import chat_controller, health_controller
from services import LangfuseService

LangfuseService.disable_langsmith()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    LangfuseService.flush()
    LangfuseService.shutdown()


app = FastAPI(
    title="OpenAI + Langfuse FastAPI",
    description="Calls OpenAI through LangChain and sends traces to local Langfuse, not LangSmith.",
    lifespan=lifespan,
)

app.include_router(health_controller)
app.include_router(chat_controller)


@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError):
    LangfuseService.record_validation_error(
        path=str(request.url.path),
        method=request.method,
        errors=exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
