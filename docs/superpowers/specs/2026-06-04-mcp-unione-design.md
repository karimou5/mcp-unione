# Spec — MCP UniOne (FastMCP, Python)

**Date:** 2026-06-04
**Owner:** karimou5
**Status:** Approved design → implementation plan to follow

A Model Context Protocol server, written in Python with **FastMCP**, that gives an
LLM agent two capabilities for [UniOne](https://docs.unione.io/en/) (Unisender Go)
transactional email:

1. **Tools** — full coverage of the UniOne transactional Web API v1 (30 methods).
2. **Documentation** — a hybrid knowledge base: a curated offline copy bundled as
   MCP resources + keyword search, plus live page fetch and error/status lookups.

The exhaustive source material extracted from the UniOne docs lives in
`docs/superpowers/research/` (5 files, ~4100 lines) and is the authority for every
parameter, enum, error code, and status referenced below.

---

## 1. Goals & non-goals

### Goals
- One-to-one, typed wrappers for every public UniOne transactional API method.
- Safe sending: real sends require an explicit confirmation flag; a sandbox path exists.
- A genuinely useful, mostly-offline UniOne knowledge base usable without network.
- Clear, typed errors (mapped from UniOne's ~300 error codes) — never raw stack traces.
- No real API calls in the test suite (httpx fully mocked with `respx`).
- Public GitHub repo with protected `main` (PR-only) and release-please automation.

### Non-goals (YAGNI)
- SMTP API (we use the HTTP API only).
- Obsolete `unsubscribed/*` methods.
- Persistent doc cache / DB.
- Any deployed app / hosting (this is a library + stdio server, not a web service).

---

## 2. Runtime & packaging

- **Language:** Python ≥ 3.11, managed with `uv`.
- **Framework:** FastMCP (the `mcp` Python SDK's FastMCP, `from mcp.server.fastmcp import FastMCP`, or the standalone `fastmcp` package — decided in the plan; default to the official `mcp[cli]`).
- **Transport:** `stdio` by default (Claude Desktop / Claude Code). An HTTP transport flag is available but not the default.
- **Deps:** `mcp[cli]` (or `fastmcp`), `httpx`, `pydantic` (v2). Dev: `pytest`, `pytest-asyncio`, `respx`, `ruff`.
- **Package name:** `mcp_unione`. Console script / module entry: `python -m mcp_unione` and a `mcp-unione` script.

---

## 3. Architecture & components

Each unit has one purpose, a typed interface, and is testable in isolation.

```
mcp-unione/
├── pyproject.toml · README.md · .env.example · .gitignore · LICENSE
├── src/mcp_unione/
│   ├── __init__.py
│   ├── __main__.py          # entrypoint: build server, run stdio (or http via flag)
│   ├── server.py            # FastMCP instance; registers tools + resources + prompts
│   ├── config.py            # env parsing: api_key, region/base_url, timeout
│   ├── client.py            # async httpx client: auth header, base URL, POST helper, error mapping
│   ├── errors.py            # UniOneError; loads data/errors.json for enrichment
│   ├── models.py            # shared Pydantic models (Recipient, Attachment, Body, …)
│   ├── tools/
│   │   ├── __init__.py      # register_all(mcp, client)
│   │   ├── email.py         # send, subscribe
│   │   ├── validation.py    # validate_email
│   │   ├── template.py      # set, get, list, delete
│   │   ├── webhook.py       # set, get, list, delete
│   │   ├── suppression.py   # set, get, list, delete
│   │   ├── domain.py        # get_dns_records, validate_verification_record, validate_dkim, list, delete
│   │   ├── event_dump.py    # create, get, list, delete
│   │   ├── tag.py           # list, delete
│   │   ├── project.py       # create, update, list, delete
│   │   └── system.py        # ping, info
│   ├── docs_tools.py        # search_docs, fetch_doc_page, lookup_error, lookup_status
│   ├── resources.py         # exposes data/kb/*.md as unione-docs://<slug>
│   ├── prompts.py           # compose_transactional_email, diagnose_delivery
│   └── data/
│       ├── kb/*.md          # curated knowledge base (built from research/)
│       ├── manifest.json    # [{slug,title,url,keywords,summary}]
│       ├── errors.json      # {code: {http, message, fix}} (~300 entries)
│       └── statuses.json    # email statuses + extended delivery_status codes
└── tests/                   # pytest + respx, fixtures, one module per tools/* module
```

`tools/*` modules receive the `client` and register their FastMCP tools. `server.py`
wires everything: `register_all(mcp, client)`, `resources.register(mcp)`,
`prompts.register(mcp)`, plus the four docs tools.

---

## 4. Tools — UniOne transactional API (30)

All tools are namespaced `unione_*`, take typed Pydantic arguments, and carry
docstrings derived from the official docs. Every tool returns the parsed UniOne
response (or a typed error). Method paths and parameters per
`research/01-api-reference.md`.

| Domain | Tools (method) |
|---|---|
| email | `unione_send_email` (email/send), `unione_subscribe` (email/subscribe) |
| validation | `unione_validate_email` (email-validation/single) |
| template | `unione_template_set/get/list/delete` |
| webhook | `unione_webhook_set/get/list/delete` |
| suppression | `unione_suppression_set/get/list/delete` |
| domain | `unione_domain_get_dns_records/validate_verification_record/validate_dkim/list/delete` |
| event_dump | `unione_event_dump_create/get/list/delete` |
| tag | `unione_tag_list/delete` |
| project | `unione_project_create/update/list/delete` |
| system | `unione_system_ping`, `unione_system_info` |

### 4.1 `unione_send_email` (the important one)
Exposes **every** `message` field: `recipients[]` (`email`, `substitutions`,
`metadata`), `tags`, `skip_unsubscribe`, `global_language`, `template_engine`
(`simple|velocity|liquid|none`), `template_id`, `global_substitutions`,
`global_metadata`, `body` (`html`, `plaintext`, `amp`), `subject`, `from_email`,
`from_name`, `reply_to`, `reply_to_name`, `track_links`, `track_read`,
`bypass_global`, `bypass_unavailable`, `bypass_unsubscribed`, `bypass_complained`,
`headers`, `attachments[]` (`type`,`name`,`content` base64), `inline_attachments[]`,
optional `idempotence_key`.

**Send guard (user-chosen behavior):**
- Parameter `confirm_send: bool = False`. When `False`, the tool does **not** call the
  API; it returns a structured preview (`from`, `to` list, `subject`, engine, counts)
  and instructs the caller to re-call with `confirm_send=true`.
- Parameter `sandbox: bool = False` routes to a UniOne sandbox sender domain when set
  (see `research/04`). Independent of `confirm_send`.
- The recipient list is logged (info level) before any real send; the API key is never logged.
- Response parsed into `status`, `job_id`, `emails[]`, `failed_emails{}`; `failed_emails`
  values explained inline from the docs.

Validation enforced by Pydantic: at least one recipient; ≤ 500 recipients; a `body`
or a `template_id`; warns when neither `html` nor `plaintext` present.

### 4.2 Notes per domain
- **suppression/set** accepts `cause` ∈ {`unsubscribed`,`temporary_unavailable`,`permanent_unavailable`,`complained`} (not `blocked`); `suppression/get` supports `all_projects`.
- **webhook/set** `status` ∈ {`active`,`disabled`,`stopped`}, `event_format` ∈ {`json_post`,`json_post_gzip`}, `events.email_status[]`, `events.spam_block[]`, `single_event`, `delivery_info`, `max_parallel`.
- **domain/*** maps the verification/DKIM lifecycle; `get_dns_records` returns the verification + DKIM record parts (DKIM selector `us._domainkey`).
- **event_dump/create** supports the full `filter` object + `format`/`delimiter`.
- **project/*** uses project key semantics; a project key works everywhere except `project/*`.

---

## 5. Documentation layer (hybrid)

### 5.1 Docs tools (4)
- `unione_search_docs(query, limit=5)` — keyword/relevance search over the bundled
  manifest + KB markdown; returns matching slugs, titles, and best passages.
- `unione_fetch_doc_page(slug_or_url)` — live-fetches a `docs.unione.io/en/<slug>`
  page, converts to markdown, returns it. For anything not bundled or for the freshest copy.
- `unione_lookup_error(code)` — returns `{code, http, message, fix}` from `errors.json`.
- `unione_lookup_status(status)` — explains an email status or extended
  `delivery_status` code from `statuses.json`.

### 5.2 Resources (curated KB, browsable as `unione-docs://<slug>`)
Built from `research/` into `data/kb/*.md`. Slugs:
`getting-started`, `web-api-reference`, `email-send-params`, `template-simple`,
`template-velocity`, `template-liquid`, `email-statuses`, `delivery-status-codes`,
`webhooks`, `suppression-lists`, `email-validation`, `dns-setup`, `sandbox-domain`,
`dedicated-ip`, `tracking-domains`, `projects`, `unsubscribe`, `error-codes`,
`changelog`, `sdks-integrations`.

Each KB file starts with a short front-matter-style header (title, source URL, last
synced date) so provenance is clear. A `scripts/build_kb.py` (or documented manual
step) regenerates `kb/`, `manifest.json`, `errors.json`, `statuses.json` from the
research notes; the generation is reproducible and committed.

### 5.3 Prompts (2)
- `compose_transactional_email` — guides the agent to assemble a valid `send` call
  (asks for from/to/subject/body/engine, reminds about verification + unsubscribe).
- `diagnose_delivery` — given a status/error/delivery_status, pulls the relevant KB +
  lookup explanation and suggests next steps.

---

## 6. Configuration & auth

Environment variables (via `.env` / process env):

| Var | Required | Default | Notes |
|---|---|---|---|
| `UNIONE_API_KEY` | for API tools | — | sent as `X-API-KEY` header |
| `UNIONE_REGION` | no | `eu` | `eu`→`eu1.unione.io`, `us`→`us1.unione.io`, `global`→`api.unione.io` |
| `UNIONE_BASE_URL` | no | derived | full override; wins over region |
| `UNIONE_TIMEOUT` | no | `30` | seconds |

Path suffix: `/en/transactional/api/v1`. Without an API key the **docs tools and
resources still work**; API tools return a clear "missing API key" error instead of failing obscurely.

---

## 7. Error handling

`client.py` POSTs JSON and inspects the response:
- UniOne `status:"error"` (or non-2xx) → raise `UniOneError(code, message, http_status)`,
  enriched with the `fix` hint from `errors.json` when the code is known.
- Network/timeout → `UniOneError` with a transport-specific message.
- Tools catch `UniOneError` and return a structured, human-readable error object
  (`{error: {code, message, fix}}`) rather than throwing raw.
- Secrets (`api_key`/`X-API-KEY`) are never included in logs or error text.

---

## 8. Testing

- `pytest` + `pytest-asyncio` + `respx` (mock httpx) — **zero real API calls**.
- One test module per `tools/*`: asserts the exact request path + payload and parses a
  representative response fixture.
- Error tests: 401, a UniOne `status:"error"` body, a timeout.
- Send-guard test: `confirm_send=False` returns a preview and makes **no** HTTP call;
  `confirm_send=True` issues the call.
- Docs tests: `search_docs` ranking, `lookup_error`, `lookup_status`, resource listing.
- `system/ping` doubles as an optional live smoke test, **skipped** when no API key is set.
- `ruff` for lint; CI runs lint + tests on every PR.

---

## 9. Repository, CI/CD & release automation

- **Create** a new GitHub repo under `karimou5` (suggested name `mcp-unione`),
  **public**.
- **Branch protection on `main`:** no direct pushes — all changes via pull request;
  require the CI status check (lint + tests) to pass; (admin enforcement on).
- **release-please:** set up via the project's `setup-release-please` skill, which wires
  the `kamencorp-release-please-bot` GitHub App (App ID 2907902), the two GitHub
  secrets, and `release-please-config.json` + `.release-please-manifest.json` +
  `.github/workflows/release-please.yml`. Release type: **python** (version in
  `pyproject.toml` + `CHANGELOG.md`, GitHub Releases on merge of the release PR). There
  are no build-staging/build-production workflows to adapt (this is a library/server,
  not a deployed app).
- **CI workflow** (`.github/workflows/ci.yml`): on PR + push, run `uv` install, `ruff`,
  `pytest`. This is the required status check for `main`.
- **Commits:** Conventional Commits (required by release-please). Commit messages and PR
  descriptions are anonymous — no assistant name or identifiable signature.
- **Sequencing:** local `git init` + first commit (spec + research) now; the GitHub repo
  creation, publish, branch protection, and release-please wiring happen during
  implementation, after the code skeleton exists.

---

## 10. Defaults locked in
- Region default: **`eu`** (`eu1.unione.io`).
- Send default: **real send requires `confirm_send=true`**; sandbox flag available.
- KB depth: **curated essentials** bundled offline; live fetch for the rest.
- Package: `mcp_unione`; repo: `karimou5/mcp-unione` (public).

---

## 11. Build sequence (high level — detailed plan to follow)
1. Project skeleton (`pyproject.toml`, package layout, config, client, errors).
2. `data/` generation: build `kb/`, `manifest.json`, `errors.json`, `statuses.json` from `research/`.
3. Tools per domain (TDD: test → implement), starting with `system/ping` + `email/send` (guard).
4. Docs tools + resources + prompts.
5. CI workflow + tests green.
6. GitHub repo: create, publish public, protect `main`, wire release-please.
