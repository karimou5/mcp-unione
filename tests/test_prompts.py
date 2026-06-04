from mcp.server.fastmcp import FastMCP

from mcp_unione import prompts


async def test_prompts_registered():
    m = FastMCP("t")
    prompts.register(m)
    names = {p.name for p in await m.list_prompts()}
    assert {"compose_transactional_email", "diagnose_delivery"} <= names
