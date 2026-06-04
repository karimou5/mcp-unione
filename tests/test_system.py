import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import system


def _mcp(client):
    m = FastMCP("t")
    system.register(m, client)
    return m


@respx.mock
async def test_ping(client, base):
    route = respx.post(f"{base}/system/ping.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    out = await _mcp(client).call_tool("unione_system_ping", {})
    assert route.called
    assert "success" in str(out)


@respx.mock
async def test_info(client, base):
    route = respx.post(f"{base}/system/info.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "info": {}})
    )
    await _mcp(client).call_tool("unione_system_info", {})
    assert route.called
