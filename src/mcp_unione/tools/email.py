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
        track_links/track_read default to 1 (UniOne default); pass 0 to disable.

        DELIVERABILITY / UNSUBSCRIBE: by default UniOne appends an unsubscribe footer to
        every message, e.g.:
            This message to <to> was sent from:
            <from_name> | <from_email>
            Unsubscribe
        Gmail often treats that footer as a marketing signal and files the email under the
        Promotions tab (or Spam for a young sending domain). For transactional mail, pass
        skip_unsubscribe=1 to drop the footer and improve inbox placement. Note:
        skip_unsubscribe must be enabled on your UniOne account first — if setting it has
        no visible effect (footer still present), contact UniOne support to turn it on.
        """
        if body is None and not template_id:
            return {"error": "Provide either `body` or `template_id`."}
        if body is not None and not body.model_dump(exclude_none=True):
            return {"error": "`body` has no content (all fields are None)."}
        if not recipients:
            return {"error": "At least one recipient is required."}
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
        message.update({k: v for k, v in opt.items() if v is not None and v != [] and v != {}})
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
    async def unione_subscribe(from_email: str, from_name: str, to_email: str) -> dict:
        """Send a double opt-in subscription confirmation via email/subscribe.json.

        Emails a confirmation request from `from_name <from_email>` to `to_email`,
        asking the recipient to confirm (opt in to) their subscription. When they click
        the confirmation link, UniOne records the consent and clears any prior
        unsubscribe for that address — the inverse of the unsubscribe footer.
        All three fields are required by UniOne; `from_email` must be on a verified
        sending domain. Returns {"status": "success"}.
        """
        return await client.post(
            "email/subscribe.json",
            {"from_email": from_email, "from_name": from_name, "to_email": to_email},
        )
