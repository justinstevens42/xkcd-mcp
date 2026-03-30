# xkcd-mcp User Guide (SOTA v2.0)

## Welcome to the xkcd MCP Server!

This server brings the entire world of Randall Munroe's comics directly into your chat experience. Whether you're looking for the newest update, a specific classic, or just a random laugh, the `xkcd-mcp` tools are designed for speed, reliability, and rich visualization.

## QUICK START

Get an xkcd comic in your chat by asking for it in natural language:

- **"Give me the latest xkcd"** → Calls `xkcd_latest()` to show today's comic.
- **"Show me xkcd 1234"** → Calls `xkcd_get(1234)` to find that exact comic index.
- **"Surprise me with an xkcd"** → Calls `xkcd_random()` to fetch a random one from the archive.
- **"Help with xkcd tools"** → Calls `xkcd_help()` to show active ports and available commands.

## HOW TO USE IT

1. **Newest Comics**: The `xkcd_latest` tool is your daily check-in. It's the most common entry point for any conversation.
2. **Specific Archives**: Known a comic by number? (e.g., *149 - Sandwich*, *327 - Exploits of a Mom*). Use `xkcd_get` to retrieve it immediately.
3. **Random Discovery**: Use `xkcd_random` when you just want a quick laugh or a bit of technical humor without a specific target.

## RICH PREFAB UI RENDERING

When using this server in a compatible MCP client (like Claude Desktop or Antigravity), you'll see a premium **Prefab UI card** for every comic:

- **Image Preview**: Displays the high-resolution comic from `xkcd.com`.
- **Mouse-over Alt Text**: The "alt" field (mouse-over text) is displayed prominently as it often contains the punchline or extra technical context.
- **Explain xkcd**: Follow the provided link to the *Explain xkcd* wiki for deep-dives into the science and jokes.
- **Official Links**: Quick access to the original comic page.

## CONFIGURATION

The `xkcd-mcp` server runs on two primary ports assigned from the SOTA fleet range (10700-10800):

- **Backend (MCP HTTP)**: **10778**
- **Vite SPA (Frontend)**: **10779**

Standard environment variables:
- `XKCD_PREFAB_APPS`: Set to `1` (default) for rich UI, or `0` for plain markdown.
- `XKCD_MCP_HOST`: Bind address (default: `127.0.0.1`).
- `XKCD_MCP_PORT`: Port override (default: `10778`).

## TROUBLESHOOTING

- **Comic Not Found**: If you request a number that doesn't exist (e.g., xkcd 9999), the server will return a clean 404 message. Check the latest comic number to find the upper bound.
- **Images Not Loading**: This requires an active internet connection to `xkcd.com`. Ensure your network allows access to the official domain.
- **Tool Failures**: Use `xkcd_help` to verify that the server is up and its ports are correctly configured.

---
*Powered by FastMCP 3.1 & Antigravity SOTA Fleet.*
