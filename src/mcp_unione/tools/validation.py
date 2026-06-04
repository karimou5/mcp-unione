def register(mcp, client):
    @mcp.tool()
    async def unione_validate_email(email: str) -> dict:
        """Validate one address (email-validation/single.json). Response result:
        valid|invalid|suspicious|unknown, plus cause, validity (0-100), mx_found, did_you_mean."""
        return await client.post("email-validation/single.json", {"email": email})
