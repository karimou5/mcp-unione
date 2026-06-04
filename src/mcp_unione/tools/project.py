def register(mcp, client):
    @mcp.tool()
    async def unione_project_create(
        name: str,
        country: str | None = None,
        send_enabled: bool = True,
        custom_unsubscribe_url_enabled: bool = False,
        backend_id: int | None = None,
    ) -> dict:
        """Create a project (project/create.json). Returns project_id + project_api_key."""
        proj = {
            "name": name,
            "send_enabled": send_enabled,
            "custom_unsubscribe_url_enabled": custom_unsubscribe_url_enabled,
        }
        if country:
            proj["country"] = country
        if backend_id is not None:
            proj["backend_id"] = backend_id
        return await client.post("project/create.json", {"project": proj})

    @mcp.tool()
    async def unione_project_update(project_id: str, project: dict) -> dict:
        """Update a project (project/update.json)."""
        return await client.post(
            "project/update.json", {"project_id": project_id, "project": project}
        )

    @mcp.tool()
    async def unione_project_list(project_id: str | None = None) -> dict:
        """List projects (project/list.json)."""
        return await client.post(
            "project/list.json", {"project_id": project_id} if project_id else {}
        )

    @mcp.tool()
    async def unione_project_delete(project_id: str) -> dict:
        """Delete a project (project/delete.json)."""
        return await client.post("project/delete.json", {"project_id": project_id})
