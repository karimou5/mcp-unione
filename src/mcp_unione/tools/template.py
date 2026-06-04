def register(mcp, client):
    @mcp.tool()
    async def unione_template_set(
        name: str,
        body: dict,
        subject: str | None = None,
        template_engine: str = "simple",
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        global_substitutions: dict | None = None,
        global_metadata: dict | None = None,
        headers: dict | None = None,
        attachments: list[dict] | None = None,
        inline_attachments: list[dict] | None = None,
        template_id: str | None = None,
    ) -> dict:
        """Create/update a template (template/set.json). Pass template_id to update."""
        tpl = {"name": name, "template_engine": template_engine, "body": body}
        for k, v in {
            "subject": subject,
            "from_email": from_email,
            "from_name": from_name,
            "reply_to": reply_to,
            "global_substitutions": global_substitutions,
            "global_metadata": global_metadata,
            "headers": headers,
            "attachments": attachments,
            "inline_attachments": inline_attachments,
            "id": template_id,
        }.items():
            if v is not None:
                tpl[k] = v
        return await client.post("template/set.json", {"template": tpl})

    @mcp.tool()
    async def unione_template_get(id: str) -> dict:
        """Get a template by id (template/get.json)."""
        return await client.post("template/get.json", {"id": id})

    @mcp.tool()
    async def unione_template_list(limit: int = 50, offset: int = 0) -> dict:
        """List templates (template/list.json)."""
        return await client.post("template/list.json", {"limit": limit, "offset": offset})

    @mcp.tool()
    async def unione_template_delete(id: str) -> dict:
        """Delete a template by id (template/delete.json)."""
        return await client.post("template/delete.json", {"id": id})
