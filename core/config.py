from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_base_url: str = "http://localhost:3100"
    langfuse_public_url: str = "http://localhost:3100"


settings = Settings()
