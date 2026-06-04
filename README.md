# mcp-unione

A Python [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server for
[UniOne / Unisender Go](https://unione.io/), exposing the transactional email API as
typed MCP tools alongside an offline, bundled knowledge base (resources, full-text
search, and error/status lookups).

It gives an MCP client (Claude Code, Claude Desktop, or any MCP host) **36 tools** —
32 typed API tools across 10 domains plus 4 documentation tools — **20 knowledge-base
resources**, and **2 guided prompts**, all backed by a thin async `httpx` client that
maps UniOne's error codes to a typed `UniOneError`.

## What it does

- Send transactional email and manage subscriptions, templates, webhooks, suppression
  lists, sending domains, event exports, tags, and projects.
- Validate email addresses and check account info.
- Search and read a curated, offline copy of the UniOne docs without leaving the chat.
- Look up any UniOne API error code or delivery status and get the cause + fix.

## Install

Requires Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

For development (tests + linter):

```bash
uv sync --extra dev
```

## Configuration

Configuration comes from environment variables (copy `.env.example` to `.env` and fill
it in, or pass them through your MCP client config):

| Variable          | Required | Default | Description                                                                 |
| ----------------- | -------- | ------- | --------------------------------------------------------------------------- |
| `UNIONE_API_KEY`  | Yes      | —       | UniOne API key (https://cp.unione.io/en/user/info/api).                     |
| `UNIONE_REGION`   | No       | `eu`    | Region selector: `eu`, `us`, or `global`. Chooses the API host.             |
| `UNIONE_BASE_URL` | No       | —       | Full base-URL override. Wins over `UNIONE_REGION` when set.                 |
| `UNIONE_TIMEOUT`  | No       | `30`    | Per-request HTTP timeout, in seconds.                                       |

The API key is only needed to make real API calls — listing tools, reading resources,
and searching the knowledge base all work without one.

## Run

```bash
uv run mcp-unione
```

The server speaks MCP over `stdio`.

## Claude Code / Claude Desktop config

Add the server to your MCP client config (Claude Desktop:
`claude_desktop_config.json`; Claude Code: `.mcp.json` / `claude mcp add`). Replace
`cwd` with the absolute path to this repository:

```json
{
  "mcpServers": {
    "unione": {
      "command": "uv",
      "args": ["run", "mcp-unione"],
      "cwd": "/absolute/path/to/mcp-unione",
      "env": {
        "UNIONE_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Safety

`unione_send_email` will **not** actually send unless you pass `confirm_send=true`.
Without it, the tool returns a dry-run preview (recipients, subject, engine, count) and
sends nothing — so the model cannot send real mail by accident. Re-call the same tool
with `confirm_send=true` to actually deliver.

The tool also accepts `sandbox=true`, which routes the message through UniOne's sandbox
domain for safe end-to-end testing without delivering to real inboxes.

## Tools

**32 API tools across 10 domains:**

| Domain         | Tools                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `system`       | `unione_system_ping`, `unione_system_info`                                                               |
| `email`        | `unione_send_email` (send-guarded), `unione_subscribe`                                                   |
| `validation`   | `unione_validate_email`                                                                                  |
| `template`     | `unione_template_set`, `unione_template_get`, `unione_template_list`, `unione_template_delete`           |
| `webhook`      | `unione_webhook_set`, `unione_webhook_get`, `unione_webhook_list`, `unione_webhook_delete`               |
| `suppression`  | `unione_suppression_set`, `unione_suppression_get`, `unione_suppression_list`, `unione_suppression_delete` |
| `domain`       | `unione_domain_get_dns_records`, `unione_domain_validate_verification_record`, `unione_domain_validate_dkim`, `unione_domain_list`, `unione_domain_delete` |
| `event_dump`   | `unione_event_dump_create`, `unione_event_dump_get`, `unione_event_dump_list`, `unione_event_dump_delete` |
| `tag`          | `unione_tag_list`, `unione_tag_delete`                                                                   |
| `project`      | `unione_project_create`, `unione_project_update`, `unione_project_list`, `unione_project_delete`         |

**4 documentation tools:**

| Tool                      | Purpose                                                                            |
| ------------------------- | --------------------------------------------------------------------------------- |
| `unione_search_docs`      | Full-text search the bundled knowledge base; returns matching pages + snippets.   |
| `unione_fetch_doc_page`   | Fetch a live UniOne docs page by slug or full URL.                                 |
| `unione_lookup_error`     | Explain a UniOne API error code (cause + fix) from the bundled error table.        |
| `unione_lookup_status`    | Explain an email status or extended delivery-status code.                          |

## Knowledge-base resources

The curated, offline knowledge base is exposed as **20 MCP resources** under the
`unione-docs://<slug>` scheme. Available slugs:

```
getting-started            web-api-reference          email-send-params
template-simple            template-velocity          template-liquid
email-statuses             delivery-status-codes      error-codes
email-validation           webhooks                   suppression-lists
projects                   dns-setup                  tracking-domains
dedicated-ip               sandbox-domain             unsubscribe
sdks-integrations          changelog
```

Read a page with, e.g., `unione-docs://email-statuses`.

## Prompts

Two guided prompts help the model use the tools correctly:

- `compose_transactional_email` — walks through assembling a valid `unione_send_email`
  call (verified `from_email`, recipients, body or template, engine, unsubscribe token,
  preview-then-confirm flow).
- `diagnose_delivery` — explains a delivery status or API error code using the lookup
  tools and the relevant KB resources.

## Development

```bash
uv run pytest          # run the test suite (httpx mocked with respx — zero real API calls)
uv run ruff check .    # lint
```

## License

MIT © 2026 karimou5
