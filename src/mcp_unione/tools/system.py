def register(mcp, client):
    @mcp.tool()
    async def unione_system_ping() -> dict:
        """Health check. POST system/ping.json (no params). Returns {status:'success'}."""
        return await client.post("system/ping.json", {})

    @mcp.tool()
    async def unione_system_info() -> dict:
        """Account/limits info. POST system/info.json (no params)."""
        return await client.post("system/info.json", {})
