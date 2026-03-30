# xkcd-mcp
version := "0.2.0"
name := "xkcd-mcp"
cmd := "xkcd-mcp"


default:
    just --list

stats:
    uv run python tools/repo_stats.py

run serve:
    uv run xkcd-mcp --serve

stdio:
    uv run xkcd-mcp

lint check:
    uv run ruff check .
    uv run ruff format --check .

format fmt:
    uv run ruff format .

test:
    uv sync --extra dev
    uv run pytest tests -v

precommit:
    uv sync --extra dev
    uv run pre-commit run --all-files

install:
    uv sync

install-web:
    cd web_sota
    npm install

web start:
    .\web_sota\start.ps1

clean:
    powershell -NoProfile -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, .ruff_cache, .pytest_cache, web_sota/node_modules, web_sota/dist; Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Cleaned.'"

health:
    curl.exe -s http://127.0.0.1:10778/health

# Build MCPB bundle (Claude Desktop)
mcpb-pack:
    mcpb pack . dist/{{name}}-v{{version}}.mcpb
