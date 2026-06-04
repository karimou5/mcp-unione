import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import event_dump


def _mcp(client):
    m = FastMCP("t")
    event_dump.register(m, client)
    return m


@respx.mock
async def test_event_dump_create_defaults(client, base):
    route = respx.post(f"{base}/event-dump/create.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_event_dump_create", {"start_time": "2022-07-20 00:00:00"}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["start_time"] == "2022-07-20 00:00:00"
    assert body["delimiter"] == ","
    assert body["format"] == "csv"
    assert body["all_projects"] is False


@respx.mock
async def test_event_dump_create_with_filter(client, base):
    route = respx.post(f"{base}/event-dump/create.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_event_dump_create",
        {
            "start_time": "2024-01-01 00:00:00",
            "end_time": "2024-01-02 00:00:00",
            "limit": 100,
            "filter": {"status": "sent"},
        },
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["start_time"] == "2024-01-01 00:00:00"
    assert body["end_time"] == "2024-01-02 00:00:00"
    assert body["limit"] == 100
    assert body["filter"] == {"status": "sent"}


@respx.mock
async def test_event_dump_get(client, base):
    route = respx.post(f"{base}/event-dump/get.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_event_dump_get", {"dump_id": "D1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"dump_id": "D1"}


@respx.mock
async def test_event_dump_list(client, base):
    route = respx.post(f"{base}/event-dump/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_event_dump_list", {})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {}


@respx.mock
async def test_event_dump_delete(client, base):
    route = respx.post(f"{base}/event-dump/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_event_dump_delete", {"dump_id": "D1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"dump_id": "D1"}
