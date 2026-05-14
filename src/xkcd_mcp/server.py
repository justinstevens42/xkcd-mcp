"""FastMCP server: xkcd comics via the official JSON API."""

from __future__ import annotations

import base64
import os
import sys

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from xkcd_mcp import xkcd_api

mcp = FastMCP(
    "xkcd-mcp",
    instructions=(
        "xkcd comics via the official JSON API and explainxkcd semantic search. "
        "Tools: xkcd_latest, xkcd_get(number), xkcd_random, xkcd_search(query). "
        "Prompts: xkcd_summarize. "
        "Each result includes the image URL, alt text, and explainxkcd wiki link."
    ),
)


def _terminal_supports_kitty_graphics() -> bool:
    """Best-effort detection of terminals that implement the Kitty graphics protocol."""
    if os.environ.get("KITTY_WINDOW_ID"):
        return True
    if os.environ.get("TERM_PROGRAM") in ("ghostty", "WezTerm"):
        return True
    if os.environ.get("KONSOLE_VERSION"):
        return True
    return False


def _png_dimensions(data: bytes) -> tuple[int, int] | None:
    """Read (width, height) in pixels from a PNG IHDR chunk. Returns None if data isn't a PNG."""
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return width, height


# Render image at this column width via Kitty's `c=` param; height scales proportionally.
_RENDER_COLS = 70
# Newlines written after the image. With `a=T`, Kitty/Ghostty advance the cursor to the
# bottom-right of the image, so the first \n drops below it and the rest are visual margin.
_TRAILING_NEWLINES = 3
# Skip rendering for images larger than this — terminals can choke on multi-MB payloads,
# and a few xkcd comics (e.g. #1110 "Click and Drag") are absurdly large.
_MAX_IMAGE_BYTES = 2 * 1024 * 1024


def _debug(msg: str) -> None:
    if os.environ.get("XKCD_MCP_DEBUG"):
        print(f"xkcd-mcp: {msg}", file=sys.stderr)


def _display_in_terminal(img_data: bytes) -> None:
    """Write image to /dev/tty using Kitty graphics protocol (Ghostty, Kitty, WezTerm, Konsole).

    Bails out (without reserving rows) if the image isn't a PNG or is too large, since
    `f=100` only accepts PNG data and oversized payloads tend to fail silently terminal-side.
    """
    if not _terminal_supports_kitty_graphics():
        return

    if _png_dimensions(img_data) is None:
        _debug("skipping non-PNG image; Kitty f=100 only supports PNG")
        return
    if len(img_data) > _MAX_IMAGE_BYTES:
        _debug(f"skipping oversized image ({len(img_data)} bytes > {_MAX_IMAGE_BYTES})")
        return

    # Build the entire payload as one bytes object so we can emit it in a single write loop.
    # If we streamed chunks one-by-one, Claude Code (or any concurrent writer to the same
    # terminal) could inject bytes mid-APC-sequence, dropping us out of graphics mode and
    # rendering the remaining base64 as literal text.
    b64 = base64.standard_b64encode(img_data).decode()
    chunks = [b64[i:i + 4096] for i in range(0, len(b64), 4096)]
    parts = [b"\n"]
    for i, chunk in enumerate(chunks):
        more = 0 if i == len(chunks) - 1 else 1
        if i == 0:
            seq = f"\033_Ga=T,f=100,m={more},q=2,c={_RENDER_COLS};{chunk}\033\\"
        else:
            seq = f"\033_Gm={more},q=2;{chunk}\033\\"
        parts.append(seq.encode())
    parts.append(b"\n" * _TRAILING_NEWLINES)
    payload = b"".join(parts)

    fd = None
    try:
        fd = os.open("/dev/tty", os.O_WRONLY)
        view = memoryview(payload)
        while view:
            n = os.write(fd, view)
            view = view[n:]
    except Exception as e:
        _debug(f"tty write failed: {e!r}")
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


async def _fetch_and_display(url: str) -> None:
    if not _terminal_supports_kitty_graphics():
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        _display_in_terminal(resp.content)
    except Exception:
        pass


def _format(comic: dict) -> str:
    return (
        f"xkcd #{comic['num']}: {comic['title']}\n"
        f"Image: {comic['img']}\n"
        f"Alt: {comic['alt']}\n"
        f"Links: {comic['xkcd_url']} | {comic['explainxkcd_url']}"
    )


async def _format_with_image(comic: dict) -> str:
    await _fetch_and_display(comic["img"])
    return _format(comic)


@mcp.tool()
async def xkcd_latest() -> str:
    """Fetch the latest xkcd comic."""
    return await _format_with_image(await xkcd_api.fetch_current())


@mcp.tool()
async def xkcd_get(number: int) -> str:
    """Fetch a specific xkcd comic by its number."""
    comic = await xkcd_api.fetch_by_number(number)
    if comic is None:
        raise ToolError(f"No comic #{number}.")
    return await _format_with_image(comic)


@mcp.tool()
async def xkcd_random() -> str:
    """Fetch a random xkcd comic."""
    return await _format_with_image(await xkcd_api.fetch_random())


@mcp.tool()
async def xkcd_search(query: str) -> str:
    """Search xkcd comics by topic via explainxkcd semantic indexing."""
    nums = await xkcd_api.search_explainxkcd(query)
    if not nums:
        return f"No xkcd comics found for '{query}'."

    comics = [c for n in nums if (c := await xkcd_api.fetch_by_number(n))]
    if not comics:
        raise ToolError(f"Found matches for '{query}' but could not fetch metadata.")

    lines = [f"Found {len(comics)} comics for '{query}':", ""]
    lines.extend(_format(c) + "\n" for c in comics)
    return "\n".join(lines)

@mcp.prompt()
def xkcd_summarize() -> str:
    """Summarize the current Claude conversation and find the most relevant xkcd comic."""
    return (
        "Summarize the current Claude conversation, and find the most relevant XKCD "
        "to the conversation. Use xkcd_search with keywords drawn from your summary, "
        "then present the best match with its title, alt text, and links."
    )
