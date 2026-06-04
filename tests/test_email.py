import json

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
    body_json = json.loads(route.calls.last.request.content)
    assert body_json["message"]["from_email"] == "s@d.com"
    assert body_json["message"]["recipients"][0]["email"] == "a@b.com"


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


async def test_send_does_not_log_api_key(client, base, caplog):
    import logging

    with respx.mock:
        respx.post(f"{base}/email/send.json").mock(
            return_value=httpx.Response(200, json={"status": "success"})
        )
        m = FastMCP("t")
        email.register(m, client)
        with caplog.at_level(logging.INFO, logger="mcp_unione"):
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
    assert "k" not in caplog.text  # the test api_key is "k"
