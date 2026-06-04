import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import tag


def _mcp(client):
    m = FastMCP("t")
    tag.register(m, client)
    return m


@respx.mock
async def test_tag_list(client, base):
    route = respx.post(f"{base}/tag/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "tags": []})
    )
    await _mcp(client).call_tool("unione_tag_list", {})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {}


@respx.mock
async def test_tag_delete(client, base):
    route = respx.post(f"{base}/tag/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_tag_delete", {"tag_id": 42})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"tag_id": 42}
