from mcp_unione.server import build_server


async def test_server_builds_and_lists_tools():
    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "unione_system_ping" in names  # registered in Task 7
