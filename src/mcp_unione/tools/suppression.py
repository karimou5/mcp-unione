def register(mcp, client):
    @mcp.tool()
    async def unione_suppression_set(
        email: str, cause: str, created: str | None = None
    ) -> dict:
        """Add to suppression list (suppression/set.json).
        cause: unsubscribed|temporary_unavailable|permanent_unavailable|complained."""
        p = {"email": email, "cause": cause}
        if created is not None:
            p["created"] = created
        return await client.post("suppression/set.json", p)

    @mcp.tool()
    async def unione_suppression_get(email: str, all_projects: bool = False) -> dict:
        """Check suppression status for an address (suppression/get.json)."""
        return await client.post(
            "suppression/get.json", {"email": email, "all_projects": all_projects}
        )

    @mcp.tool()
    async def unione_suppression_list(
        cause: str | None = None,
        source: str | None = None,
        start_time: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        """List suppressions with cursor pagination (suppression/list.json).
        source: user|system|subscriber."""
        p = {"limit": limit}
        for k, v in {
            "cause": cause,
            "source": source,
            "start_time": start_time,
            "cursor": cursor,
        }.items():
            if v is not None:
                p[k] = v
        return await client.post("suppression/list.json", p)

    @mcp.tool()
    async def unione_suppression_delete(email: str) -> dict:
        """Remove an address from the suppression list (suppression/delete.json)."""
        return await client.post("suppression/delete.json", {"email": email})
