from __future__ import annotations


def register(mcp, client=None):
    @mcp.prompt()
    def compose_transactional_email(goal: str = "") -> str:
        """Guide the model to assemble a valid unione_send_email call."""
        return (
            "You are composing a UniOne transactional email.\n"
            f"Goal: {goal}\n\n"
            "Collect/confirm: from_email (on a verified domain), recipient(s), subject, "
            "and body.html (+ optional plaintext) OR a template_id.\n"
            "Pick template_engine (simple|velocity|liquid). Include the unsubscribe token "
            "({{UnsubscribeUrl}} for simple, $UnsubscribeUrl for velocity) unless skip_unsubscribe=1.\n"
            "Then call unione_send_email with confirm_send=false first to preview, then "
            "confirm_send=true to send. Use unione_validate_email for risky addresses."
        )

    @mcp.prompt()
    def diagnose_delivery(status_or_error: str = "") -> str:
        """Guide the model to explain a delivery status / error code."""
        return (
            f"Diagnose this UniOne status or error: '{status_or_error}'.\n"
            "Call unione_lookup_status for an email/delivery_status, or unione_lookup_error "
            "for a numeric API code. Then consult resources unione-docs://email-statuses, "
            "unione-docs://delivery-status-codes, or unione-docs://error-codes and summarize "
            "the cause and the fix."
        )
