def register(mcp, client):
    @mcp.tool()
    async def unione_domain_get_dns_records(domain: str) -> dict:
        """Get required DNS records (domain/get-dns-records.json). Returns verification-record
        and dkim (key part only — prepend 'v=DKIM1; k=rsa; p=' for the published value; selector us._domainkey)."""
        return await client.post("domain/get-dns-records.json", {"domain": domain})

    @mcp.tool()
    async def unione_domain_validate_verification_record(domain: str) -> dict:
        """Re-validate the ownership TXT record (domain/validate-verification-record.json)."""
        return await client.post(
            "domain/validate-verification-record.json", {"domain": domain}
        )

    @mcp.tool()
    async def unione_domain_validate_dkim(domain: str) -> dict:
        """Re-validate DKIM (domain/validate-dkim.json). Async: 200 means validation started."""
        return await client.post("domain/validate-dkim.json", {"domain": domain})

    @mcp.tool()
    async def unione_domain_list(
        domain: str | None = None, limit: int = 50, offset: int = 0
    ) -> dict:
        """List domains + verification/dkim status (domain/list.json)."""
        p = {"limit": limit, "offset": offset}
        if domain is not None:
            p["domain"] = domain
        return await client.post("domain/list.json", p)

    @mcp.tool()
    async def unione_domain_delete(domain: str) -> dict:
        """Delete a domain (domain/delete.json)."""
        return await client.post("domain/delete.json", {"domain": domain})
