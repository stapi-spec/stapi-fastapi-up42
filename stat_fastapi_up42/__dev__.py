#!/usr/bin/env python3

from sys import stderr

from fastapi import FastAPI

try:
    from pydantic_settings import BaseSettings
    from uvicorn.main import run
except ImportError:
    print("install uvicorn and pydantic-settings to use the dev server", file=stderr)
    exit(1)

from stat_fastapi.api import StatApiRouter

from stat_fastapi_up42 import StatUp42Backend


class DevSettings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"


app = FastAPI(debug=True)
app.include_router(StatApiRouter(backend=StatUp42Backend()).router)


def cli():
    settings = DevSettings()
    run(
        "stat_fastapi_up42.__dev__:app",
        reload=True,
        host=settings.host,
        port=settings.port,
    )
