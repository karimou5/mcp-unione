from mcp.server.fastmcp import FastMCP

from mcp_unione import resources


async def test_lists_and_reads_resource():
    m = FastMCP("t")
    resources.register(m)
    res = await m.list_resources()
    uris = {str(r.uri) for r in res}
    assert any(u.startswith("unione-docs://") for u in uris)
    content = await m.read_resource("unione-docs://email-statuses")
    assert "status" in str(content).lower()


async def test_reads_distinct_resources():
    from mcp.server.fastmcp import FastMCP

    m = FastMCP("t")
    resources.register(m)
    c1 = str(await m.read_resource("unione-docs://getting-started"))
    c2 = str(await m.read_resource("unione-docs://webhooks"))
    assert c1 != c2
    assert "webhook" in c2.lower()
