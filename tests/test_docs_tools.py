import httpx
import respx
from mcp.server.fastmcp import FastMCP

from mcp_unione import docs_tools


def _mcp():
    m = FastMCP("t")
    docs_tools.register(m, None)
    return m


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
        return_value=httpx.Response(200, html="<html><body><h1>Email statuses</h1></body></html>")
    )
    out = await _mcp().call_tool("unione_fetch_doc_page", {"slug_or_url": "email-statuses"})
    assert "Email statuses" in str(out)
