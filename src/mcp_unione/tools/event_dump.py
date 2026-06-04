def register(mcp, client):
    @mcp.tool()
    async def unione_event_dump_create(
        start_time: str,
        end_time: str | None = None,
        limit: int | None = None,
        all_projects: bool = False,
        filter: dict | None = None,
        delimiter: str = ",",
        format: str = "csv",
    ) -> dict:
        """Create a CSV event export (event-dump/create.json). filter supports job_id, status,
        delivery_status, email, email_from, domain, campaign_id."""
        p = {
            "start_time": start_time,
            "all_projects": all_projects,
            "delimiter": delimiter,
            "format": format,
        }
        for k, v in {
            "end_time": end_time,
            "limit": limit,
            "filter": filter,
        }.items():
            if v is not None:
                p[k] = v
        return await client.post("event-dump/create.json", p)

    @mcp.tool()
    async def unione_event_dump_get(dump_id: str) -> dict:
        """Get an export's status/URL (event-dump/get.json)."""
        return await client.post("event-dump/get.json", {"dump_id": dump_id})

    @mcp.tool()
    async def unione_event_dump_list() -> dict:
        """List event exports (event-dump/list.json)."""
        return await client.post("event-dump/list.json", {})

    @mcp.tool()
    async def unione_event_dump_delete(dump_id: str) -> dict:
        """Delete an export (event-dump/delete.json)."""
        return await client.post("event-dump/delete.json", {"dump_id": dump_id})
