def register(mcp, client):
    @mcp.tool()
    async def unione_tag_list() -> dict:
        """List tags (tag/list.json)."""
        return await client.post("tag/list.json", {})

    @mcp.tool()
    async def unione_tag_delete(tag_id: int) -> dict:
        """Delete a tag by id (tag/delete.json)."""
        return await client.post("tag/delete.json", {"tag_id": tag_id})
