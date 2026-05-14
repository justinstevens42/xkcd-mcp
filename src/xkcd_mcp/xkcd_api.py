"""xkcd official JSON API + explainxkcd MediaWiki search."""

from __future__ import annotations

import random
import re
from typing import Any

import httpx

_BASE = "https://xkcd.com"
_EXPLAIN = "https://www.explainxkcd.com/wiki/api.php"
_UA = "xkcd-mcp/0.4 (+https://github.com/justinstevens42/xkcd-mcp)"
_TIMEOUT = httpx.Timeout(20.0)


def _comic(data: dict[str, Any]) -> dict[str, Any]:
    num = int(data["num"])
    return {
        "num": num,
        "title": data.get("title"),
        "alt": data.get("alt"),
        "img": data.get("img"),
        "year": data.get("year"),
        "month": data.get("month"),
        "day": data.get("day"),
        "transcript": data.get("transcript") or "",
        "xkcd_url": f"{_BASE}/{num}/",
        "explainxkcd_url": f"https://www.explainxkcd.com/wiki/index.php/{num}",
    }


async def _get_json(url: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": _UA}) as client:
        r = await client.get(url)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


async def fetch_current() -> dict[str, Any]:
    data = await _get_json(f"{_BASE}/info.0.json")
    return _comic(data)


async def fetch_by_number(num: int) -> dict[str, Any] | None:
    if num < 1:
        return None
    data = await _get_json(f"{_BASE}/{num}/info.0.json")
    return _comic(data) if data else None


async def fetch_random() -> dict[str, Any]:
    latest = await fetch_current()
    pick = random.randint(1, latest["num"])
    return await fetch_by_number(pick) or latest


async def search_explainxkcd(query: str, limit: int = 5) -> list[int]:
    """Search explainxkcd via MediaWiki API; return comic numbers parsed from page titles."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "srwhat": "text",
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": _UA}) as client:
        r = await client.get(_EXPLAIN, params=params)
    r.raise_for_status()
    results = r.json().get("query", {}).get("search", [])

    pattern = re.compile(r"^(\d+):")
    nums: list[int] = []
    for item in results:
        m = pattern.search(item.get("title", ""))
        if m:
            nums.append(int(m.group(1)))
    return nums
