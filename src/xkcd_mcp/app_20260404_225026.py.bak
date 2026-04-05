"""FastAPI + MCP HTTP."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI
from pydantic import BaseModel

from xkcd_mcp.config import load_settings
from xkcd_mcp.server import mcp
from xkcd_mcp.xkcd_api import fetch_by_number, fetch_current, fetch_random

mcp_http = mcp.http_app(path="/mcp")


class ComicBody(BaseModel):
    operation: Literal["current", "by_number", "random"]
    comic_number: int | None = None


def build_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title="xkcd-mcp",
        version="0.2.0",
        lifespan=mcp_http.lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "ok": True,
            "service": "xkcd-mcp",
            "port": settings.port,
            "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
        }

    @app.get("/")
    async def root() -> dict[str, Any]:
        return {
            "service": "xkcd-mcp",
            "version": "0.2.0",
            "docs": f"http://{settings.host}:{settings.port}/docs",
            "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
            "webapp": "http://127.0.0.1:10779",
        }

    @app.post("/api/comic")
    async def api_comic(body: ComicBody) -> dict[str, Any]:
        op = body.operation
        if op == "current":
            return await fetch_current()
        if op == "random":
            return await fetch_random()
        if op == "by_number":
            if body.comic_number is None:
                return {"success": False, "error": "comic_number required"}
            return await fetch_by_number(body.comic_number)
        return {"success": False, "error": "bad operation"}

    path = settings.mcp_http_path.strip() or "/mcp"
    app.mount(path, mcp_http)

    return app


app = build_app()
