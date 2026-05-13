"""FastMCP 3.2 — xkcd tools."""

from __future__ import annotations

import os

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult

from xkcd_mcp import xkcd_api

# Prefab UI imports with graceful fallback
try:
    from prefab_ui.app import PrefabApp
    from prefab_ui.components import (
        Card,
        CardContent,
        CardHeader,
        CardTitle,
        Div,
        Image,
        Text,
    )

    HAS_PREFAB = os.environ.get("XKCD_PREFAB_APPS", "1") != "0"
except ImportError:
    HAS_PREFAB = False

mcp = FastMCP(
    "xkcd-mcp",
    instructions=(
        "xkcd comics via the official JSON API and explainxkcd semantic search. "
        "Operations: latest, by_number, random, search(topic). Includes image URL, alt text, and explainxkcd wiki link."
    ),
)


@mcp.tool()
async def xkcd_latest() -> ToolResult:
    """Fetch the latest comic from xkcd.com."""
    try:
        res = await xkcd_api.fetch_current()
        if not res.get("success"):
            raise ToolError(f"Error: {res.get('error')}")
        return await _format_comic_result(res["comic"])
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def xkcd_get(number: int) -> ToolResult:
    """Fetch a specific xkcd comic by its number."""
    try:
        res = await xkcd_api.fetch_by_number(number)
        if not res.get("success"):
            raise ToolError(f"Error: {res.get('error')}")
        return await _format_comic_result(res["comic"])
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def xkcd_search(query: str) -> ToolResult:
    """
    Search for xkcd comics by topic (e.g., 'aliens', 'global warming').
    Uses explainxkcd semantic indexing to find relevant comic numbers.
    """
    try:
        # 1. Search explainxkcd for comic numbers
        comic_nums = await xkcd_api.search_explain_xkcd(query)
        if not comic_nums:
            return ToolResult(content=f"No xkcd comics found for topic: '{query}'")

        # 2. Fetch full metadata for each found comic
        comics = []
        for num in comic_nums:
            res = await xkcd_api.fetch_by_number(num)
            if res.get("success"):
                comics.append(res["comic"])

        if not comics:
            raise ToolError(f"Found references for '{query}', but could not fetch metadata.")

        # 3. Format result (Text + Prefab)
        text_results = [f"Found {len(comics)} comics for '{query}':"]
        for c in comics:
            text_results.append(f"- #{c['num']}: {c['title']} ({c['xkcd_url']})")

        text_summary = "\n".join(text_results)

        structured_content = None
        if HAS_PREFAB:
            # We'll use a vertical stack of comic cards
            with Div(css_class="flex flex-col gap-6") as view:
                Text(f"Search Results for: **{query}**", css_class="text-xl font-bold mb-4")
                for c in comics:
                    with Card(css_class="border-none shadow-none bg-secondary/10 p-4 rounded-xl"):
                        with CardHeader():
                            CardTitle(f"#{c['num']}: {c['title']}")
                        with CardContent():
                            Image(
                                src=c["img"],
                                alt=c["alt"],
                                css_class="rounded-lg mb-2 max-h-64 object-contain",
                            )
                            Text(c["alt"], css_class="text-sm italic opacity-80 mb-2")
                            Text(
                                f"[View on xkcd]({c['xkcd_url']}) | [Explanation]({c['explainxkcd_url']})",
                                css_class="text-xs text-primary",
                            )

            structured_content = PrefabApp(view=view, title=f"xkcd Search: {query}")

        return ToolResult(content=text_summary, structured_content=structured_content)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Search failed: {str(e)}")


@mcp.tool()
async def xkcd_random() -> ToolResult:
    """Fetch a random comic from the entire xkcd collection."""
    try:
        res = await xkcd_api.fetch_random()
        if not res.get("success"):
            raise ToolError(f"Error: {res.get('error')}")
        return await _format_comic_result(res["comic"])
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def xkcd_help() -> ToolResult:
    """Get help and usage information for xkcd-mcp tools and configuration."""
    help_text = (
        "# xkcd-mcp Help\n\n"
        "This server utilizes the official xkcd.com JSON API to fetch comic metadata and images.\n\n"
        "### Available Tools\n"
        "- `xkcd_latest()`: Fetch the most recent comic.\n"
        "- `xkcd_get(num)`: Fetch a specific comic by number.\n"
        "- `xkcd_random()`: Get a random surprise comic.\n"
        "- `xkcd_search(query)`: Search comics by topic (e.g., 'aliens').\n\n"
        "### Configuration\n"
        "- **Backend Port**: 10778 (API + MCP HTTP)\n"
        "- **Web UI Port**: 10779 (Vite Dashboard)\n"
        "- **Prefab UI**: Enabled by default in compatible clients.\n\n"
        "### Links\n"
        "- [Official xkcd](https://xkcd.com)\n"
        "- [explainxkcd Wiki](https://www.explainxkcd.com)\n"
    )

    structured_content = None
    if HAS_PREFAB:
        with Card(css_class="max-w-xl border-none shadow-none bg-transparent") as view:
            with CardHeader():
                CardTitle("xkcd-mcp Help Center")
            with CardContent():
                Text(
                    "Official xkcd metadata and rich in-chat comic rendering.",
                    css_class="text-lg font-bold mb-4",
                )
                with Div(css_class="grid grid-cols-2 gap-4"):
                    with Div():
                        Text("📡 Backend API", css_class="font-mono text-sm opacity-60")
                        Text("Port 10778", css_class="text-xl")
                    with Div():
                        Text("🎨 Web UI", css_class="font-mono text-sm opacity-60")
                        Text("Port 10779", css_class="text-xl")
                Text(
                    "\nUse `xkcd_latest` or `xkcd_random` to get started!", css_class="mt-4 italic"
                )

        structured_content = PrefabApp(view=view, title="xkcd-mcp Help")

    return ToolResult(content=help_text, structured_content=structured_content)


async def _format_comic_result(comic: dict) -> ToolResult:
    """Common formatting for comic results (Text + Prefab)."""
    title = comic["title"]
    alt = comic["alt"]
    img_url = comic["img"]
    num = comic["num"]

    label = f"xkcd #{num}: {title}"
    text_summary = (
        f"{label}\n"
        f"Image: {img_url}\n"
        f"Alt: {alt}\n"
        f"Links: {comic['xkcd_url']} | {comic['explainxkcd_url']}"
    )

    structured_content = None
    if HAS_PREFAB:
        with Card(css_class="max-w-2xl border-none shadow-none bg-transparent") as view:
            with CardHeader():
                CardTitle(label)
            with CardContent():
                Image(src=img_url, alt=alt, css_class="rounded-lg shadow-md mb-2")
                Text(alt, css_class="text-sm italic opacity-80")

        structured_content = PrefabApp(view=view, title=label)

    return ToolResult(content=text_summary, structured_content=structured_content)
