from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib.resources import files

import httpx


@lru_cache(maxsize=None)
def _data(name: str) -> str:
    return files("mcp_unione.data").joinpath(name).read_text("utf-8")


@lru_cache(maxsize=None)
def _manifest() -> list[dict]:
    return json.loads(_data("manifest.json"))


def _kb_text(slug: str) -> str:
    return files("mcp_unione.data").joinpath("kb", f"{slug}.md").read_text("utf-8")


def _score(entry: dict, terms: list[str]) -> int:
    hay = (
        entry["title"]
        + " "
        + " ".join(entry.get("keywords", []))
        + " "
        + entry.get("summary", "")
    ).lower()
    return sum(hay.count(t) for t in terms)


def register(mcp, client=None):
    @mcp.tool()
    async def unione_search_docs(query: str, limit: int = 5) -> dict:
        """Search the bundled UniOne knowledge base. Returns matching pages with slug,
        title, url, and a short snippet. Use unione_fetch_doc_page or the resource for full text."""
        terms = [t for t in re.split(r"\W+", query.lower()) if t]
        scored = sorted(
            ((_score(e, terms), e) for e in _manifest()),
            key=lambda x: x[0],
            reverse=True,
        )
        hits = []
        for s, e in scored[:limit]:
            if s == 0:
                break
            try:
                body = _kb_text(e["slug"])
            except OSError:
                body = ""
            snippet = next(
                (ln for ln in body.splitlines() if any(t in ln.lower() for t in terms)),
                e.get("summary", ""),
            )
            hits.append(
                {
                    "slug": e["slug"],
                    "title": e["title"],
                    "url": e["url"],
                    "resource": f"unione-docs://{e['slug']}",
                    "snippet": snippet[:300],
                }
            )
        return {"query": query, "results": hits}

    @mcp.tool()
    async def unione_fetch_doc_page(slug_or_url: str) -> dict:
        """Fetch a live UniOne docs page (markdown-ish text). Accepts a slug
        (e.g. 'email-statuses') or a full https://docs.unione.io/en/... URL."""
        url = (
            slug_or_url
            if slug_or_url.startswith(("https://", "http://"))
            else f"https://docs.unione.io/en/{slug_or_url}"
        )
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
        return (
            {"code": code, **info}
            if info
            else {"code": code, "message": "Unknown code.", "fix": None}
        )

    @mcp.tool()
    async def unione_lookup_status(status: str) -> dict:
        """Explain an email status or extended delivery_status code."""
        s = json.loads(_data("statuses.json"))
        status_lower = status.strip().lower()
        for bucket in ("statuses", "delivery_status", "blocking_reasons", "validation", "suppression_cause"):
            if status_lower in s.get(bucket, {}):
                return {"status": status, "category": bucket, "meaning": s[bucket][status_lower]}
        return {"status": status, "meaning": "Unknown status."}
