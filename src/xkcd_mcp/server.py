"""FastMCP server: xkcd comics via the official JSON API."""

from __future__ import annotations

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


def _format(comic: dict) -> str:
    return (
        f"xkcd #{comic['num']}: {comic['title']}\n"
        f"Image: {comic['img']}\n"
        f"Alt: {comic['alt']}\n"
        f"Links: {comic['xkcd_url']} | {comic['explainxkcd_url']}"
    )


@mcp.tool()
async def xkcd_latest() -> str:
    """Fetch the latest xkcd comic."""
    return _format(await xkcd_api.fetch_current())


@mcp.tool()
async def xkcd_get(number: int) -> str:
    """Fetch a specific xkcd comic by its number."""
    comic = await xkcd_api.fetch_by_number(number)
    if comic is None:
        raise ToolError(f"No comic #{number}.")
    return _format(comic)


@mcp.tool()
async def xkcd_random() -> str:
    """Fetch a random xkcd comic."""
    return _format(await xkcd_api.fetch_random())


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

