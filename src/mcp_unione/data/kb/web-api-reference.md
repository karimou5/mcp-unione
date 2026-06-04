---
title: Web API Reference
source: https://docs.unione.io/en/web-api
synced: 2026-06-04
---

## 1. Transport, Base URLs & Request Envelope

- All UniOne API methods **require an HTTPS connection**.
- UniOne accepts **HTTP POST** requests in **JSON** format, **up to 10 megabytes** long, and returns the HTTP response also in **JSON**.
- The API endpoint (base URL) depends on which datacenter the user is registered at.

**Base URLs (full path `/en/transactional/api/v1`):**

| Base URL | Notes |
|---|---|
| `https://api.unione.io/en/transactional/api/v1` | **Preferred** — UniOne API-server instance (auto-routes to your datacenter). |
| `https://eu1.unione.io/en/transactional/api/v1` | EU datacenter — use directly if your account was registered there. |
| `https://us1.unione.io/en/transactional/api/v1` | US datacenter — use directly if your account was registered there. |

A method is invoked by appending the method path, e.g.:
`POST https://api.unione.io/en/transactional/api/v1/email/send.json`

**Request envelope (HTTP):**

```
POST https://api.unione.io/en/transactional/api/v1/email/send.json HTTP/1.1
Host: api.unione.io
Content-Type: application/json
Accept: application/json
X-API-KEY: <your-api-key>

{ "message": { ... } }
```

- `Content-Type: application/json`
- `Accept: application/json`
- The JSON body is the request payload (each method documents its own top-level fields).

---

## 2. Authentication

Every method call requires authentication by providing the **user API key** or **project API key** in **either of two places**:

| Mechanism | Where | Field/Header name |
|---|---|---|
| HTTP header | Request headers | `X-API-KEY` |
| JSON body field | Request body | `api_key` |

- The **user API key** is obtained in account settings (`https://cp.unione.io/en/user/info/api`).
- The **project API key** is obtained on the Projects page (`https://cp.unione.io/en/user/project`) or via the `project/*` API methods (`project/create`, `project/list`).
- A **project API key** can be used in place of the user API key in **all methods except `project/*` methods**.

---

## 3. Response Envelope

### Success
A successful call returns **HTTP 200** with a JSON object whose `status` field is the string `"success"`, plus method-specific fields:

```json
{ "status": "success", ... }
```

### Error
On failure the call returns an HTTP code other than 200, usually accompanied by a JSON error object:

```json
{ "status": "error", "code": 150, "message": "An unknown internal error occurred" }
```

| Field | Type | Description |
|---|---|---|
| `status` | string | Always contains `"error"`. |
| `code` | integer | API error code (do **not** confuse with the HTTP code). |
| `message` | string | Human-readable error message in English. |

---

## 4. HTTP Status Codes (transport level)

| HTTP Code | Meaning |
|---|---|
| 200 | OK – Request was successfully processed. |
| 400 | Bad Request – Your request is invalid. Check request format and parameters. |
| 401 | Unauthorized – Your API key is wrong. |
| 403 | Forbidden – Not enough rights to process the request. |
| 404 | Not Found – The specified endpoint not found. |
| 413 | Request Entity Too Large – Request size is too large, reduce size to 10 MB. |
| 429 | Too Many Requests – Please slow down request rate. |
| 50x | Internal Server Error – Problem on the server (500, 502, 503, etc.). Try again later. |

The HTTP error code gives generic information; a JSON object (see §3) usually accompanies it with the API error code (see §6).

---

## 5. Rate Limits & Size Limits (documented)

- **Request body size**: max **10 MB** (HTTP 413 / API code 199 if exceeded).
- **`email/send`**: max **500 recipients** per request; max request size 10 MB.
- **Attachments / inline attachments**: max file size **7 MB** (= 9 786 710 bytes in base64); attachment name max 255 bytes; `/` not allowed in names.
- **`email-validation/single`**: a maximum of **2 concurrent requests** are allowed; exceeding returns an error (API code 3800 cites 4 concurrent in one message variant — the page text states 2). Also a per-day call limit (API code 3803).
- **HTTP 429** ("Too Many Requests – please slow down request rate") is the generic throttling response — no fixed numeric request-per-second rate is published in the reference.
- **Per-user daily sending limit** exists (auto-increases with good delivery, resets nightly) — API codes 901/902/906.
- **Tags**: max 10 000 per project; max 4 per email; ≤ 50 chars each.
- **Templates**: max 10 000 per account.
- **Event dumps**: max 10 concurrent dumps per user; data retained up to 32 days (tariff-dependent).
- **Scheduled send** (`options.send_at`): up to 24 hours in advance.
- **Metadata**: max 10 keys; key ≤ 64 chars; value ≤ 1024 chars; total metadata ≤ 4000 bytes.

---

## 9. Quick Enum Reference

| Concept | Allowed values |
|---|---|
| `template_engine` / `X-UNIONE-Template-Engine` | `simple` (default), `velocity`, `liquid`, `none` |
| `global_language` / `X-UNIONE-Global-Language` | `be`, `de`, `en`, `es`, `fr`, `it`, `pl`, `pt`, `ru`, `ua`, `kz` |
| `editor_type` (template) | `html` (default), `visual` |
| webhook `status` | `active` (default), `disabled`, `stopped` |
| webhook `event_format` | `json_post` (default), `json_post_gzip` |
| webhook `email_status` events | `accepted`, `sent`, `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam` |
| webhook `spam_block` | single element `"*"` |
| webhook `event_name` | `transactional_email_status`, `transactional_spam_block` |
| suppression `cause` | `unsubscribed`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` |
| suppression `source` | `user`, `system`, `subscriber` |
| email validation `result` | `valid`, `invalid`, `suspicious`, `unknown` |
| email validation `cause` | `no_mx_record`, `syntax_error`, `possible_typo`, `mailbox_not_found`, `global_suppression`, `disposable`, `role`, `abuse`, `spamtrap`, `smtp_connection_failed` |
| event-dump `format` | `csv` (default), `csv_gzip` |
| event-dump `delimiter` | `,` (default), `;` |
| event-dump `aggregate` | `day_status`, `""` (empty/default) |
| event-dump `status` (filter) | `accepted`, `sent`, `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam` |
| event-dump `dump_status` | `queued`, `in_process`, `ready`, `failed` |
| project `email_counter_mode` | `default`, `permanent` |
| `failed_emails` values (email/send) | `unsubscribed`, `invalid`, `duplicate`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` |

---

*Document generated from the static HTML of the UniOne Web API v1.87 reference. The "Interactive API Request" widget at the bottom of the page is JS-rendered and contains no additional parameter documentation.*
