"""xkcd.com official JSON endpoints only (no HTML scraping)."""

from __future__ import annotations

import base64
import random
from typing import Any

import httpx

_BASE = "https://xkcd.com"
_UA = "xkcd-mcp/0.1 (+https://github.com/sandraschi/xkcd-mcp)"


def _comic_dict(data: dict[str, Any]) -> dict[str, Any]:
    num = int(data["num"])
    return {
        "num": num,
        "month": data.get("month"),
        "year": data.get("year"),
        "day": data.get("day"),
        "title": data.get("title"),
        "safe_title": data.get("safe_title"),
        "alt": data.get("alt"),
        "img": data.get("img"),
        "transcript": data.get("transcript"),
        "link": data.get("link") or "",
        "news": data.get("news") or "",
        "xkcd_url": f"{_BASE}/{num}/",
        "explainxkcd_url": f"https://www.explainxkcd.com/wiki/index.php/{num}",
        "json_source": f"{_BASE}/{num}/info.0.json",
    }


async def fetch_current() -> dict[str, Any]:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(20.0),
        headers={"User-Agent": _UA},
    ) as client:
        r = await client.get(f"{_BASE}/info.0.json")
    r.raise_for_status()
    data = r.json()
    return {"success": True, "comic": _comic_dict(data)}


async def fetch_by_number(num: int) -> dict[str, Any]:
    if num < 1:
        return {"success": False, "error": "comic_number must be >= 1"}
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(20.0),
        headers={"User-Agent": _UA},
    ) as client:
        r = await client.get(f"{_BASE}/{num}/info.0.json")
    if r.status_code == 404:
        return {"success": False, "error": f"No comic #{num} (404)."}
    r.raise_for_status()
    data = r.json()
    return {"success": True, "comic": _comic_dict(data)}


async def fetch_random() -> dict[str, Any]:
    cur = await fetch_current()
    if not cur.get("success"):
        return cur
    n = int(cur["comic"]["num"])
    if n < 1:
        return {"success": False, "error": "Could not determine latest comic number."}
    pick = random.randint(1, n)
    return await fetch_by_number(pick)


async def fetch_image_data_uri(url: str) -> str | None:
    """Fetch image from URL and return as base64 data URI (capped at 512KB)."""
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(20.0),
            headers={"User-Agent": _UA},
        ) as client:
            # Use stream=True and a byte limit to prevent huge payloads
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "image/png")
                chunks = []
                bytes_received = 0
                max_bytes = 512 * 1024  # 512 KB SOTA cap
                
                async for chunk in response.aiter_bytes():
                    bytes_received += len(chunk)
                    if bytes_received > max_bytes:
                        # Too big; abort
                        return None
                    chunks.append(chunk)
                
                image_data = b"".join(chunks)
                b64_data = base64.b64encode(image_data).decode("utf-8")
                return f"data:{content_type};base64,{b64_data}"
    except Exception:
        return None
