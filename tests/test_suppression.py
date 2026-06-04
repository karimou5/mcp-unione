import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import suppression


def _mcp(client):
    m = FastMCP("t")
    suppression.register(m, client)
    return m


@respx.mock
async def test_suppression_set_sends_cause(client, base):
    route = respx.post(f"{base}/suppression/set.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_suppression_set",
        {"email": "a@b.com", "cause": "unsubscribed"},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"email": "a@b.com", "cause": "unsubscribed"}


@respx.mock
async def test_suppression_set_with_created(client, base):
    route = respx.post(f"{base}/suppression/set.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_suppression_set",
        {"email": "a@b.com", "cause": "complained", "created": "2024-01-01 00:00:00"},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["created"] == "2024-01-01 00:00:00"
    assert body["cause"] == "complained"


@respx.mock
async def test_suppression_get(client, base):
    route = respx.post(f"{base}/suppression/get.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_suppression_get", {"email": "a@b.com", "all_projects": True}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"email": "a@b.com", "all_projects": True}


@respx.mock
async def test_suppression_list_only_limit_by_default(client, base):
    route = respx.post(f"{base}/suppression/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_suppression_list", {"limit": 25})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"limit": 25}


@respx.mock
async def test_suppression_list_with_filters(client, base):
    route = respx.post(f"{base}/suppression/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_suppression_list",
        {"cause": "unsubscribed", "source": "user", "cursor": "c1"},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["cause"] == "unsubscribed"
    assert body["source"] == "user"
    assert body["cursor"] == "c1"


@respx.mock
async def test_suppression_delete(client, base):
    route = respx.post(f"{base}/suppression/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_suppression_delete", {"email": "a@b.com"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"email": "a@b.com"}
