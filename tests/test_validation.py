import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import validation


def _mcp(client):
    m = FastMCP("t")
    validation.register(m, client)
    return m


@respx.mock
async def test_validate_email(client, base):
    route = respx.post(f"{base}/email-validation/single.json").mock(
        return_value=httpx.Response(200, json={"status": "success", "result": "valid"})
    )
    await _mcp(client).call_tool("unione_validate_email", {"email": "a@b.com"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"email": "a@b.com"}
