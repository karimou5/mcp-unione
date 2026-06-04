import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import email


def _mcp(client):
    m = FastMCP("t")
    email.register(m, client)
    return m


@respx.mock
async def test_send_guard_blocks_without_confirm(client, base):
    route = respx.post(f"{base}/email/send.json")
    m = _mcp(client)
    out = await m.call_tool(
        "unione_send_email",
        {
            "recipients": [{"email": "a@b.com"}],
            "subject": "Hi",
            "from_email": "s@d.com",
            "body": {"html": "<b>hi</b>"},
        },
    )
    assert route.called is False  # no real send
    assert "preview" in str(out).lower()


@respx.mock
async def test_send_real_with_confirm(client, base):
    route = respx.post(f"{base}/email/send.json").mock(
        return_value=httpx.Response(
            200, json={"status": "success", "job_id": "J", "emails": ["a@b.com"]}
        )
    )
    m = _mcp(client)
    await m.call_tool(
        "unione_send_email",
        {
            "recipients": [{"email": "a@b.com"}],
            "subject": "Hi",
            "from_email": "s@d.com",
            "body": {"html": "<b>hi</b>"},
            "confirm_send": True,
        },
    )
    assert route.called
    body = route.calls.last.request.content
    # httpx serializes JSON compactly (no space after the colon).
    assert b"a@b.com" in body and b'"from_email":"s@d.com"' in body
    assert b'"message"' in body


@respx.mock
async def test_send_requires_body_or_template(client, base):
    route = respx.post(f"{base}/email/send.json")
    m = _mcp(client)
    out = await m.call_tool(
        "unione_send_email",
        {
            "recipients": [{"email": "a@b.com"}],
            "subject": "Hi",
            "from_email": "s@d.com",
            "confirm_send": True,
        },
    )
    assert route.called is False
    assert "body" in str(out).lower() and "template_id" in str(out).lower()


@respx.mock
async def test_subscribe(client, base):
    route = respx.post(f"{base}/email/subscribe.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    m = _mcp(client)
    await m.call_tool(
        "unione_subscribe", {"from_email": "s@d.com", "to_email": "u@x.com"}
    )
    assert route.called
