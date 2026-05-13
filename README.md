# xkcd-mcp

A minimal [FastMCP](https://github.com/jlowin/fastmcp) server that gives Claude Code access to xkcd comics via the official xkcd JSON API and explainxkcd search.

## Tools

- `xkcd_latest` — fetch the most recent comic
- `xkcd_get(number)` — fetch a specific comic by number
- `xkcd_random` — fetch a random comic
- `xkcd_search(query)` — search comics by topic

Each result returns the title, image URL, alt text, and links to xkcd.com / explainxkcd.com.

## Install

Requires [`uv`](https://github.com/astral-sh/uv) and Python 3.12+.

```sh
git clone https://github.com/justinstevens42/xkcd-mcp.git
cd xkcd-mcp
uv sync
```

## Add to Claude Code

From inside the cloned repo:

```sh
claude mcp add --scope user xkcd -- uv --directory "$(pwd)" run xkcd-mcp
```

If you've registered it before, remove the old entry first:

```sh
claude mcp remove --scope user xkcd
```

## License

MIT — forked from [sandraschi/xkcd-mcp](https://github.com/sandraschi/xkcd-mcp).
