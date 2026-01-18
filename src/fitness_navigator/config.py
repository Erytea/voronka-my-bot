"""
Конфигурация бота и приложения
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    bot_token: Optional[str] = Field(default=None, env="BOT_TOKEN")
    database_url: str = Field(default="sqlite://./db.sqlite3", env="DATABASE_URL")
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file_ignore_empty=True
    )


settings = Settings()
