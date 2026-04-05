"""Starlette + MCP HTTP — no FastAPI, no Pydantic (fleet standard)."""

from __future__ import annotations

import json
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from xkcd_mcp.config import load_settings
from xkcd_mcp.server import mcp
from xkcd_mcp.xkcd_api import fetch_by_number, fetch_current, fetch_random

mcp_http = mcp.http_app(path="/mcp")


async def health(request: Request) -> JSONResponse:
    settings = load_settings()
    return JSONResponse({
        "ok": True,
        "service": "xkcd-mcp",
        "version": "0.3.0",
        "port": settings.port,
        "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
    })


async def root(request: Request) -> JSONResponse:
    settings = load_settings()
    return JSONResponse({
        "service": "xkcd-mcp",
        "version": "0.3.0",
        "docs": f"http://{settings.host}:{settings.port}/docs",
        "mcp_http": f"http://{settings.host}:{settings.port}{settings.mcp_http_path}",
        "webapp": "http://127.0.0.1:10779",
    })


async def api_comic(request: Request) -> JSONResponse:
    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "invalid JSON body"}, status_code=400)

    op = body.get("operation")
    if op == "current":
        return JSONResponse(await fetch_current())
    if op == "random":
        return JSONResponse(await fetch_random())
    if op == "by_number":
        num = body.get("comic_number")
        if num is None:
            return JSONResponse({"success": False, "error": "comic_number required"}, status_code=400)
        return JSONResponse(await fetch_by_number(int(num)))
    return JSONResponse({"success": False, "error": f"unknown operation: {op!r}"}, status_code=400)


def build_app() -> Starlette:
    settings = load_settings()
    path = settings.mcp_http_path.strip() or "/mcp"

    return Starlette(
        lifespan=mcp_http.lifespan,
        routes=[
            Route("/", root),
            Route("/health", health),
            Route("/api/comic", api_comic, methods=["POST"]),
            Mount(path, app=mcp_http),
        ],
    )


app = build_app()
