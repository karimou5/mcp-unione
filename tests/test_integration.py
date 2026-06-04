from mcp_unione.server import build_server

EXPECTED_TOOLS = {
    # email
    "unione_send_email",
    "unione_subscribe",
    # validation
    "unione_validate_email",
    # template
    "unione_template_set",
    "unione_template_get",
    "unione_template_list",
    "unione_template_delete",
    # webhook
    "unione_webhook_set",
    "unione_webhook_get",
    "unione_webhook_list",
    "unione_webhook_delete",
    # suppression
    "unione_suppression_set",
    "unione_suppression_get",
    "unione_suppression_list",
    "unione_suppression_delete",
    # domain
    "unione_domain_get_dns_records",
    "unione_domain_validate_verification_record",
    "unione_domain_validate_dkim",
    "unione_domain_list",
    "unione_domain_delete",
    # event-dump
    "unione_event_dump_create",
    "unione_event_dump_get",
    "unione_event_dump_list",
    "unione_event_dump_delete",
    # tag
    "unione_tag_list",
    "unione_tag_delete",
    # project
    "unione_project_create",
    "unione_project_update",
    "unione_project_list",
    "unione_project_delete",
    # system
    "unione_system_ping",
    "unione_system_info",
    # docs
    "unione_search_docs",
    "unione_fetch_doc_page",
    "unione_lookup_error",
    "unione_lookup_status",
}

EXPECTED_PROMPTS = {"compose_transactional_email", "diagnose_delivery"}


async def test_full_surface(monkeypatch):
    monkeypatch.setenv("UNIONE_API_KEY", "k")
    mcp = build_server()

    tools = {t.name for t in await mcp.list_tools()}
    missing = EXPECTED_TOOLS - tools
    assert not missing, f"missing tools: {missing}"

    prompts = {p.name for p in await mcp.list_prompts()}
    assert EXPECTED_PROMPTS <= prompts, f"missing prompts: {EXPECTED_PROMPTS - prompts}"
