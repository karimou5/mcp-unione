def register(mcp, client):
    @mcp.tool()
    async def unione_webhook_set(
        url: str,
        events: dict,
        status: str = "active",
        event_format: str = "json_post",
        delivery_info: int = 1,
        single_event: int = 0,
        max_parallel: int = 10,
    ) -> dict:
        """Create/update a webhook (webhook/set.json).
        status: active|disabled|stopped. event_format: json_post|json_post_gzip.
        events: {"email_status":[delivered,opened,clicked,unsubscribed,subscribed,
        soft_bounced,hard_bounced,spam], "spam_block":["*"]}."""
        return await client.post(
            "webhook/set.json",
            {
                "url": url,
                "events": events,
                "status": status,
                "event_format": event_format,
                "delivery_info": delivery_info,
                "single_event": single_event,
                "max_parallel": max_parallel,
            },
        )

    @mcp.tool()
    async def unione_webhook_get(url: str) -> dict:
        """Get a webhook by url (webhook/get.json)."""
        return await client.post("webhook/get.json", {"url": url})

    @mcp.tool()
    async def unione_webhook_list(limit: int = 50, offset: int = 0) -> dict:
        """List webhooks (webhook/list.json)."""
        return await client.post("webhook/list.json", {"limit": limit, "offset": offset})

    @mcp.tool()
    async def unione_webhook_delete(url: str) -> dict:
        """Delete a webhook by url (webhook/delete.json)."""
        return await client.post("webhook/delete.json", {"url": url})
