"""FastMCP 3.1 — xkcd tools."""

from __future__ import annotations
import os

from fastmcp import FastMCP
from fastmcp.tools import ToolResult

from xkcd_mcp import xkcd_api

# Prefab UI imports with graceful fallback
try:
    from prefab_ui.app import PrefabApp
    from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Image, Text
    HAS_PREFAB = os.environ.get("XKCD_PREFAB_APPS", "1") != "0"
except ImportError:
    HAS_PREFAB = False

mcp = FastMCP(
    "xkcd-mcp",
    instructions=(
        "xkcd comics via the official JSON API only (xkcd.com/.../info.0.json). "
        "Operations: current, by_number, random. Includes image URL, alt text, and explainxkcd wiki link "
        "(link only — no scraping)."
    ),
)


@mcp.tool(app=HAS_PREFAB)
async def xkcd_latest() -> ToolResult:
    """Fetch the latest comic from xkcd.com."""
    try:
        res = await xkcd_api.fetch_current()
        if not res.get("success"):
            return ToolResult(content=f"Error: {res.get('error')}", is_error=True)
        return await _format_comic_result(res["comic"])
    except Exception as e:
        return ToolResult(content=f"Unexpected error: {str(e)}", is_error=True)


@mcp.tool(app=HAS_PREFAB)
async def xkcd_get(comic_number: int) -> ToolResult:
    """Fetch a specific xkcd comic by its number."""
    try:
        res = await xkcd_api.fetch_by_number(comic_number)
        if not res.get("success"):
            return ToolResult(content=f"Error: {res.get('error')}", is_error=True)
        return await _format_comic_result(res["comic"])
    except Exception as e:
        return ToolResult(content=f"Unexpected error: {str(e)}", is_error=True)


@mcp.tool(app=HAS_PREFAB)
async def xkcd_random() -> ToolResult:
    """Fetch a random comic from the entire xkcd collection."""
    try:
        res = await xkcd_api.fetch_random()
        if not res.get("success"):
            return ToolResult(content=f"Error: {res.get('error')}", is_error=True)
        return await _format_comic_result(res["comic"])
    except Exception as e:
        return ToolResult(content=f"Unexpected error: {str(e)}", is_error=True)


@mcp.tool(app=HAS_PREFAB)
async def xkcd_help() -> ToolResult:
    """Get help and usage information for xkcd-mcp tools and configuration."""
    help_text = (
        "# xkcd-mcp Help\n\n"
        "This server utilizes the official xkcd.com JSON API to fetch comic metadata and images.\n\n"
        "### Available Tools\n"
        "- `xkcd_latest()`: Fetch the most recent comic.\n"
        "- `xkcd_get(num)`: Fetch a specific comic by number.\n"
        "- `xkcd_random()`: Get a random surprise comic.\n\n"
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
                Text("Official xkcd metadata and rich in-chat comic rendering.", css_class="text-lg font-bold mb-4")
                with Text(css_class="grid grid-cols-2 gap-4"):
                    with Text():
                        Text("📡 Backend API", css_class="font-mono text-sm opacity-60")
                        Text("Port 10778", css_class="text-xl")
                    with Text():
                        Text("🎨 Web UI", css_class="font-mono text-sm opacity-60")
                        Text("Port 10779", css_class="text-xl")
                Text("\nUse `xkcd_latest` or `xkcd_random` to get started!", css_class="mt-4 italic")
        
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
        data_uri = await xkcd_api.fetch_image_data_uri(img_url)
        if data_uri:
            with Card(css_class="max-w-2xl border-none shadow-none bg-transparent") as view:
                with CardHeader():
                    CardTitle(label)
                with CardContent():
                    Image(src=data_uri, alt=alt, css_class="rounded-lg shadow-md mb-2")
                    Text(alt, css_class="text-sm italic opacity-80")
            
            structured_content = PrefabApp(view=view, title=label)

    return ToolResult(content=text_summary, structured_content=structured_content)
