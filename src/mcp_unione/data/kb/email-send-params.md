---
title: email/send Parameters
source: https://docs.unione.io/en/web-api-email-send
synced: 2026-06-04
---

## 7.1 `email/send.json`

`POST /en/transactional/api/v1/email/send.json`
Sends an email or a bunch of emails. While sending you can provide substitutions (merge tags), use a template, turn on read/click tracking, etc.

**Restrictions:**
- maximum request size is **10 MB**
- maximum number of recipients is **500**
- the symbol `/` is not allowed in attachment names
- if the recipient list contains invalid, non-existent, duplicate, or unsubscribed emails, those are returned in `failed_emails` and the email is still sent to the other valid addresses.
- if **all** addresses fall into `failed_emails`, sending is not carried out and **API error 204** is returned.

### Parameters (all under top-level `message` object)

| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `message` | object | **Required** | — | — | Object containing all message properties. |
| `message.recipients` | array | **Required** | — | max 500 | Array of recipients with emails, substitutions and metadata. |
| `message.recipients[].email` | string(email) | **Required** | — | — | Recipient email. |
| `message.recipients[].substitutions` | object | Optional | — | — | Per-recipient substitutions (merge tags). Usable in `body.html`, `body.plaintext`, `body.amp`, `subject`, `from_name`, `headers["List-Unsubscribe"]`, `options.unsubscribe_url`. Names: latin chars/numbers/`_`, must start with a letter. Special `to_name` substitution puts the recipient name in the SMTP "To" header (max 78 chars). |
| `message.recipients[].metadata` | object | Optional | — | — | Per-recipient metadata `"key":"value"`. Max 10 keys; key ≤ 64 chars; value ≤ 1024 chars (combined ≤ 4000 bytes). Returned by webhook & event-dump. A `campaign_id` key (≤128-bit) is treated as campaign identifier in statistics. |
| `message.template_id` | string(uuid) | Optional | — | — | Identifier of a template created via `template/set`. Template fields fill in any omitted `email/send` fields (e.g. `body`, `subject`). |
| `message.tags` | array of strings | Optional | — | each ≤ 50 chars; up to 4; unique; ≤ 10000/project | Categorize emails; passed by event-dump. |
| `message.skip_unsubscribe` | integer | Optional | `0` | `0` = append footer, `1` = skip | Whether to skip appending the default unsubscribe footer. `1` requires support approval. |
| `message.global_language` | string | Optional | — | `be`,`de`,`en`,`es`,`fr`,`it`,`pl`,`pt`,`ru`,`ua`,`kz` | Language of unsubscribe footer & page. |
| `message.template_engine` | string | Optional | `simple` | `simple`, `velocity`, `liquid`, `none` | Template engine for handling substitutions. |
| `message.global_substitutions` | object | Optional | — | — | Substitutions common to all recipients (e.g. company name). Per-recipient `substitutions` override duplicates. Usable in `body.html/plaintext/amp`, `subject`, `from_name`, `options.unsubscribe_url`. |
| `message.global_metadata` | object | Optional | — | — | Metadata common to all recipients. Same limits as recipient metadata. System key `campaign_id` accepts a ≤128-bit non-negative integer or a UUID (`c7703772-...`); invalid values treated as `0`. |
| `message.body` | object | **Required** | — | — | HTML/plaintext/AMP parts; **either `html` or `plaintext` required**. |
| `message.body.html` | string | Optional | — | — | HTML part of the email body. |
| `message.body.plaintext` | string | Optional | — | — | Plaintext part. |
| `message.body.amp` | string | Optional | — | — | AMP part. |
| `message.subject` | string | **Required** | — | — | Email subject. |
| `message.from_email` | string(email) | Optional* | — | — | Sender's email. *Required only if `template_id` is empty. Must be on a verified domain. |
| `message.from_name` | string | Optional | — | — | Sender's name. |
| `message.reply_to` | string | Optional | — | — | Reply-To email (if different from sender). |
| `message.reply_to_name` | string | Optional | — | — | Reply-To name (if `reply_to` set and you want a display name). |
| `message.track_links` | integer | Optional | `1` | `0`,`1` | `1` = click tracking on (default), `0` = off (needs support to enable). |
| `message.track_read` | integer | Optional | `1` | `0`,`1` | `1` = read tracking on (default), `0` = off (needs support to enable). |
| `message.bypass_global` | integer | Optional | `0` | `0`,`1` | `1` = ignore the global unavailability list. May be ignored for some addresses. |
| `message.bypass_unavailable` | integer | Optional | `0` | `0`,`1` | `1` = ignore current user's/project's unavailability list. Works only if `bypass_global=1`. |
| `message.bypass_unsubscribed` | integer | Optional | `0` | `0`,`1` | `1` = ignore unsubscribed list. Works only if `bypass_global=1`; requires the "omit unsubscribe link" right (support). |
| `message.bypass_complained` | integer | Optional | `0` | `0`,`1` | `1` = ignore complaint list. Works only if `bypass_global=1`; requires "omit unsubscribe link" right (support). |
| `message.idempotence_key` | string | Optional | — | ≤ 64 chars | Unique message key to prevent duplicates; resending the same key within 1 minute is declined. |
| `message.headers` | object | Optional | — | max 50 | Email headers. Only `X-` prefixed accepted (others ignored), e.g. `X-UNIONE-Global-Language`, `X-UNIONE-Template-Engine`. Standard `To`/`CC`/`BCC` passed without `X-` (with restrictions). With support approval: `List-Unsubscribe`, `List-Subscribe`, `List-Help`, `List-Owner`, `List-Archive`, `In-Reply-To`, `References`. |
| `message.headers["X-UNIONE-Global-Language"]` | string | Optional | — | `be`,`de`,`en`,`es`,`fr`,`it`,`pl`,`pt`,`ru`,`ua`,`kz` | Unsubscribe footer/page language. |
| `message.headers["X-UNIONE-Template-Engine"]` | string | Optional | `simple` | `simple`,`velocity`,`liquid`,`none` | Template engine; has priority over `template_engine`. |
| `message.attachments` | array | Optional | — | — | Array of attachments. |
| `message.attachments[].type` | string | **Required** | — | MIME type | Attachment MIME type; if unsure use `application/octet-stream`. |
| `message.attachments[].name` | string | **Required** | — | unique; no `/`; ≤ 255 bytes | Filename `name.extension`. |
| `message.attachments[].content` | string(byte) | **Required** | — | ≤ 7 MB (9786710 bytes base64) | File contents in base64. |
| `message.inline_attachments` | array | Optional | — | — | Inline attachments (e.g. embed images by CID). |
| `message.inline_attachments[].type` | string | **Required** | — | MIME type | Attachment MIME type. |
| `message.inline_attachments[].name` | string | **Required** | — | — | Content ID; referenced in HTML as `<img src="cid:NAME">` (e.g. `IMAGECID1`). |
| `message.inline_attachments[].content` | string(byte) | **Required** | — | ≤ 7 MB | File contents in base64. |
| `message.options` | object | Optional | — | — | Additional message options. |
| `message.options.send_at` | string | Optional | — | `YYYY-MM-DD hh:mm:ss` UTC | Schedule sending up to 24h in advance. |
| `message.options.unsubscribe_url` | string | Optional | — | — | Custom unsubscribe link. |
| `message.options.custom_backend_id` | integer | Optional | — | — | Backend-domain (dedicated IP) identifier. Default used if absent. |
| `message.options.smtp_pool_id` | string(uuid) | Optional | — | — | SMTP pool identifier; usually auto-selected (requires `custom_backend_id` if passed). |

**Request body example:**
```json
{
  "message": {
    "recipients": [
      { "email": "email@example.com",
        "substitutions": { "tag": "value" },
        "metadata": { "key": "value" } }
    ],
    "template_id": "00000000-0000-0000-0000-000000000000",
    "tags": [],
    "skip_unsubscribe": 0,
    "global_language": "en",
    "template_engine": "velocity",
    "global_substitutions": { "property1": "string", "property2": "string" },
    "global_metadata": { "property1": "string", "property2": "string" },
    "body": {
      "html": "<b>Hello, {{to_name}}</b>",
      "plaintext": "Hello, {{to_name}}",
      "amp": "<!doctype html><html amp4email>...</html>"
    },
    "subject": "UniOne test email",
    "from_email": "email@example.com",
    "from_name": "John Smith",
    "reply_to": "email@example.com",
    "reply_to_name": "John Smith",
    "track_links": 0,
    "track_read": 0,
    "bypass_global": 0,
    "bypass_unavailable": 0,
    "bypass_unsubscribed": 0,
    "bypass_complained": 0,
    "idempotence_key": "SG1VsbG68sIH2dvc5mx890kIQ",
    "headers": { "X-MyHeader": "some data" },
    "attachments": [ { "type": "text/plain", "name": "readme.txt", "content": "SGVsbG8sIHdvcmxkIQ==" } ],
    "inline_attachments": [ { "type": "image/gif", "name": "IMAGECID1", "content": "R0lGODdh..." } ],
    "options": {}
  }
}
```

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `job_id` | string | Required | Job identifier (useful for error investigation). |
| `emails` | array | Optional | Recipient emails successfully accepted for sending. |
| `failed_emails` | object | Optional | Map of rejected email → status. Possible statuses: `unsubscribed`, `invalid`, `duplicate`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` (new statuses may be added). |

```json
{
  "status": "success",
  "job_id": "1ZymBc-00041N-9X",
  "emails": ["user@example.com"],
  "failed_emails": {
    "email1@gmail.com": "temporary_unavailable",
    "bad@address": "invalid",
    "email@example.com": "duplicate",
    "root@example.org": "permanent_unavailable",
    "olduser@example.net": "unsubscribed"
  }
}
```

**`failed_emails` status meanings:**
- `unsubscribed` — the email is unsubscribed.
- `invalid` — the email does not exist or is malformed.
- `duplicate` — already present in the request (duplication prevented).
- `temporary_unavailable` — unavailable; for the next 3 days sending will error (spam rejection, full/unused mailbox, domain not accepting mail, blacklisted sending server, etc.).
- `permanent_unavailable` — permanently unavailable or globally unsubscribed.
- `complained` — recipient reported spam in previous emails.
- `blocked` — sending prohibited by UniOne administration.

---
