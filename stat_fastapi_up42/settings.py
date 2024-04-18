from enum import Enum
from logging import basicConfig

from pydantic_settings import BaseSettings


class LogLevel(Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class Settings(BaseSettings):
    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"

    TOKEN: str | None = None
    BASE_URL = "https://api.up42.com"

    @classmethod
    def load(cls) -> "Settings":
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
