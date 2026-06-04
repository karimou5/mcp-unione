# mcp-unione

A Python [FastMCP](https://github.com/jlowin/fastmcp) server exposing 30+ typed [UniOne](https://unione.io/) transactional API tools plus an offline knowledge base (resources, search, lookups).

## Install

```bash
uv sync --extra dev
```

## Configuration

Copy `.env.example` to `.env` and fill in your API key:

```bash
UNIONE_API_KEY=your_key_here
UNIONE_REGION=eu  # eu | us | global
```

## Run

```bash
uv run mcp-unione
```

## Claude MCP config

```json
{
  "mcpServers": {
    "unione": {
      "command": "uv",
      "args": ["run", "mcp-unione"],
      "env": {
        "UNIONE_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Development

```bash
uv run pytest -q
```

## License

MIT © 2026 karimou5
