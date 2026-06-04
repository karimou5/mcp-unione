import logging

from ..models import Attachment, Body, Engine, Recipient

log = logging.getLogger("mcp_unione")


def register(mcp, client):
    @mcp.tool()
    async def unione_send_email(
        recipients: list[Recipient],
        subject: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        reply_to_name: str | None = None,
        body: Body | None = None,
        template_id: str | None = None,
        template_engine: Engine = "simple",
        global_substitutions: dict | None = None,
        global_metadata: dict | None = None,
        global_language: str | None = None,
        tags: list[str] | None = None,
        headers: dict | None = None,
        attachments: list[Attachment] | None = None,
        inline_attachments: list[Attachment] | None = None,
        track_links: int = 1,
        track_read: int = 1,
        skip_unsubscribe: int = 0,
        bypass_global: int = 0,
        bypass_unavailable: int = 0,
        bypass_unsubscribed: int = 0,
        bypass_complained: int = 0,
        idempotence_key: str | None = None,
        sandbox: bool = False,
        confirm_send: bool = False,
    ) -> dict:
        """Send a transactional email via UniOne email/send.json.

        SAFETY: real sends require confirm_send=true. Without it, returns a preview
        and sends nothing. body OR template_id is required. ≤500 recipients.
        template_engine: simple|velocity|liquid|none. Unsubscribe token:
        {{UnsubscribeUrl}} (simple) / $UnsubscribeUrl (velocity).
        """
        if not body and not template_id:
            return {"error": "Provide either `body` or `template_id`."}
        if len(recipients) > 500:
            return {"error": "UniOne allows at most 500 recipients per send."}
        message = {
            "recipients": [r.model_dump(exclude_none=True) for r in recipients],
            "template_engine": template_engine,
            "track_links": track_links,
            "track_read": track_read,
            "skip_unsubscribe": skip_unsubscribe,
            "bypass_global": bypass_global,
            "bypass_unavailable": bypass_unavailable,
            "bypass_unsubscribed": bypass_unsubscribed,
            "bypass_complained": bypass_complained,
        }
        opt = {
            "subject": subject,
            "from_email": from_email,
            "from_name": from_name,
            "reply_to": reply_to,
            "reply_to_name": reply_to_name,
            "template_id": template_id,
            "global_language": global_language,
            "global_substitutions": global_substitutions,
            "global_metadata": global_metadata,
            "tags": tags,
            "headers": headers,
            "body": body.model_dump(exclude_none=True) if body else None,
            "attachments": [a.model_dump() for a in attachments] if attachments else None,
            "inline_attachments": (
                [a.model_dump() for a in inline_attachments] if inline_attachments else None
            ),
            "idempotence_key": idempotence_key,
        }
        message.update({k: v for k, v in opt.items() if v is not None})
        if sandbox:
            message.setdefault("options", {})["sandbox"] = True  # routed to sandbox domain
        to = [r.email for r in recipients]
        if not confirm_send:
            return {
                "preview": True,
                "would_send": True,
                "from_email": from_email,
                "to": to,
                "subject": subject,
                "engine": template_engine,
                "recipient_count": len(to),
                "note": "Dry run. Re-call with confirm_send=true to actually send.",
            }
        log.info("UniOne send → %d recipient(s): %s", len(to), ", ".join(to))
        return await client.post("email/send.json", {"message": message})

    @mcp.tool()
    async def unione_subscribe(
        from_email: str, to_email: str, from_name: str | None = None
    ) -> dict:
        """Send a double opt-in subscription confirmation. POST email/subscribe.json."""
        payload = {"from_email": from_email, "to_email": to_email}
        if from_name:
            payload["from_name"] = from_name
        return await client.post("email/subscribe.json", payload)
