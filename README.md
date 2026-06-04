# mcp-unione

[![CI](https://github.com/karimou5/mcp-unione/actions/workflows/ci.yml/badge.svg)](https://github.com/karimou5/mcp-unione/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/karimou5/mcp-unione?sort=semver)](https://github.com/karimou5/mcp-unione/releases)
[![Container](https://img.shields.io/badge/ghcr.io-mcp--unione-2496ED?logo=docker&logoColor=white)](https://github.com/karimou5/mcp-unione/pkgs/container/mcp-unione)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server for
[UniOne / Unisender Go](https://unione.io/) that exposes the transactional email API as
typed [Model Context Protocol](https://modelcontextprotocol.io/) tools — alongside an
**offline, bundled knowledge base** (browsable resources, full-text search, and
error/status lookups generated from the official docs).

Point any MCP client (Claude Code, Claude Desktop, or any MCP host) at it and the model
can send transactional email, manage your sending setup, and answer UniOne questions
from a curated local copy of the docs — without a single hand-written API call.

```
36 tools   ·   20 knowledge-base resources   ·   2 guided prompts
```

- **32 API tools** across 10 domains — a typed, 1:1 wrapper over the UniOne
  transactional Web API v1.
- **4 documentation tools** — search the bundled KB, fetch a live docs page, and look up
  any error code or delivery status (cause **+** fix).
- **20 KB resources** — a curated, offline copy of the UniOne docs under
  `unione-docs://<slug>`, distilled from ~4,000 lines of crawled documentation.
- **Send guard** — `unione_send_email` refuses to deliver real mail unless you explicitly
  opt in, so an autonomous agent can explore safely.
- A thin async `httpx` client maps UniOne's ~360 error codes to a typed `UniOneError`
  (with the documented fix), and **never logs your API key**.

---

## Contents

- [Quick start](#quick-start) · [Run with Docker](#run-with-docker)
- [Configuration](#configuration)
- [Use it from an MCP client](#use-it-from-an-mcp-client)
- [Safety: the send guard](#safety-the-send-guard)
- [Tools](#tools) · [Knowledge-base resources](#knowledge-base-resources) · [Prompts](#prompts)
- [Development](#development) · [Releases & images](#releases--images)

---

## Quick start

Requires Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                       # install
export UNIONE_API_KEY=...      # from https://cp.unione.io/en/user/info/api
uv run mcp-unione              # start the server (speaks MCP over stdio)
```

The API key is only needed for **real** API calls — listing tools, reading resources,
and searching the knowledge base all work without one.

## Run with Docker

A multi-arch image is published to GitHub Container Registry on every release:

```bash
docker pull ghcr.io/karimou5/mcp-unione:latest

# stdio server — keep STDIN open with -i
docker run -i --rm -e UNIONE_API_KEY=your_key_here ghcr.io/karimou5/mcp-unione:latest
```

Tags: `:latest` and `:X.Y.Z` / `:X.Y` (published from releases), plus `:main` and
`:sha-<short>` (built from `main`).

## Configuration

Configuration comes from environment variables (copy `.env.example` to `.env`, or pass
them through your MCP client config):

| Variable          | Required | Default | Description                                                       |
| ----------------- | -------- | ------- | ----------------------------------------------------------------- |
| `UNIONE_API_KEY`  | Yes¹     | —       | UniOne API key — <https://cp.unione.io/en/user/info/api>.         |
| `UNIONE_REGION`   | No       | `eu`    | API host: `eu` (`eu1`), `us` (`us1`), or `global` (`api`).        |
| `UNIONE_BASE_URL` | No       | —       | Full base-URL override (must include `/en/transactional/api/v1`). Wins over `UNIONE_REGION`. |
| `UNIONE_TIMEOUT`  | No       | `30`    | Per-request HTTP timeout, in seconds.                             |

¹ Only required to make real API calls. Docs tools and resources work without it; API
tools return a clear "missing API key" error instead of failing obscurely.

## Use it from an MCP client

Add the server to your MCP client config (Claude Desktop:
`claude_desktop_config.json`; Claude Code: `.mcp.json` or `claude mcp add`).

**Local (uv)** — replace `cwd` with the absolute path to this repository:

```json
{
  "mcpServers": {
    "unione": {
      "command": "uv",
      "args": ["run", "mcp-unione"],
      "cwd": "/absolute/path/to/mcp-unione",
      "env": { "UNIONE_API_KEY": "your_key_here" }
    }
  }
}
```

**Docker** — no local checkout needed:

```json
{
  "mcpServers": {
    "unione": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "UNIONE_API_KEY", "ghcr.io/karimou5/mcp-unione:latest"],
      "env": { "UNIONE_API_KEY": "your_key_here" }
    }
  }
}
```

## Safety: the send guard

`unione_send_email` will **not** actually send unless you pass `confirm_send=true`.
Without it, the tool returns a dry-run preview (recipients, subject, engine, count) and
sends nothing — so the model cannot send real mail by accident. Re-call the same tool
with `confirm_send=true` to deliver.

It also accepts `sandbox=true`, which routes the message through UniOne's sandbox domain
for safe end-to-end testing without reaching real inboxes.

## Deliverability & the unsubscribe footer

By default UniOne appends an **unsubscribe footer** to every message, e.g.:

```
This message to <to> was sent from:
MCP UniOne | <from_email>
Unsubscribe
```

Gmail often reads that footer as a marketing signal and files the email under the
**Promotions** tab (or **Spam** for a young sending domain) — so a "delivered" email can
still feel "not received". For transactional mail, pass **`skip_unsubscribe=1`** to
`unione_send_email` to drop the footer and improve inbox placement.

> **Note:** `skip_unsubscribe` must be enabled on your UniOne account first. If setting it
> has no visible effect (the footer is still there), **contact UniOne support** to turn it
> on for your account.

Tip: a "delivered" status (UniOne event `delivered` / `ok_delivered`, with a `250 OK` from
the receiving server) means the message reached the inbox provider. If it's not in the
inbox, check **Promotions** and **Spam** before assuming a send failure — use
`unione_event_dump_create` to read the real per-message delivery status.

## Subscribe / double opt-in

`unione_subscribe(from_email, from_name, to_email)` sends a **subscription confirmation
request** to `to_email`: the recipient receives an email from `from_name <from_email>`
asking them to confirm (opt in). When they click the confirmation link, UniOne records the
consent and clears any prior unsubscribe for that address — the inverse of the unsubscribe
footer above. All three arguments are required, and `from_email` must be on a verified
sending domain. Use it to (re)build explicit consent before sending to an address that may
have unsubscribed.

## Tools

**32 API tools across 10 domains:**

| Domain        | Tools                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------- |
| `system`      | `unione_system_ping`, `unione_system_info`                                                                 |
| `email`       | `unione_send_email` (send-guarded), `unione_subscribe`                                                     |
| `validation`  | `unione_validate_email`                                                                                    |
| `template`    | `unione_template_set`, `unione_template_get`, `unione_template_list`, `unione_template_delete`             |
| `webhook`     | `unione_webhook_set`, `unione_webhook_get`, `unione_webhook_list`, `unione_webhook_delete`                 |
| `suppression` | `unione_suppression_set`, `unione_suppression_get`, `unione_suppression_list`, `unione_suppression_delete` |
| `domain`      | `unione_domain_get_dns_records`, `unione_domain_validate_verification_record`, `unione_domain_validate_dkim`, `unione_domain_list`, `unione_domain_delete` |
| `event_dump`  | `unione_event_dump_create`, `unione_event_dump_get`, `unione_event_dump_list`, `unione_event_dump_delete`  |
| `tag`         | `unione_tag_list`, `unione_tag_delete`                                                                      |
| `project`     | `unione_project_create`, `unione_project_update`, `unione_project_list`, `unione_project_delete`           |

**4 documentation tools:**

| Tool                    | Purpose                                                                          |
| ----------------------- | -------------------------------------------------------------------------------- |
| `unione_search_docs`    | Full-text search the bundled knowledge base; returns matching pages + snippets.  |
| `unione_fetch_doc_page` | Fetch a live UniOne docs page by slug or full URL.                               |
| `unione_lookup_error`   | Explain a UniOne API error code (cause + fix) from the bundled error table.      |
| `unione_lookup_status`  | Explain an email status or extended delivery-status code.                        |

## Knowledge-base resources

The curated, offline knowledge base is exposed as **20 MCP resources** under the
`unione-docs://<slug>` scheme — read e.g. `unione-docs://email-statuses`:

```
getting-started       web-api-reference      email-send-params
template-simple       template-velocity      template-liquid
email-statuses        delivery-status-codes  error-codes
email-validation      webhooks               suppression-lists
projects              dns-setup              tracking-domains
dedicated-ip          sandbox-domain         unsubscribe
sdks-integrations     changelog
```

## Prompts

Two guided prompts help the model use the tools correctly:

- `compose_transactional_email` — walks through assembling a valid `unione_send_email`
  call (verified `from_email`, recipients, body or template, engine, unsubscribe token,
  preview-then-confirm flow).
- `diagnose_delivery` — explains a delivery status or API error code using the lookup
  tools and the relevant KB resources.

## Development

```bash
uv sync --extra dev    # install dev dependencies (pytest, respx, ruff)
uv run pytest          # 67 tests — HTTP mocked with respx, zero real API calls
uv run ruff check .    # lint
```

The knowledge-base data (`src/mcp_unione/data/`) is generated from the upstream docs and
regenerated deterministically with:

```bash
uv run python scripts/build_kb.py
```

## Releases & images

Versioning is automated with [release-please](https://github.com/googleapis/release-please)
and [Conventional Commits](https://www.conventionalcommits.org/) (`feat:` → minor,
`fix:` → patch). Merging the release PR publishes a GitHub Release + tag and pushes the
versioned Docker image (`:X.Y.Z`, `:X.Y`, `:latest`) to
[GHCR](https://github.com/karimou5/mcp-unione/pkgs/container/mcp-unione). Pushes to `main`
publish `:main` / `:sha-<short>` staging images.

## License

MIT © 2026 karimou5
