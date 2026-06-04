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
