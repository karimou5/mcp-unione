import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import webhook


def _mcp(client):
    m = FastMCP("t")
    webhook.register(m, client)
    return m


@respx.mock
async def test_webhook_set_defaults(client, base):
    route = respx.post(f"{base}/webhook/set.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_webhook_set",
        {
            "url": "https://h.example/hook",
            "events": {"email_status": ["delivered"]},
        },
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["url"] == "https://h.example/hook"
    assert body["events"] == {"email_status": ["delivered"]}
    assert body["status"] == "active"
    assert body["event_format"] == "json_post"
    assert body["delivery_info"] == 1
    assert body["single_event"] == 0
    assert body["max_parallel"] == 10


@respx.mock
async def test_webhook_get(client, base):
    route = respx.post(f"{base}/webhook/get.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_webhook_get", {"url": "https://h.example/hook"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"url": "https://h.example/hook"}


@respx.mock
async def test_webhook_list(client, base):
    route = respx.post(f"{base}/webhook/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_webhook_list", {"limit": 20, "offset": 0})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"limit": 20, "offset": 0}


@respx.mock
async def test_webhook_delete(client, base):
    route = respx.post(f"{base}/webhook/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_webhook_delete", {"url": "https://h.example/hook"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"url": "https://h.example/hook"}
