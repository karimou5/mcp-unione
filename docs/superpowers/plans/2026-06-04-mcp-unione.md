# MCP UniOne Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Python FastMCP server exposing 30 typed UniOne transactional-API tools plus a hybrid offline knowledge base (resources + search + lookups), in the public repo `karimou5/mcp-unione` with protected `main` and release-please.

**Architecture:** A FastMCP server (`stdio`) with a thin async httpx client (`client.py`) shared by per-domain tool modules under `tools/`. Configuration comes from env (`UNIONE_API_KEY`, `UNIONE_REGION` default `eu`). A curated knowledge base, generated from `docs/superpowers/research/` into `src/mcp_unione/data/`, is exposed as MCP resources and four docs tools. Errors map UniOne's ~300 codes to a typed `UniOneError`. Tests mock httpx with `respx` — zero real API calls.

**Tech Stack:** Python ≥3.11, uv, `mcp[cli]` (FastMCP), httpx, pydantic v2, pytest + pytest-asyncio + respx, ruff, GitHub Actions, release-please.

**Authority for params/enums/errors:** `docs/superpowers/research/0{1..5}-*.md` (committed). When a task says "all fields per research", use those files verbatim.

---

## File structure (locked)

```
src/mcp_unione/
  __init__.py            # __version__
  __main__.py            # CLI entry → build_server().run()
  config.py              # Settings (env) + region→base_url
  client.py              # UniOneClient.post(path, payload) async
  errors.py              # UniOneError + load errors.json enrichment
  models.py              # Pydantic: Recipient, Attachment, Body, SendMessage, Template…
  server.py              # build_server(): FastMCP + register everything
  docs_tools.py          # search_docs, fetch_doc_page, lookup_error, lookup_status
  resources.py           # register unione-docs://{slug}
  prompts.py             # compose_transactional_email, diagnose_delivery
  tools/
    __init__.py          # register_all(mcp, client)
    system.py email.py validation.py template.py webhook.py
    suppression.py domain.py event_dump.py tag.py project.py
  data/
    kb/<slug>.md         # 20 curated pages
    manifest.json errors.json statuses.json
scripts/build_kb.py      # regenerate data/ from research/
tests/                   # conftest.py + test_*.py mirroring modules
.github/workflows/ci.yml
pyproject.toml README.md .env.example LICENSE
```

---

## Phase 0 — Skeleton

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`, `src/mcp_unione/__init__.py`, `.env.example`, `README.md`, `LICENSE`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "mcp-unione"
version = "0.1.0"
description = "MCP server (FastMCP) for UniOne / Unisender Go: transactional API tools + offline knowledge base."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = ["mcp[cli]>=1.2.0", "httpx>=0.27", "pydantic>=2.6"]

[project.scripts]
mcp-unione = "mcp_unione.__main__:main"

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.23", "respx>=0.21", "ruff>=0.6"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_unione"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: Write `src/mcp_unione/__init__.py`**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Write `.env.example`**

```bash
# UniOne API key — https://cp.unione.io/en/user/info/api
UNIONE_API_KEY=
# Region: eu (default) | us | global
UNIONE_REGION=eu
# Optional full base-URL override (wins over region)
# UNIONE_BASE_URL=
# Request timeout, seconds
UNIONE_TIMEOUT=30
```

- [ ] **Step 4: Write a minimal `README.md`** (project intro + `uv sync` + Claude config snippet placeholder) and a standard MIT `LICENSE` (year 2026, holder "karimou5").

- [ ] **Step 5: Create env + verify install**

Run: `uv sync --extra dev`
Expected: resolves and installs `mcp`, `httpx`, `pydantic`, dev tools; no error.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/mcp_unione/__init__.py .env.example README.md LICENSE
git commit -m "chore: project scaffold (pyproject, package, env example)"
```

---

### Task 2: `config.py`

**Files:**
- Create: `src/mcp_unione/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
import importlib
import pytest
from mcp_unione.config import Settings

def test_region_eu_default(monkeypatch):
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    monkeypatch.setenv("UNIONE_REGION", "eu")
    s = Settings.from_env()
    assert s.base_url == "https://eu1.unione.io/en/transactional/api/v1"

def test_region_us(monkeypatch):
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    monkeypatch.setenv("UNIONE_REGION", "us")
    assert Settings.from_env().base_url.startswith("https://us1.unione.io")

def test_base_url_override_wins(monkeypatch):
    monkeypatch.setenv("UNIONE_REGION", "eu")
    monkeypatch.setenv("UNIONE_BASE_URL", "https://x.example/api/v1")
    assert Settings.from_env().base_url == "https://x.example/api/v1"

def test_default_region_when_unset(monkeypatch):
    monkeypatch.delenv("UNIONE_REGION", raising=False)
    monkeypatch.delenv("UNIONE_BASE_URL", raising=False)
    assert "eu1.unione.io" in Settings.from_env().base_url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL (`ModuleNotFoundError`/`AttributeError`).

- [ ] **Step 3: Implement**

```python
from __future__ import annotations
import os
from dataclasses import dataclass

_REGIONS = {
    "eu": "https://eu1.unione.io",
    "us": "https://us1.unione.io",
    "global": "https://api.unione.io",
}
_PATH = "/en/transactional/api/v1"

@dataclass(frozen=True)
class Settings:
    api_key: str | None
    base_url: str
    timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        override = os.getenv("UNIONE_BASE_URL")
        region = (os.getenv("UNIONE_REGION") or "eu").lower()
        host = _REGIONS.get(region, _REGIONS["eu"])
        base_url = override.rstrip("/") if override else host + _PATH
        timeout = float(os.getenv("UNIONE_TIMEOUT") or "30")
        return cls(api_key=os.getenv("UNIONE_API_KEY"), base_url=base_url, timeout=timeout)
```

- [ ] **Step 4: Run tests** → `uv run pytest tests/test_config.py -v` → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: config from env with eu default region"`

---

### Task 3: `errors.py`

**Files:**
- Create: `src/mcp_unione/errors.py`
- Test: `tests/test_errors.py`

- [ ] **Step 1: Failing test**

```python
from mcp_unione.errors import UniOneError, enrich

def test_error_str_includes_code_and_message():
    e = UniOneError(code=101, message="api_key not found", http_status=400)
    assert "101" in str(e) and "api_key not found" in str(e)

def test_enrich_adds_fix_when_known(tmp_path, monkeypatch):
    # enrich() reads the bundled errors.json; unknown codes return base dict unchanged
    out = enrich(999999, "boom", 400)
    assert out["code"] == 999999 and out["message"] == "boom"
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
from __future__ import annotations
import json
from functools import lru_cache
from importlib.resources import files

class UniOneError(Exception):
    def __init__(self, code: int | str, message: str, http_status: int | None = None, fix: str | None = None):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.fix = fix
        super().__init__(f"UniOne error {code} (HTTP {http_status}): {message}")

    def as_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message,
                          "http_status": self.http_status, "fix": self.fix}}

@lru_cache(maxsize=1)
def _table() -> dict:
    try:
        return json.loads(files("mcp_unione.data").joinpath("errors.json").read_text("utf-8"))
    except Exception:
        return {}

def enrich(code, message: str, http_status: int | None) -> dict:
    info = _table().get(str(code), {})
    return {"code": code, "message": message, "http_status": http_status, "fix": info.get("fix")}
```

- [ ] **Step 4: Run** → PASS (errors.json may be absent now; `_table()` returns `{}`).
- [ ] **Step 5: Commit** → `git commit -am "feat: UniOneError + error-code enrichment"`

---

### Task 4: `client.py`

**Files:**
- Create: `src/mcp_unione/client.py`
- Test: `tests/test_client.py`

- [ ] **Step 1: Failing test (respx-mocked)**

```python
import httpx, pytest, respx
from mcp_unione.client import UniOneClient
from mcp_unione.config import Settings
from mcp_unione.errors import UniOneError

def _client(key="k"):
    return UniOneClient(Settings(api_key=key, base_url="https://eu1.unione.io/en/transactional/api/v1", timeout=5))

@respx.mock
async def test_post_sends_api_key_and_returns_json():
    route = respx.post("https://eu1.unione.io/en/transactional/api/v1/system/ping.json").mock(
        return_value=httpx.Response(200, json={"status": "success"}))
    out = await _client().post("system/ping.json", {})
    assert out == {"status": "success"}
    assert route.calls.last.request.headers["X-API-KEY"] == "k"

@respx.mock
async def test_error_body_raises_unione_error():
    respx.post(url__regex=r".*/email/send.json").mock(
        return_value=httpx.Response(400, json={"status": "error", "code": 101, "message": "bad key"}))
    with pytest.raises(UniOneError) as ei:
        await _client().post("email/send.json", {})
    assert ei.value.code == 101

async def test_missing_api_key_raises():
    with pytest.raises(UniOneError) as ei:
        await _client(key=None).post("system/info.json", {})
    assert "api key" in str(ei.value).lower()
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
from __future__ import annotations
import httpx
from .config import Settings
from .errors import UniOneError

class UniOneClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def post(self, path: str, payload: dict) -> dict:
        if not self.settings.api_key:
            raise UniOneError(code="no_api_key", message="Missing API key: set UNIONE_API_KEY.", http_status=None)
        url = f"{self.settings.base_url}/{path.lstrip('/')}"
        headers = {"X-API-KEY": self.settings.api_key, "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.settings.timeout) as c:
                resp = await c.post(url, json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise UniOneError(code="transport", message=f"Network error: {e}", http_status=None) from e
        try:
            data = resp.json()
        except ValueError:
            raise UniOneError(code="bad_response", message=resp.text[:300], http_status=resp.status_code)
        if resp.status_code >= 400 or (isinstance(data, dict) and data.get("status") == "error"):
            code = data.get("code", resp.status_code) if isinstance(data, dict) else resp.status_code
            msg = data.get("message", "error") if isinstance(data, dict) else "error"
            from .errors import enrich
            raise UniOneError(code=code, message=msg, http_status=resp.status_code, fix=enrich(code, msg, resp.status_code)["fix"])
        return data
```

- [ ] **Step 4: Run** → `uv run pytest tests/test_client.py -v` → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: async UniOne httpx client with error mapping"`

---

### Task 5: `server.py` + `__main__.py` (skeleton)

**Files:**
- Create: `src/mcp_unione/server.py`, `src/mcp_unione/__main__.py`, `src/mcp_unione/tools/__init__.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Failing test**

```python
from mcp_unione.server import build_server

async def test_server_builds_and_lists_tools():
    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "unione_system_ping" in names  # registered in Task 6
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** (`tools/__init__.py` `register_all` is filled in later tasks; start with system only import-safe)

```python
# server.py
from mcp.server.fastmcp import FastMCP
from .config import Settings
from .client import UniOneClient
from . import tools, docs_tools, resources, prompts

def build_server() -> FastMCP:
    mcp = FastMCP("unione")
    client = UniOneClient(Settings.from_env())
    tools.register_all(mcp, client)
    docs_tools.register(mcp, client)
    resources.register(mcp)
    prompts.register(mcp)
    return mcp
```

```python
# __main__.py
from .server import build_server

def main() -> None:
    build_server().run()  # stdio by default

if __name__ == "__main__":
    main()
```

```python
# tools/__init__.py
from . import system  # add domains here as implemented

def register_all(mcp, client) -> None:
    system.register(mcp, client)
    # email.register(mcp, client) ... (added per task)
```

> Note: `docs_tools`, `resources`, `prompts` must exist as import-safe stubs with a `register(...)` no-op until their tasks. Create one-line stubs now:
> ```python
> def register(mcp, client=None): ...
> ```

- [ ] **Step 4: Run** → still FAIL until Task 6 adds `system`. Create the `system` stub now returning nothing, then the test asserts after Task 6. For Task 5, weaken assertion to `isinstance(names, set)` then restore in Task 6. **Step 4 expected: PASS** with weakened assertion.
- [ ] **Step 5: Commit** → `git commit -am "feat: FastMCP server skeleton + stdio entrypoint"`

---

## Phase 1 — Data / knowledge base

### Task 6: `scripts/build_kb.py` + generated `data/`

**Files:**
- Create: `scripts/build_kb.py`, `src/mcp_unione/data/kb/*.md`, `data/manifest.json`, `data/errors.json`, `data/statuses.json`
- Test: `tests/test_data.py`

- [ ] **Step 1: Failing test**

```python
import json
from importlib.resources import files

def _d(name): return files("mcp_unione.data").joinpath(name).read_text("utf-8")

def test_manifest_has_expected_slugs():
    m = json.loads(_d("manifest.json"))
    slugs = {e["slug"] for e in m}
    assert {"web-api-reference", "email-send-params", "template-velocity",
            "email-statuses", "error-codes", "suppression-lists"} <= slugs

def test_errors_table_nonempty_and_has_101():
    e = json.loads(_d("errors.json"))
    assert "101" in e and "fix" in e["101"]

def test_statuses_has_delivered_and_extended():
    s = json.loads(_d("statuses.json"))
    assert "delivered" in s["statuses"] and "err_user_unknown" in s["delivery_status"]
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement `scripts/build_kb.py`**

The script reads `docs/superpowers/research/0{1..5}-*.md` and writes the 20 KB pages, `manifest.json`, `errors.json`, `statuses.json`. Concretely:
  - **kb/<slug>.md**: split the research files into the 20 slugs listed in the spec §5.2. Each page begins with:
    `---\ntitle: <Title>\nsource: https://docs.unione.io/en/<docslug>\nsynced: 2026-06-04\n---\n` followed by the relevant curated section.
  - **manifest.json**: `[{"slug","title","url","keywords":[...],"summary":"..."}]` — one entry per kb page; keywords derived from the page headings.
  - **errors.json**: parse the markdown error-code table in `research/01-api-reference.md` (columns code | http | meaning | fix) into `{ "<code>": {"http":<int>,"message":"...","fix":"..."} }`.
  - **statuses.json**: `{"statuses": {<name>: <desc>}, "delivery_status": {<code>: <desc>}, "blocking_reasons": {...}, "validation": {...}, "suppression_cause": {...}}` parsed from `research/03` and `research/05`.

Provide a deterministic parser (regex on `| ... |` table rows; fall back to a committed hand-curated JSON if a table row is malformed). The script is idempotent: `uv run python scripts/build_kb.py` regenerates all of `data/`.

> Implementation detail: the parser must handle the `research/01` table which spans codes 101–10009. If automated parsing is brittle, the engineer should generate a first pass with the script, then commit the JSON; the JSON (not the parsing) is the runtime artifact.

- [ ] **Step 4: Run the generator then the tests**

Run: `uv run python scripts/build_kb.py && uv run pytest tests/test_data.py -v`
Expected: data files written; tests PASS.

- [ ] **Step 5: Commit** → `git add scripts/build_kb.py src/mcp_unione/data && git commit -m "feat: generate curated KB, error table, status maps from research"`

---

## Phase 2 — API tools (TDD, one domain per task)

**Shared tool pattern** (every tool follows this; shown once):

```python
# tools/<domain>.py
def register(mcp, client):
    @mcp.tool()
    async def unione_<name>(<typed args>) -> dict:
        """<docstring from research: what it does + key params/enums>"""
        payload = { ... }                      # exact body per research/Postman
        return await client.post("<path>.json", payload)
```

Each task: (1) write a respx test asserting the exact path + payload for a representative tool, (2) run→fail, (3) implement all tools in the domain, (4) register in `tools/__init__.py`, (5) run→pass, (6) commit. Tests reuse a `conftest.py` fixture.

- [ ] **Task 6.5: `tests/conftest.py`** — shared fixtures:

```python
import httpx, pytest, respx
from mcp.server.fastmcp import FastMCP
from mcp_unione.client import UniOneClient
from mcp_unione.config import Settings

@pytest.fixture
def client():
    return UniOneClient(Settings(api_key="k", base_url="https://eu1.unione.io/en/transactional/api/v1", timeout=5))

@pytest.fixture
def base():
    return "https://eu1.unione.io/en/transactional/api/v1"

async def call_tool(mcp: FastMCP, name: str, args: dict):
    return await mcp.call_tool(name, args)
```

Commit conftest before the tool tasks.

### Task 7: `system` tools (ping, info)

**Files:** Create `src/mcp_unione/tools/system.py`; Test `tests/test_system.py`. Restore the strong assertion in `tests/test_server.py` (Task 5).

- [ ] **Step 1: Failing test**

```python
import httpx, respx
from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import system

@respx.mock
async def test_ping(client, base):
    r = respx.post(f"{base}/system/ping.json").mock(return_value=httpx.Response(200, json={"status":"success"}))
    mcp = FastMCP("t"); system.register(mcp, client)
    out = await mcp.call_tool("unione_system_ping", {})
    assert r.called
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_system_ping() -> dict:
        """Health check. POST system/ping.json (no params). Returns {status:'success'}."""
        return await client.post("system/ping.json", {})

    @mcp.tool()
    async def unione_system_info() -> dict:
        """Account/limits info. POST system/info.json (no params)."""
        return await client.post("system/info.json", {})
```

- [ ] **Step 4: Run** `uv run pytest tests/test_system.py tests/test_server.py -v` → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: system ping/info tools"`

### Task 8: `email` tools — `unione_send_email` (with guard) + `unione_subscribe`

**Files:** Create `src/mcp_unione/tools/email.py`, add models to `src/mcp_unione/models.py`; Test `tests/test_email.py`. Register in `tools/__init__.py`.

- [ ] **Step 1: Failing tests (guard + real send + subscribe)**

```python
import httpx, respx
from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import email

def _mcp(client):
    m = FastMCP("t"); email.register(m, client); return m

@respx.mock
async def test_send_guard_blocks_without_confirm(client, base):
    route = respx.post(f"{base}/email/send.json")
    m = _mcp(client)
    out = await m.call_tool("unione_send_email", {
        "recipients":[{"email":"a@b.com"}], "subject":"Hi",
        "from_email":"s@d.com", "body":{"html":"<b>hi</b>"}})
    assert route.called is False  # no real send

@respx.mock
async def test_send_real_with_confirm(client, base):
    route = respx.post(f"{base}/email/send.json").mock(
        return_value=httpx.Response(200, json={"status":"success","job_id":"J","emails":["a@b.com"]}))
    m = _mcp(client)
    out = await m.call_tool("unione_send_email", {
        "recipients":[{"email":"a@b.com"}], "subject":"Hi",
        "from_email":"s@d.com", "body":{"html":"<b>hi</b>"}, "confirm_send": True})
    assert route.called
    body = route.calls.last.request.content
    assert b"a@b.com" in body and b"\"from_email\": \"s@d.com\"" in body

@respx.mock
async def test_subscribe(client, base):
    route = respx.post(f"{base}/email/subscribe.json").mock(return_value=httpx.Response(200, json={"status":"success"}))
    m = _mcp(client)
    await m.call_tool("unione_subscribe", {"from_email":"s@d.com","to_email":"u@x.com"})
    assert route.called
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement `models.py`** (Pydantic v2) and `tools/email.py`.

`models.py` — define exactly these (fields/enums per `research/01-api-reference.md §email/send`):

```python
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field

class Recipient(BaseModel):
    email: str
    substitutions: dict | None = None
    metadata: dict | None = None

class Attachment(BaseModel):
    type: str
    name: str
    content: str  # base64

class Body(BaseModel):
    html: str | None = None
    plaintext: str | None = None
    amp: str | None = None

Engine = Literal["simple", "velocity", "liquid", "none"]
```

`tools/email.py`:

```python
import logging
from typing import Optional
from ..models import Recipient, Attachment, Body, Engine

log = logging.getLogger("mcp_unione")

def register(mcp, client):
    @mcp.tool()
    async def unione_send_email(
        recipients: list[Recipient],
        subject: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        reply_to_name: str | None = None,
        body: Body | None = None,
        template_id: str | None = None,
        template_engine: Engine = "simple",
        global_substitutions: dict | None = None,
        global_metadata: dict | None = None,
        global_language: str | None = None,
        tags: list[str] | None = None,
        headers: dict | None = None,
        attachments: list[Attachment] | None = None,
        inline_attachments: list[Attachment] | None = None,
        track_links: int = 1,
        track_read: int = 1,
        skip_unsubscribe: int = 0,
        bypass_global: int = 0,
        bypass_unavailable: int = 0,
        bypass_unsubscribed: int = 0,
        bypass_complained: int = 0,
        idempotence_key: str | None = None,
        sandbox: bool = False,
        confirm_send: bool = False,
    ) -> dict:
        """Send a transactional email via UniOne email/send.json.

        SAFETY: real sends require confirm_send=true. Without it, returns a preview
        and sends nothing. body OR template_id is required. ≤500 recipients.
        template_engine: simple|velocity|liquid|none. Unsubscribe token:
        {{UnsubscribeUrl}} (simple) / $UnsubscribeUrl (velocity).
        """
        if not body and not template_id:
            return {"error": "Provide either `body` or `template_id`."}
        if len(recipients) > 500:
            return {"error": "UniOne allows at most 500 recipients per send."}
        message = {
            "recipients": [r.model_dump(exclude_none=True) for r in recipients],
            "template_engine": template_engine,
            "track_links": track_links, "track_read": track_read,
            "skip_unsubscribe": skip_unsubscribe,
            "bypass_global": bypass_global, "bypass_unavailable": bypass_unavailable,
            "bypass_unsubscribed": bypass_unsubscribed, "bypass_complained": bypass_complained,
        }
        opt = {
            "subject": subject, "from_email": from_email, "from_name": from_name,
            "reply_to": reply_to, "reply_to_name": reply_to_name,
            "template_id": template_id, "global_language": global_language,
            "global_substitutions": global_substitutions, "global_metadata": global_metadata,
            "tags": tags, "headers": headers,
            "body": body.model_dump(exclude_none=True) if body else None,
            "attachments": [a.model_dump() for a in attachments] if attachments else None,
            "inline_attachments": [a.model_dump() for a in inline_attachments] if inline_attachments else None,
            "idempotence_key": idempotence_key,
        }
        message.update({k: v for k, v in opt.items() if v is not None})
        if sandbox:
            message.setdefault("options", {})["sandbox"] = True  # routed to sandbox domain
        to = [r.email for r in recipients]
        if not confirm_send:
            return {"preview": True, "would_send": True, "from_email": from_email,
                    "to": to, "subject": subject, "engine": template_engine,
                    "recipient_count": len(to),
                    "note": "Dry run. Re-call with confirm_send=true to actually send."}
        log.info("UniOne send → %d recipient(s): %s", len(to), ", ".join(to))
        return await client.post("email/send.json", {"message": message})

    @mcp.tool()
    async def unione_subscribe(from_email: str, to_email: str, from_name: str | None = None) -> dict:
        """Send a double opt-in subscription confirmation. POST email/subscribe.json."""
        payload = {"from_email": from_email, "to_email": to_email}
        if from_name:
            payload["from_name"] = from_name
        return await client.post("email/subscribe.json", payload)
```

Add `email.register(mcp, client)` to `tools/__init__.py:register_all`.

- [ ] **Step 4: Run** `uv run pytest tests/test_email.py -v` → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: email send (with send-guard) + subscribe tools"`

### Task 9: `validation` tool

**Files:** Create `tools/validation.py`; Test `tests/test_validation.py`; register.

- [ ] Test asserts `POST email-validation/single.json` with `{"email": "..."}`. Implement:

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_validate_email(email: str) -> dict:
        """Validate one address (email-validation/single.json). Response result:
        valid|invalid|suspicious|unknown, plus cause, validity (0-100), mx_found, did_you_mean."""
        return await client.post("email-validation/single.json", {"email": email})
```
Run → PASS → commit `feat: email validation tool`.

### Task 10: `template` tools (set/get/list/delete)

**Files:** `tools/template.py`; `tests/test_template.py`; add `Template` model if useful; register.

- [ ] Tests assert the 4 paths. Implement (params per `research/01`):

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_template_set(name: str, body: dict, subject: str | None = None,
        template_engine: str = "simple", from_email: str | None = None, from_name: str | None = None,
        reply_to: str | None = None, global_substitutions: dict | None = None,
        global_metadata: dict | None = None, headers: dict | None = None,
        attachments: list[dict] | None = None, inline_attachments: list[dict] | None = None,
        template_id: str | None = None) -> dict:
        """Create/update a template (template/set.json). Pass template_id to update."""
        tpl = {"name": name, "template_engine": template_engine, "body": body}
        for k, v in {"subject":subject,"from_email":from_email,"from_name":from_name,"reply_to":reply_to,
                     "global_substitutions":global_substitutions,"global_metadata":global_metadata,
                     "headers":headers,"attachments":attachments,"inline_attachments":inline_attachments,
                     "id":template_id}.items():
            if v is not None: tpl[k] = v
        return await client.post("template/set.json", {"template": tpl})

    @mcp.tool()
    async def unione_template_get(id: str) -> dict:
        """Get a template by id (template/get.json)."""
        return await client.post("template/get.json", {"id": id})

    @mcp.tool()
    async def unione_template_list(limit: int = 50, offset: int = 0) -> dict:
        """List templates (template/list.json)."""
        return await client.post("template/list.json", {"limit": limit, "offset": offset})

    @mcp.tool()
    async def unione_template_delete(id: str) -> dict:
        """Delete a template by id (template/delete.json)."""
        return await client.post("template/delete.json", {"id": id})
```
Run → PASS → commit `feat: template tools`.

### Task 11: `webhook` tools (set/get/list/delete)

**Files:** `tools/webhook.py`; `tests/test_webhook.py`; register. Enums per `research/03`.

- [ ] Implement:

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_webhook_set(url: str, events: dict, status: str = "active",
        event_format: str = "json_post", delivery_info: int = 1, single_event: int = 0,
        max_parallel: int = 10) -> dict:
        """Create/update a webhook (webhook/set.json).
        status: active|disabled|stopped. event_format: json_post|json_post_gzip.
        events: {"email_status":[delivered,opened,clicked,unsubscribed,subscribed,
        soft_bounced,hard_bounced,spam], "spam_block":["*"]}."""
        return await client.post("webhook/set.json", {"url": url, "events": events,
            "status": status, "event_format": event_format, "delivery_info": delivery_info,
            "single_event": single_event, "max_parallel": max_parallel})

    @mcp.tool()
    async def unione_webhook_get(url: str) -> dict:
        """Get a webhook by url (webhook/get.json)."""
        return await client.post("webhook/get.json", {"url": url})

    @mcp.tool()
    async def unione_webhook_list(limit: int = 50, offset: int = 0) -> dict:
        """List webhooks (webhook/list.json)."""
        return await client.post("webhook/list.json", {"limit": limit, "offset": offset})

    @mcp.tool()
    async def unione_webhook_delete(url: str) -> dict:
        """Delete a webhook by url (webhook/delete.json)."""
        return await client.post("webhook/delete.json", {"url": url})
```
Run → PASS → commit `feat: webhook tools`.

### Task 12: `suppression` tools (set/get/list/delete)

**Files:** `tools/suppression.py`; `tests/test_suppression.py`; register. Enums per `research/05`.

- [ ] Implement:

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_suppression_set(email: str, cause: str, created: str | None = None) -> dict:
        """Add to suppression list (suppression/set.json).
        cause: unsubscribed|temporary_unavailable|permanent_unavailable|complained."""
        p = {"email": email, "cause": cause}
        if created: p["created"] = created
        return await client.post("suppression/set.json", p)

    @mcp.tool()
    async def unione_suppression_get(email: str, all_projects: bool = False) -> dict:
        """Check suppression status for an address (suppression/get.json)."""
        return await client.post("suppression/get.json", {"email": email, "all_projects": all_projects})

    @mcp.tool()
    async def unione_suppression_list(cause: str | None = None, source: str | None = None,
        start_time: str | None = None, cursor: str | None = None, limit: int = 50) -> dict:
        """List suppressions with cursor pagination (suppression/list.json).
        source: user|system|subscriber."""
        p = {"limit": limit}
        for k, v in {"cause":cause,"source":source,"start_time":start_time,"cursor":cursor}.items():
            if v is not None: p[k] = v
        return await client.post("suppression/list.json", p)

    @mcp.tool()
    async def unione_suppression_delete(email: str) -> dict:
        """Remove an address from the suppression list (suppression/delete.json)."""
        return await client.post("suppression/delete.json", {"email": email})
```
Run → PASS → commit `feat: suppression tools`.

### Task 13: `domain` tools (get_dns_records/validate_verification_record/validate_dkim/list/delete)

**Files:** `tools/domain.py`; `tests/test_domain.py`; register. Details per `research/04`.

- [ ] Implement (each posts `{"domain": ...}`, list adds limit/offset):

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_domain_get_dns_records(domain: str) -> dict:
        """Get required DNS records (domain/get-dns-records.json). Returns verification-record
        and dkim (key part only — prepend 'v=DKIM1; k=rsa; p=' for the published value; selector us._domainkey)."""
        return await client.post("domain/get-dns-records.json", {"domain": domain})

    @mcp.tool()
    async def unione_domain_validate_verification_record(domain: str) -> dict:
        """Re-validate the ownership TXT record (domain/validate-verification-record.json)."""
        return await client.post("domain/validate-verification-record.json", {"domain": domain})

    @mcp.tool()
    async def unione_domain_validate_dkim(domain: str) -> dict:
        """Re-validate DKIM (domain/validate-dkim.json). Async: 200 means validation started."""
        return await client.post("domain/validate-dkim.json", {"domain": domain})

    @mcp.tool()
    async def unione_domain_list(domain: str | None = None, limit: int = 50, offset: int = 0) -> dict:
        """List domains + verification/dkim status (domain/list.json)."""
        p = {"limit": limit, "offset": offset}
        if domain: p["domain"] = domain
        return await client.post("domain/list.json", p)

    @mcp.tool()
    async def unione_domain_delete(domain: str) -> dict:
        """Delete a domain (domain/delete.json)."""
        return await client.post("domain/delete.json", {"domain": domain})
```
Run → PASS → commit `feat: domain tools`.

### Task 14: `event_dump` tools (create/get/list/delete)

**Files:** `tools/event_dump.py`; `tests/test_event_dump.py`; register. Filter object per `research/01`.

- [ ] Implement:

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_event_dump_create(start_time: str | None = None, end_time: str | None = None,
        limit: int | None = None, all_projects: bool = False, filter: dict | None = None,
        delimiter: str = ";", format: str = "csv") -> dict:
        """Create a CSV event export (event-dump/create.json). filter supports job_id, status,
        delivery_status, email, email_from, domain, campaign_id."""
        p = {"all_projects": all_projects, "delimiter": delimiter, "format": format}
        for k, v in {"start_time":start_time,"end_time":end_time,"limit":limit,"filter":filter}.items():
            if v is not None: p[k] = v
        return await client.post("event-dump/create.json", p)

    @mcp.tool()
    async def unione_event_dump_get(dump_id: str) -> dict:
        """Get an export's status/URL (event-dump/get.json)."""
        return await client.post("event-dump/get.json", {"dump_id": dump_id})

    @mcp.tool()
    async def unione_event_dump_list() -> dict:
        """List event exports (event-dump/list.json)."""
        return await client.post("event-dump/list.json", {})

    @mcp.tool()
    async def unione_event_dump_delete(dump_id: str) -> dict:
        """Delete an export (event-dump/delete.json)."""
        return await client.post("event-dump/delete.json", {"dump_id": dump_id})
```
Run → PASS → commit `feat: event-dump tools`.

### Task 15: `tag` + `project` tools

**Files:** `tools/tag.py`, `tools/project.py`; tests `tests/test_tag.py`, `tests/test_project.py`; register both.

- [ ] Implement `tag.py`:

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_tag_list() -> dict:
        """List tags (tag/list.json)."""
        return await client.post("tag/list.json", {})

    @mcp.tool()
    async def unione_tag_delete(tag_id: int) -> dict:
        """Delete a tag by id (tag/delete.json)."""
        return await client.post("tag/delete.json", {"tag_id": tag_id})
```

- [ ] Implement `project.py` (project object per `research/05`):

```python
def register(mcp, client):
    @mcp.tool()
    async def unione_project_create(name: str, country: str | None = None, send_enabled: bool = True,
        custom_unsubscribe_url_enabled: bool = False, backend_id: int | None = None) -> dict:
        """Create a project (project/create.json). Returns project_id + project_api_key."""
        proj = {"name": name, "send_enabled": send_enabled,
                "custom_unsubscribe_url_enabled": custom_unsubscribe_url_enabled}
        if country: proj["country"] = country
        if backend_id is not None: proj["backend_id"] = backend_id
        return await client.post("project/create.json", {"project": proj})

    @mcp.tool()
    async def unione_project_update(project_id: str, project: dict) -> dict:
        """Update a project (project/update.json)."""
        return await client.post("project/update.json", {"project_id": project_id, "project": project})

    @mcp.tool()
    async def unione_project_list(project_id: str | None = None) -> dict:
        """List projects (project/list.json)."""
        return await client.post("project/list.json", {"project_id": project_id} if project_id else {})

    @mcp.tool()
    async def unione_project_delete(project_id: str) -> dict:
        """Delete a project (project/delete.json)."""
        return await client.post("project/delete.json", {"project_id": project_id})
```
Run both test files → PASS → commit `feat: tag + project tools`.

---

## Phase 3 — Documentation layer

### Task 16: `docs_tools.py` (search_docs, fetch_doc_page, lookup_error, lookup_status)

**Files:** Create `src/mcp_unione/docs_tools.py`; Test `tests/test_docs_tools.py`.

- [ ] **Step 1: Failing tests**

```python
import httpx, respx
from mcp.server.fastmcp import FastMCP
from mcp_unione import docs_tools

def _mcp():
    m = FastMCP("t"); docs_tools.register(m, None); return m

async def test_search_docs_finds_webhook():
    out = await _mcp().call_tool("unione_search_docs", {"query": "webhook events spam_block"})
    text = str(out)
    assert "webhook" in text.lower()

async def test_lookup_error_known_code():
    out = await _mcp().call_tool("unione_lookup_error", {"code": 101})
    assert "101" in str(out)

async def test_lookup_status_delivered():
    out = await _mcp().call_tool("unione_lookup_status", {"status": "delivered"})
    assert "deliver" in str(out).lower()

@respx.mock
async def test_fetch_doc_page_live():
    respx.get(url__regex=r"https://docs\.unione\.io/en/email-statuses").mock(
        return_value=httpx.Response(200, html="<html><body><h1>Email statuses</h1></body></html>"))
    out = await _mcp().call_tool("unione_fetch_doc_page", {"slug_or_url": "email-statuses"})
    assert "Email statuses" in str(out)
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
from __future__ import annotations
import json, re
import httpx
from importlib.resources import files

def _data(name): return files("mcp_unione.data").joinpath(name).read_text("utf-8")

def _manifest(): return json.loads(_data("manifest.json"))

def _kb_text(slug: str) -> str:
    return files("mcp_unione.data").joinpath("kb", f"{slug}.md").read_text("utf-8")

def _score(entry: dict, terms: list[str]) -> int:
    hay = (entry["title"] + " " + " ".join(entry.get("keywords", [])) + " " + entry.get("summary","")).lower()
    return sum(hay.count(t) for t in terms)

def register(mcp, client=None):
    @mcp.tool()
    async def unione_search_docs(query: str, limit: int = 5) -> dict:
        """Search the bundled UniOne knowledge base. Returns matching pages with slug,
        title, url, and a short snippet. Use unione_fetch_doc_page or the resource for full text."""
        terms = [t for t in re.split(r"\W+", query.lower()) if t]
        scored = sorted(((_score(e, terms), e) for e in _manifest()), key=lambda x: x[0], reverse=True)
        hits = []
        for s, e in scored[:limit]:
            if s == 0 and hits: break
            body = _kb_text(e["slug"])
            snippet = next((ln for ln in body.splitlines() if any(t in ln.lower() for t in terms)), e.get("summary",""))
            hits.append({"slug": e["slug"], "title": e["title"], "url": e["url"],
                         "resource": f"unione-docs://{e['slug']}", "snippet": snippet[:300]})
        return {"query": query, "results": hits}

    @mcp.tool()
    async def unione_fetch_doc_page(slug_or_url: str) -> dict:
        """Fetch a live UniOne docs page (markdown-ish text). Accepts a slug
        (e.g. 'email-statuses') or a full https://docs.unione.io/en/... URL."""
        url = slug_or_url if slug_or_url.startswith("http") else f"https://docs.unione.io/en/{slug_or_url}"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
            r = await c.get(url)
        text = re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+\n", "\n", re.sub(r"[ \t]+", " ", text))
        return {"url": url, "status": r.status_code, "text": text.strip()[:20000]}

    @mcp.tool()
    async def unione_lookup_error(code: int | str) -> dict:
        """Explain a UniOne API error code (from the bundled error table)."""
        table = json.loads(_data("errors.json"))
        info = table.get(str(code))
        return {"code": code, **info} if info else {"code": code, "message": "Unknown code.", "fix": None}

    @mcp.tool()
    async def unione_lookup_status(status: str) -> dict:
        """Explain an email status or extended delivery_status code."""
        s = json.loads(_data("statuses.json"))
        for bucket in ("statuses", "delivery_status", "blocking_reasons", "validation", "suppression_cause"):
            if status in s.get(bucket, {}):
                return {"status": status, "category": bucket, "meaning": s[bucket][status]}
        return {"status": status, "meaning": "Unknown status."}
```

- [ ] **Step 4: Run** `uv run pytest tests/test_docs_tools.py -v` → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: docs tools (search, live fetch, error/status lookup)"`

### Task 17: `resources.py` (KB as `unione-docs://{slug}`)

**Files:** Create `src/mcp_unione/resources.py`; Test `tests/test_resources.py`.

- [ ] **Step 1: Failing test**

```python
from mcp.server.fastmcp import FastMCP
from mcp_unione import resources

async def test_lists_and_reads_resource():
    m = FastMCP("t"); resources.register(m)
    res = await m.list_resources()
    uris = {str(r.uri) for r in res}
    assert any(u.startswith("unione-docs://") for u in uris)
    content = await m.read_resource("unione-docs://email-statuses")
    assert "status" in str(content).lower()
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
from __future__ import annotations
import json
from importlib.resources import files

def _manifest():
    return json.loads(files("mcp_unione.data").joinpath("manifest.json").read_text("utf-8"))

def register(mcp, client=None):
    # one static resource per KB page (for listing) + a templated reader
    for e in _manifest():
        slug, title = e["slug"], e["title"]
        uri = f"unione-docs://{slug}"
        def _make(slug):
            def _read() -> str:
                return files("mcp_unione.data").joinpath("kb", f"{slug}.md").read_text("utf-8")
            return _read
        mcp.add_resource_fn(_make(slug), uri=uri, name=title,
                            description=e.get("summary",""), mime_type="text/markdown")
```

> If the installed FastMCP version lacks `add_resource_fn`, use the decorator form:
> `@mcp.resource("unione-docs://{slug}")` with a function `def read_doc(slug: str) -> str: ...`
> plus a separate `@mcp.tool()`/`list_resources` override. Pick whichever the pinned `mcp`
> version supports; the test above is the contract. Verify the exact API with
> `uv run python -c "import mcp.server.fastmcp as f; help(f.FastMCP)"`.

- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: expose knowledge base as MCP resources"`

### Task 18: `prompts.py` (2 prompts)

**Files:** Create `src/mcp_unione/prompts.py`; Test `tests/test_prompts.py`.

- [ ] **Step 1: Failing test**

```python
from mcp.server.fastmcp import FastMCP
from mcp_unione import prompts

async def test_prompts_registered():
    m = FastMCP("t"); prompts.register(m)
    names = {p.name for p in await m.list_prompts()}
    assert {"compose_transactional_email", "diagnose_delivery"} <= names
```

- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement**

```python
def register(mcp, client=None):
    @mcp.prompt()
    def compose_transactional_email(goal: str = "") -> str:
        """Guide the model to assemble a valid unione_send_email call."""
        return (
            "You are composing a UniOne transactional email.\n"
            f"Goal: {goal}\n\n"
            "Collect/confirm: from_email (on a verified domain), recipient(s), subject, "
            "and body.html (+ optional plaintext) OR a template_id.\n"
            "Pick template_engine (simple|velocity|liquid). Include the unsubscribe token "
            "({{UnsubscribeUrl}} for simple, $UnsubscribeUrl for velocity) unless skip_unsubscribe=1.\n"
            "Then call unione_send_email with confirm_send=false first to preview, then "
            "confirm_send=true to send. Use unione_validate_email for risky addresses."
        )

    @mcp.prompt()
    def diagnose_delivery(status_or_error: str = "") -> str:
        """Guide the model to explain a delivery status / error code."""
        return (
            f"Diagnose this UniOne status or error: '{status_or_error}'.\n"
            "Call unione_lookup_status for an email/delivery_status, or unione_lookup_error "
            "for a numeric API code. Then consult resources unione-docs://email-statuses, "
            "unione-docs://delivery-status-codes, or unione-docs://error-codes and summarize "
            "the cause and the fix."
        )
```

- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: MCP prompts for composing/diagnosing email"`

---

## Phase 4 — Wiring, README, CI

### Task 19: Full server wiring + end-to-end list test

**Files:** Modify `tools/__init__.py` (ensure all 10 domains registered), `server.py`; Test `tests/test_integration.py`.

- [ ] **Step 1: Failing test** — assert the full surface is present:

```python
from mcp_unione.server import build_server

async def test_full_surface(monkeypatch):
    monkeypatch.setenv("UNIONE_API_KEY", "k")
    mcp = build_server()
    tools = {t.name for t in await mcp.list_tools()}
    expected = {
      "unione_send_email","unione_subscribe","unione_validate_email",
      "unione_template_set","unione_template_get","unione_template_list","unione_template_delete",
      "unione_webhook_set","unione_webhook_get","unione_webhook_list","unione_webhook_delete",
      "unione_suppression_set","unione_suppression_get","unione_suppression_list","unione_suppression_delete",
      "unione_domain_get_dns_records","unione_domain_validate_verification_record","unione_domain_validate_dkim","unione_domain_list","unione_domain_delete",
      "unione_event_dump_create","unione_event_dump_get","unione_event_dump_list","unione_event_dump_delete",
      "unione_tag_list","unione_tag_delete",
      "unione_project_create","unione_project_update","unione_project_list","unione_project_delete",
      "unione_system_ping","unione_system_info",
      "unione_search_docs","unione_fetch_doc_page","unione_lookup_error","unione_lookup_status",
    }
    missing = expected - tools
    assert not missing, missing
    prompts = {p.name for p in await mcp.list_prompts()}
    assert {"compose_transactional_email","diagnose_delivery"} <= prompts
```

- [ ] **Step 2: Run** → fix `register_all` until PASS (all `*.register` calls present).
- [ ] **Step 3: Update `tools/__init__.py`**

```python
from . import system, email, validation, template, webhook, suppression, domain, event_dump, tag, project

def register_all(mcp, client) -> None:
    for m in (system, email, validation, template, webhook, suppression, domain, event_dump, tag, project):
        m.register(mcp, client)
```

- [ ] **Step 4: Run** `uv run pytest -q` (whole suite) → PASS.
- [ ] **Step 5: Commit** → `git commit -am "feat: wire all tool domains into the server"`

### Task 20: README + manual run check

**Files:** Modify `README.md`.

- [ ] **Step 1:** Write README sections: what it is, install (`uv sync`), env vars table, run (`uv run mcp-unione`), Claude Code/Desktop MCP config JSON example, tool list, KB resources list, "safety: confirm_send", dev/test (`uv run pytest`), license.
- [ ] **Step 2: Manual smoke** (no API key needed for listing):

Run: `uv run python -c "import asyncio; from mcp_unione.server import build_server; print(len(asyncio.run(build_server().list_tools())))"`
Expected: prints `36` (32 API + 4 docs tools).

- [ ] **Step 3: Commit** → `git commit -am "docs: README with setup, config, tools, and safety notes"`

### Task 21: CI workflow

**Files:** Create `.github/workflows/ci.yml`.

- [ ] **Step 1: Write workflow**

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --extra dev
      - run: uv run ruff check .
      - run: uv run pytest -q
```

- [ ] **Step 2: Commit** → `git commit -am "ci: lint + test on push and PR"`

---

## Phase 5 — Publish hardening (repo already exists & is public)

> The repo `karimou5/mcp-unione` is already created, public, default branch `main`.
> These steps bootstrap `main` with the code, wire release-please, then lock `main`.

### Task 22: Land the implementation on `main`

- [ ] **Step 1:** Ensure the whole suite is green locally: `uv run ruff check . && uv run pytest -q` → all PASS.
- [ ] **Step 2:** Push the accumulated commits to `main`: `git push origin main`.
- [ ] **Step 3:** Confirm CI is green on GitHub: `gh run watch` (or `gh run list -L 1`). Expected: `ci` success — this makes the `test` check context exist for branch protection.

### Task 23: release-please

- [ ] **Step 1:** Invoke the project skill: use the `setup-release-please` skill for `karimou5/mcp-unione`. It wires the `kamencorp-release-please-bot` GitHub App (App ID 2907902), sets the two GitHub secrets, and creates `release-please-config.json`, `.release-please-manifest.json`, `.github/workflows/release-please.yml`.
- [ ] **Step 2:** Configure release-please for a Python package: `release-please-config.json` uses `"release-type": "python"`, tracks `pyproject.toml` version + `CHANGELOG.md`; `.release-please-manifest.json` seeds `"."` to the current version (`0.1.0`). No build-staging/build-production workflows exist to adapt (library/server only) — skip that part of the skill.
- [ ] **Step 3:** Land the release-please files (initial bootstrap may go directly to `main` since protection is enabled in Task 24 *after* this): `git push origin main`. Verify the release-please workflow opens a release PR: `gh pr list`.

### Task 24: Protect `main` (PR-only, no direct pushes)

- [ ] **Step 1:** Enable branch protection so nobody can push to `main` directly and the CI check is required:

```bash
gh api -X PUT repos/karimou5/mcp-unione/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=test" \
  -F "enforce_admins=true" \
  -f "required_pull_request_reviews[required_approving_review_count]=0" \
  -F "restrictions=" \
  -F "allow_force_pushes=false" \
  -F "allow_deletions=false"
```

> Notes: `enforce_admins=true` blocks direct pushes even for the owner — all changes go through PRs. `required_approving_review_count=0` keeps a solo workflow (PR required, self-merge allowed). `contexts=test` matches the CI job id from Task 21. release-please's bot opens PRs (compatible). If the `gh api` array syntax errors on this CLI version, send the equivalent JSON via `--input` with a heredoc.

- [ ] **Step 2:** Verify: `gh api repos/karimou5/mcp-unione/branches/main/protection --jq '.enforce_admins.enabled, .required_status_checks.contexts'` → `true` and `["test"]`.
- [ ] **Step 3:** Sanity check that direct push is now refused: `git commit --allow-empty -m "chore: verify protection" && git push origin main` → expected REJECTED by remote (then `git reset --hard HEAD~1`). From here, all work uses feature branches + PRs.

---

## Self-review

**Spec coverage:** every spec section maps to a task — runtime/packaging (T1), config+eu default (T2), errors (T3), client/auth (T4), server/transport (T5), KB generation incl. errors.json/statuses.json (T6), all 30 API tools (T7–T15), send-guard (T8), docs tools incl. search/fetch/lookups (T16), resources (T17), prompts (T18), full wiring (T19), README (T20), CI (T21), repo public + branch protection + release-please (T22–T24). Testing strategy (respx, zero real calls) is embedded in every tool task and the guard test (T8).

**Placeholders:** none — each code step contains runnable code; repetitive tools share one explicit pattern with full code per tool.

**Type consistency:** `UniOneClient.post(path, payload)`, `Settings(api_key, base_url, timeout)`, `UniOneError(code, message, http_status, fix)`, `register(mcp, client)` per tool module, and `register_all(mcp, client)` are used identically across tasks. Tool names in T19's expected set match the names defined in T7–T16 (36 total: 32 API + 4 docs).

**Known risk flagged inline:** the exact FastMCP resource-registration API (`add_resource_fn` vs `@mcp.resource`) and `mcp.call_tool` return shape can vary by `mcp` version — T17 tells the engineer to verify against the pinned version; the tests encode the contract.
