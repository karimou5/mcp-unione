# syntax=docker/dockerfile:1
FROM python:3.12-slim

# uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Resolve + install dependencies and the package (data files ship inside the wheel)
COPY pyproject.toml uv.lock README.md .python-version ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# stdio MCP server — run with:  docker run -i --rm -e UNIONE_API_KEY=... ghcr.io/karimou5/mcp-unione
ENTRYPOINT ["mcp-unione"]
