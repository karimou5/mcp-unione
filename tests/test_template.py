import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import template


def _mcp(client):
    m = FastMCP("t")
    template.register(m, client)
    return m


@respx.mock
async def test_template_set_wraps_under_template(client, base):
    route = respx.post(f"{base}/template/set.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "template": {"id": "T"}})
    )
    await _mcp(client).call_tool(
        "unione_template_set",
        {"name": "Welcome", "body": {"html": "<b>hi</b>"}, "subject": "Hi"},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert "template" in body
    assert body["template"]["name"] == "Welcome"
    assert body["template"]["subject"] == "Hi"
    assert body["template"]["template_engine"] == "simple"
    assert body["template"]["body"] == {"html": "<b>hi</b>"}


@respx.mock
async def test_template_set_update_passes_id(client, base):
    route = respx.post(f"{base}/template/set.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_template_set",
        {"name": "Welcome", "body": {"html": "x"}, "template_id": "abc"},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["template"]["id"] == "abc"


@respx.mock
async def test_template_get(client, base):
    route = respx.post(f"{base}/template/get.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_template_get", {"id": "T1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"id": "T1"}


@respx.mock
async def test_template_list(client, base):
    route = respx.post(f"{base}/template/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "templates": []})
    )
    await _mcp(client).call_tool("unione_template_list", {"limit": 10, "offset": 5})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"limit": 10, "offset": 5}


@respx.mock
async def test_template_delete(client, base):
    route = respx.post(f"{base}/template/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_template_delete", {"id": "T1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"id": "T1"}
