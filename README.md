# xkcd-mcp (modified to work with Claude Code)

[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.2-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

**MODEL CONTEXT PROTOCOL**  *fine print sold separately*

---

### The part humans read first

**xkcd-mcp**  Comics for your LLM. **Official** JSON API (`/info.0.json`), **unofficial** amount of stick-figure drama.

You get a small **Vite** dashboard with a comic-panel **hero**: stick people, a speech bubble that says *MCP, explain this*, and a box labeled **JSON** that definitely understands your feelings. The README cant draw SVG, so imagine it badlysame energy as the web app.

> **Alt text (this repo):** A README receives a pull request titled make it whimsical. The CI passes. The narrator questions whether that was ever in scope.

> **Alt text (the app):** A tiny server labeled JSON gets enthusiastic waves while someone negotiates with the universe. Hover tooltips not included; thats what the comic **alt** is for.

No scraping. No Explainxkcd body fetch. Were not here to parse HTML like its 2003.

**Original Repo:** [github.com/sandraschi/xkcd-mcp](https://github.com/sandraschi/xkcd-mcp)
**Forked Repo:** [github.com/justinstevens42/xkcd-mcp](https://github.com/justinstevens42/xkcd-mcp)
---

## Technical details

### What it is

- **MCP server + HTTP API** exposing xkcd metadata and image URLs via the **official** API and **explainxkcd** semantic search.
- **Web UI** calls `POST /api/comic` with the same operations as the tool (`latest`, `random`, `by_number`, `search`).

### MCP tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `xkcd_latest` | Fetch the most recent comic. | None |
| `xkcd_get` | Fetch a specific comic by number. | `comic_number` (int) |
| `xkcd_random` | Fetch a random surprise comic. | None |
| `xkcd_search` | Search comics by topic (aliens, climate). | `query` (str) |
| `xkcd_help` | Display usage guide and system info. | None |

### Prefab UI (Rich In-Chat Comics)

When installed with the `apps` extra and used in a compatible client (Claude Desktop, Antigravity), these tools render a rich **PrefabApp** card containing:
- The comic **image** (high-resolution, base64-encoded).
- The comic **title** and **number**.
- The **alt text** directly below the image for context.
- A **link** to the original xkcd page.

This provides a seamless, visual way to consume comics without leaving the chat interface.

### Install

To get started, clone the repository and sync dependencies:

```powershell
git clone https://github.com/sandraschi/xkcd-mcp.git
Set-Location xkcd-mcp

# Sync all dependencies (v0.2.0)
uv sync
```

### MCP Configuration (Claude / Antigravity)

Add the following to your `mcp_config.json` (Antigravity) or `claude_desktop_config.json` (Claude):

```json
{
  "mcpServers": {
    "xkcd": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/xkcd-mcp", "run", "xkcd-mcp"],
      "env": {
        "XKCD_PREFAB_APPS": "1"
      }
    }
  }
}
```

> [!TIP]
> Ensure the `args` path matches your actual disk location. Using `uv run` is the most reliable way to ensure the correct environment and `apps` extra are loaded.

---

## Run  Manual Start

```powershell
uv run xkcd-mcp --serve
```

| Item | Value |
|------|--------|
| HTTP | `http://127.0.0.1:10778`  `/health`, `/docs` |
| MCP | `http://127.0.0.1:10778/mcp` |
| Env | `XKCD_MCP_HOST`, `XKCD_MCP_PORT` (default **10778**), `XKCD_MCP_HTTP_PATH` (default `/mcp`) |

### Run  web UI (SPA)

```powershell
.\web_sota\start.ps1
```

Or double-click `web_sota\start.bat` (launches the same script).

**http://127.0.0.1:10779/** (same repo root as install)

### Working with Claude Code (new)

Find where the repository is loaded on your machine. Then if the directory is DIRECTORY, run the command:
```
claude mcp add --scope user xkcd -e XKCD_PREFAB_APPS=1 -- uv --directory DIRECTORY run xkcd-mcp
```

### Fleet docs (LLM index)

- **`llms.txt`**  short index; **`llms-full.txt`**  tools, env, ports, troubleshooting.

#
## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

MIT
