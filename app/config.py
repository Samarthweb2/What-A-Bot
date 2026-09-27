"""
Environment/config loading. See .env.example for every variable this
project needs. No business logic here -- Section C/G reference these
values, don't hardcode them elsewhere.
"""
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    telegram_bot_token: str
    telegram_webhook_secret: str
    send_mode: str = "real"

    model_provider: str = ""
    model_api_key: str = ""
    model_name: str = ""
    model_fallback_name: str = ""

    n8n_webhook_url: str = ""
    n8n_shared_secret: str = ""

    owner_page_token: str = ""

    default_review_above_paise: int = 100_000
    healthcheck_path: str = "/health"

    class Config:
        env_file = ".env"


settings = Settings()
