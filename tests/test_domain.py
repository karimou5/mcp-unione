import json

import httpx
import respx

from mcp.server.fastmcp import FastMCP
from mcp_unione.tools import domain


def _mcp(client):
    m = FastMCP("t")
    domain.register(m, client)
    return m


@respx.mock
async def test_domain_get_dns_records(client, base):
    route = respx.post(f"{base}/domain/get-dns-records.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_domain_get_dns_records", {"domain": "example.com"}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"domain": "example.com"}


@respx.mock
async def test_domain_validate_verification_record(client, base):
    route = respx.post(f"{base}/domain/validate-verification-record.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool(
        "unione_domain_validate_verification_record", {"domain": "example.com"}
    )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"domain": "example.com"}


@respx.mock
async def test_domain_validate_dkim(client, base):
    route = respx.post(f"{base}/domain/validate-dkim.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_domain_validate_dkim", {"domain": "example.com"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"domain": "example.com"}


@respx.mock
async def test_domain_list_default(client, base):
    route = respx.post(f"{base}/domain/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_domain_list", {"limit": 10, "offset": 0})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"limit": 10, "offset": 0}


@respx.mock
async def test_domain_list_with_domain(client, base):
    route = respx.post(f"{base}/domain/list.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_domain_list", {"domain": "example.com"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["domain"] == "example.com"


@respx.mock
async def test_domain_delete(client, base):
    route = respx.post(f"{base}/domain/delete.json").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )
    await _mcp(client).call_tool("unione_domain_delete", {"domain": "example.com"})
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body == {"domain": "example.com"}
