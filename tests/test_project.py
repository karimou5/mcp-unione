import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import project


def _mcp(client):
    m = FastMCP("t")
    project.register(m, client)
    return m


@respx.mock
async def test_project_create_wraps_under_project(client, base):
    route = respx.post(f"{base}/project/create.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "project_id": "P"})
    )
    await _mcp(client).call_tool(
        "unione_project_create", {"name": "Proj", "country": "FR"}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert "project" in body
    assert body["project"]["name"] == "Proj"
    assert body["project"]["country"] == "FR"
    assert body["project"]["send_enabled"] is True
    assert body["project"]["custom_unsubscribe_url_enabled"] is False


@respx.mock
async def test_project_create_with_backend_id(client, base):
    route = respx.post(f"{base}/project/create.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_project_create", {"name": "Proj", "backend_id": 7}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["project"]["backend_id"] == 7
    assert "country" not in body["project"]


@respx.mock
async def test_project_update(client, base):
    route = respx.post(f"{base}/project/update.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_project_update",
        {"project_id": "P1", "project": {"name": "New"}},
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"project_id": "P1", "project": {"name": "New"}}


@respx.mock
async def test_project_list_default(client, base):
    route = respx.post(f"{base}/project/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_project_list", {})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {}


@respx.mock
async def test_project_list_with_id(client, base):
    route = respx.post(f"{base}/project/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_project_list", {"project_id": "P1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"project_id": "P1"}


@respx.mock
async def test_project_delete(client, base):
    route = respx.post(f"{base}/project/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_project_delete", {"project_id": "P1"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"project_id": "P1"}
