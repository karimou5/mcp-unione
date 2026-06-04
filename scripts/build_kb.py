#!/usr/bin/env python3
"""Generate the bundled knowledge base from the research notes.

Reads ``docs/superpowers/research/0{1..5}-*.md`` and writes, under
``src/mcp_unione/data/``:

* ``kb/<slug>.md``    — 20 curated KB pages (front-matter header + content)
* ``manifest.json``   — one entry per KB page (slug, title, url, keywords, summary)
* ``errors.json``     — parsed API error-code table from research/01 §6
* ``statuses.json``   — status / delivery_status / blocking / validation / suppression maps

The script is deterministic, idempotent and standalone (no network). Run with:

    uv run python scripts/build_kb.py

The generated JSON is the runtime artifact; this script regenerates it byte-for-byte
from the research notes so the two stay in sync.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "docs" / "superpowers" / "research"
DATA = ROOT / "src" / "mcp_unione" / "data"
KB = DATA / "kb"
SYNCED = "2026-06-04"
DOCS_BASE = "https://docs.unione.io/en"

RESEARCH_FILES = {
    "01": "01-api-reference.md",
    "02": "02-template-engines.md",
    "03": "03-events-statuses-webhooks.md",
    "04": "04-deliverability-domains.md",
    "05": "05-concepts-features.md",
}


# --------------------------------------------------------------------------- #
# Research-file access helpers                                                  #
# --------------------------------------------------------------------------- #
def _read(num: str) -> list[str]:
    return (RESEARCH / RESEARCH_FILES[num]).read_text("utf-8").splitlines()


def _heading_index(lines: list[str], heading: str, after: int = 0) -> int:
    """Return the index of the first line at/after ``after`` equal to ``heading``."""
    for i in range(after, len(lines)):
        if lines[i].rstrip() == heading:
            return i
    raise ValueError(f"heading not found: {heading!r}")


def section(num: str, start_heading: str, end_heading: str | None = None) -> str:
    """Return the markdown between ``start_heading`` (inclusive) and ``end_heading``.

    ``end_heading`` is exclusive and searched **after** the start, so non-unique
    markers like ``---`` resolve to the next occurrence. ``None`` runs to EOF.
    """
    lines = _read(num)
    start = _heading_index(lines, start_heading)
    end = _heading_index(lines, end_heading, start + 1) if end_heading else len(lines)
    return "\n".join(lines[start:end]).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# Error-code table parser (research/01 §6)                                     #
# --------------------------------------------------------------------------- #
# Each section 6.x table has rows of the form:  | <http> | <api codes> | <meaning/fix> |
# The "api codes" cell may list several comma-separated codes that share the row.
_ROW = re.compile(r"^\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$")


def _split_fix(text: str) -> tuple[str, str]:
    """Split a "meaning. fix." cell into (message, fix).

    Heuristic: the fix is the trailing sentence(s) that read as an instruction. If
    no clear instruction is present, the whole cell doubles as both message and fix.
    """
    text = text.strip()
    # Sentences end at ". " — keep the trailing one(s) as the fix when they look
    # like guidance (start with an imperative verb / "Use" / "Contact" / etc.).
    parts = re.split(r"(?<=[.!?])\s+", text)
    if len(parts) >= 2:
        head = " ".join(parts[:-1]).strip()
        tail = parts[-1].strip()
        if re.match(
            r"^(Use|Pass|Set|Add|Contact|Check|Try|Turn|Send|Call|Re-?check|"
            r"Re-?send|Make|Verify|Specify|Remove|Choose|Ensure|Confirm|Fix)\b",
            tail,
        ):
            return head, tail
    return text, text


def parse_errors() -> dict[str, dict]:
    lines = _read("01")
    start = _heading_index(lines, "## 6. Global / Common API Error Codes")
    end = _heading_index(lines, "# 7. Method Reference (28 methods)")
    table: dict[str, dict] = {}
    for line in lines[start:end]:
        m = _ROW.match(line)
        if not m:
            continue
        http_cell, code_cell, meaning_cell = m.groups()
        # Skip header rows and markdown separators.
        if code_cell.lower() in {"api", "code"} or set(code_cell) <= {"-", " ", ":"}:
            continue
        # HTTP cell may be a range like "50x" — keep it int only when numeric.
        http_match = re.match(r"^(\d{3})$", http_cell.strip())
        http_val: int | None = int(http_match.group(1)) if http_match else None
        codes = [c.strip() for c in code_cell.split(",") if c.strip()]
        # Every shared code must be a bare integer; otherwise this is not a code row.
        if not codes or not all(c.isdigit() for c in codes):
            continue
        message, fix = _split_fix(meaning_cell)
        for code in codes:
            table[code] = {"http": http_val, "message": message, "fix": fix}
    return dict(sorted(table.items(), key=lambda kv: int(kv[0])))


# --------------------------------------------------------------------------- #
# Status / enum maps (research/03 + research/05)                               #
# --------------------------------------------------------------------------- #
_BACKTICK_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|")


def _parse_pipe_map(num: str, start_heading: str, end_heading: str) -> dict[str, str]:
    """Parse ``| `key` | description |`` rows in a section into {key: description}."""
    lines = _read(num)
    start = _heading_index(lines, start_heading)
    end = _heading_index(lines, end_heading, start + 1)
    out: dict[str, str] = {}
    for line in lines[start:end]:
        m = _BACKTICK_ROW.match(line)
        if not m:
            continue
        key, desc = m.group(1).strip(), m.group(2).strip()
        # Drop trailing table cells (Final?/Notes) — keep the first description cell.
        desc = desc.split(" | ")[0].strip()
        # Skip the table header row (e.g. | `result` | Meaning |).
        if desc.lower() in {"meaning", "description", "scope"}:
            continue
        if key and desc and key not in out:
            out[key] = desc
    return out


def parse_statuses() -> dict[str, dict]:
    # Standard 8 statuses (research/03 §1.1).
    statuses = _parse_pipe_map(
        "03",
        "### 1.1 Standard statuses (from the `email-statuses` article)",
        "### 1.2 `status` enum as documented in the webhook callback-format reference",
    )
    # Add `accepted` and `subscribed` from the webhook-reference enum (§1.2).
    ext = _parse_pipe_map(
        "03",
        "### 1.2 `status` enum as documented in the webhook callback-format reference",
        "## 2. Extended delivery statuses (`delivery_info.delivery_status`)",
    )
    for name in ("accepted", "subscribed"):
        if name in ext and name not in statuses:
            statuses[name] = ext[name]

    # Extended delivery statuses (research/03 §2.1–2.7 success/error tables).
    delivery: dict[str, str] = {}
    for start, end in (
        ("### 2.1 Success", "### 2.2 Complaint or unsubscription"),
        ("### 2.2 Complaint or unsubscription",
         "### 2.3 Temporary failure (soft bounce — additional delivery attempts will be made)"),
        ("### 2.3 Temporary failure (soft bounce — additional delivery attempts will be made)",
         "### 2.4 Non-existent address"),
        ("### 2.4 Non-existent address", "### 2.5 Rejected as spam"),
        ("### 2.5 Rejected as spam", "### 2.6 Long-term unreachable"),
        ("### 2.6 Long-term unreachable", "### 2.7 Short-term unreachable"),
        ("### 2.7 Short-term unreachable",
         "### 2.8 Additional `delivery_status` values listed only in the webhook reference"),
        ("### 2.8 Additional `delivery_status` values listed only in the webhook reference",
         "## 3. Reasons to block sending (`email/send` blocking reasons)"),
    ):
        for k, v in _parse_pipe_map("03", start, end).items():
            delivery.setdefault(k, v)

    # Blocking reasons (research/03 §3).
    blocking = _parse_pipe_map(
        "03",
        "## 3. Reasons to block sending (`email/send` blocking reasons)",
        "## 4. Webhooks",
    )

    # Validation result + cause enums (research/05 §2).
    validation = _parse_pipe_map(
        "05",
        "### `result` — ALL possible validation statuses (verbatim)",
        "### `cause` — ALL possible causes for a validation result (verbatim)",
    )
    validation.update(
        _parse_pipe_map(
            "05",
            "### `cause` — ALL possible causes for a validation result (verbatim)",
            "---",
        )
    )

    # Suppression cause enum (research/05 §3).
    suppression = _parse_pipe_map(
        "05",
        "### `cause` — COMPLETE list of suppression cause values (verbatim)",
        "### `source` — COMPLETE list of suppression source values (verbatim)",
    )

    return {
        "statuses": statuses,
        "delivery_status": delivery,
        "blocking_reasons": blocking,
        "validation": validation,
        "suppression_cause": suppression,
    }


# --------------------------------------------------------------------------- #
# KB page definitions                                                          #
# --------------------------------------------------------------------------- #
# Each page: (slug, Title, docslug-for-source-url, body-builder)
def _page_getting_started() -> str:
    return "\n".join([
        section("05", "## 1. Getting started", "## 2. Email validation").rstrip(),
        "",
        section("01", "## 1. Transport, Base URLs & Request Envelope",
                "## 4. HTTP Status Codes (transport level)").rstrip(),
    ]) + "\n"


def _page_web_api_reference() -> str:
    return "\n".join([
        section("01", "## 1. Transport, Base URLs & Request Envelope",
                "## 6. Global / Common API Error Codes").rstrip(),
        "",
        section("01", "## 9. Quick Enum Reference").rstrip(),
    ]) + "\n"


def _page_email_send_params() -> str:
    return section("01", "## 7.1 `email/send.json`", "## 7.2 `email/subscribe.json`")


def _page_template_simple() -> str:
    return "\n".join([
        section("02", "## 0. Overview — How an engine is selected",
                "## 1. Simple Template Engine").rstrip(),
        "",
        section("02", "## 1. Simple Template Engine", "## 2. Velocity Template Engine").rstrip(),
    ]) + "\n"


def _page_template_velocity() -> str:
    return section("02", "## 2. Velocity Template Engine", "## 3. Liquid Template Engine")


def _page_template_liquid() -> str:
    return "\n".join([
        section("02", "## 3. Liquid Template Engine",
                "## 4. Special / reserved substitution variables & system substitutions").rstrip(),
        "",
        section("02", "## 4. Special / reserved substitution variables & system substitutions").rstrip(),
    ]) + "\n"


def _page_email_statuses() -> str:
    return "\n".join([
        section("03", "## 1. Email Statuses (`status` field)",
                "## 2. Extended delivery statuses (`delivery_info.delivery_status`)").rstrip(),
        "",
        section("03", "## 3. Reasons to block sending (`email/send` blocking reasons)",
                "## 4. Webhooks").rstrip(),
    ]) + "\n"


def _page_delivery_status_codes() -> str:
    return section(
        "03",
        "## 2. Extended delivery statuses (`delivery_info.delivery_status`)",
        "## 3. Reasons to block sending (`email/send` blocking reasons)",
    )


def _page_webhooks() -> str:
    return "\n".join([
        section("03", "## 4. Webhooks", "## 5. Webhook callback format — the exact JSON UniOne POSTs to your endpoint").rstrip(),
        "",
        section("03", "## 5. Webhook callback format — the exact JSON UniOne POSTs to your endpoint",
                "## 6. Spam blocking (`spam_block` events)").rstrip(),
        "",
        section("03", "## 6. Spam blocking (`spam_block` events)",
                "## 7. Sending CC and BCC (copies / blind copies)").rstrip(),
    ]) + "\n"


def _page_suppression_lists() -> str:
    return section("05", "## 3. Suppression lists", "## 4. Projects")


def _page_email_validation() -> str:
    return section("05", "## 2. Email validation", "## 3. Suppression lists")


def _page_dns_setup() -> str:
    return "\n".join([
        section("04", "## 1. DNS Setup & Domain Authentication",
                "## 2. The Domain API methods").rstrip(),
        "",
        section("04", "## 2. The Domain API methods", "## 3. Sandbox Domain (test sending)").rstrip(),
    ]) + "\n"


def _page_sandbox_domain() -> str:
    return section("04", "## 3. Sandbox Domain (test sending)", "## 4. Dedicated IP & Warmup")


def _page_dedicated_ip() -> str:
    return section("04", "## 4. Dedicated IP & Warmup", "## 5. Tracking Domains (click/open tracking)")


def _page_tracking_domains() -> str:
    return "\n".join([
        section("04", "## 5. Tracking Domains (click/open tracking)", "## 6. IP Access Control").rstrip(),
        "",
        section("04", "## 6. IP Access Control", "## 7. Cross-cutting notes for the MCP server").rstrip(),
    ]) + "\n"


def _page_projects() -> str:
    return section("05", "## 4. Projects", "## 5. Unsubscribe link")


def _page_unsubscribe() -> str:
    return section("05", "## 5. Unsubscribe link", "## 6. Shared access (roles)")


def _page_error_codes() -> str:
    return section("01", "## 6. Global / Common API Error Codes",
                   "# 7. Method Reference (28 methods)")


def _page_changelog() -> str:
    return section("05", "## 9. API changelog (notable versions)",
                   "## 10. Integrations & official SDKs")


def _page_sdks_integrations() -> str:
    return "\n".join([
        section("05", "## 10. Integrations & official SDKs", "## Appendix — quick reference of all verbatim enums").rstrip(),
        "",
        section("05", "## Appendix — quick reference of all verbatim enums").rstrip(),
    ]) + "\n"


# slug -> (Human Title, docslug, builder)
PAGES: list[tuple[str, str, str, object]] = [
    ("getting-started", "Getting Started with UniOne", "getting-started", _page_getting_started),
    ("web-api-reference", "Web API Reference", "web-api", _page_web_api_reference),
    ("email-send-params", "email/send Parameters", "web-api-email-send", _page_email_send_params),
    ("template-simple", "Simple Template Engine", "simple-template-engine", _page_template_simple),
    ("template-velocity", "Velocity Template Engine", "velocity-template-engine", _page_template_velocity),
    ("template-liquid", "Liquid Template Engine", "liquid-template-engine", _page_template_liquid),
    ("email-statuses", "Email Statuses", "email-statuses", _page_email_statuses),
    ("delivery-status-codes", "Extended Delivery Status Codes", "email-statuses", _page_delivery_status_codes),
    ("webhooks", "Webhooks", "web-api-notifications", _page_webhooks),
    ("suppression-lists", "Suppression Lists", "suppression-list", _page_suppression_lists),
    ("email-validation", "Email Validation", "email-validation", _page_email_validation),
    ("dns-setup", "DNS Setup & Domain Authentication", "dns-settings", _page_dns_setup),
    ("sandbox-domain", "Sandbox Domain", "sandbox", _page_sandbox_domain),
    ("dedicated-ip", "Dedicated IP & Warmup", "dedicated-ip", _page_dedicated_ip),
    ("tracking-domains", "Tracking Domains", "tracking-domain", _page_tracking_domains),
    ("projects", "Projects", "projects", _page_projects),
    ("unsubscribe", "Unsubscribe Link & Footer", "unsubscribe", _page_unsubscribe),
    ("error-codes", "API Error Codes", "api-errors", _page_error_codes),
    ("changelog", "API Changelog", "api-changelog", _page_changelog),
    ("sdks-integrations", "SDKs & Integrations", "integrations", _page_sdks_integrations),
]


# --------------------------------------------------------------------------- #
# Manifest keyword/summary derivation                                          #
# --------------------------------------------------------------------------- #
_STOP = {
    "the", "and", "for", "with", "from", "this", "that", "via", "are", "all",
    "how", "what", "your", "you", "per", "into", "each", "only", "not", "its",
    "can", "may", "set", "use", "used", "have", "has", "see", "ref", "etc",
    "json", "api", "http", "https", "docs", "unione", "title", "source", "synced",
}
_WORD = re.compile(r"[a-z][a-z0-9_-]{2,}")


def _keywords(slug: str, title: str, body: str) -> list[str]:
    """Derive keywords from the slug, title and section headings of the page."""
    seen: list[str] = []

    def add(tokens):
        for tok in tokens:
            if tok in _STOP or tok in seen:
                continue
            seen.append(tok)

    add(slug.split("-"))
    add(_WORD.findall(title.lower()))
    # Pull words from markdown headings (### / ## lines) and backticked identifiers.
    for line in body.splitlines():
        if line.startswith("#"):
            add(_WORD.findall(line.lower()))
        for ident in re.findall(r"`([a-z][a-z0-9_./-]+)`", line):
            tok = ident.split("/")[0].split(".")[0].split("[")[0]
            if _WORD.fullmatch(tok):
                add([tok])
    return seen[:14]


def _summary(title: str, slug: str) -> str:
    return f"{title}: curated UniOne reference for {slug.replace('-', ' ')}."


# --------------------------------------------------------------------------- #
# Writers                                                                      #
# --------------------------------------------------------------------------- #
def _header(title: str, docslug: str) -> str:
    return (
        "---\n"
        f"title: {title}\n"
        f"source: {DOCS_BASE}/{docslug}\n"
        f"synced: {SYNCED}\n"
        "---\n\n"
    )


def write_kb_and_manifest() -> None:
    KB.mkdir(parents=True, exist_ok=True)
    manifest = []
    for slug, title, docslug, builder in PAGES:
        body = builder()
        page = _header(title, docslug) + body
        if not page.endswith("\n"):
            page += "\n"
        (KB / f"{slug}.md").write_text(page, "utf-8")
        url = f"{DOCS_BASE}/{docslug}"
        manifest.append({
            "slug": slug,
            "title": title,
            "url": url,
            "keywords": _keywords(slug, title, body),
            "summary": _summary(title, slug),
        })
    (DATA / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )


def write_json(name: str, obj) -> None:
    (DATA / name).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    write_json("errors.json", parse_errors())
    write_json("statuses.json", parse_statuses())
    write_kb_and_manifest()
    errors = json.loads((DATA / "errors.json").read_text("utf-8"))
    statuses = json.loads((DATA / "statuses.json").read_text("utf-8"))
    kb_count = len(list(KB.glob("*.md")))
    print(f"wrote {kb_count} kb pages")
    print(f"wrote errors.json: {len(errors)} codes")
    print(
        "wrote statuses.json: "
        f"{len(statuses['statuses'])} statuses, "
        f"{len(statuses['delivery_status'])} delivery_status, "
        f"{len(statuses['blocking_reasons'])} blocking_reasons, "
        f"{len(statuses['validation'])} validation, "
        f"{len(statuses['suppression_cause'])} suppression_cause"
    )
    print("wrote manifest.json")


if __name__ == "__main__":
    main()
