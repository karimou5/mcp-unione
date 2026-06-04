---
title: Webhooks
source: https://docs.unione.io/en/web-api-notifications
synced: 2026-06-04
---

## 4. Webhooks

### 4.1 Concept & operational rules

- You provide a URL; every time a watched event occurs, UniOne submits a request with JSON data to that URL.
- Configurable: format (JSON or gzipped JSON), which events, whether multiple events are grouped per request, and whether to include extra details (SMTP answer, recipient's user agent, etc.).
- **Your webhook handler should be able to process at least 5 parallel requests, up to 100 events each.** You can configure the max parallel connections **up to 100, which is recommended**.
- **Success response required:** your server must respond with **HTTP 200 OK within a 3-second timeout**.
- **Retry behavior:** if the URL is not available (no HTTP 200 OK within 3 s), the system **repeats requests every 10 minutes for 24 hours**, passing an extra parameter `retry_count`.
- **Auto-disable:** if there were **at least 10 distinct events** in the last 24 hours and **all** webhook requests about them failed, UniOne considers the handler broken and **automatically changes its status to inactive/`stopped`**. A notification is emailed to the address configured in the control panel.

### 4.2 Webhook management methods

| Method | Endpoint |
|---|---|
| `webhook/set` | `POST https://api.unione.io/en/transactional/api/v1/webhook/set.json` (creates **or edits** a webhook) |
| `webhook/get` | `POST https://api.unione.io/en/transactional/api/v1/webhook/get.json` |
| `webhook/list` | `POST https://api.unione.io/en/transactional/api/v1/webhook/list.json` |
| `webhook/delete` | `POST https://api.unione.io/en/transactional/api/v1/webhook/delete.json` |

Authentication for these management calls uses the `X-API-KEY: <API_KEY>` header (plus `Content-Type: application/json`, `Accept: application/json`).

### 4.3 `webhook/set` parameters

```json
{
  "url": "https://yourhost.example.com/unione-webhook",
  "status": "active",
  "event_format": "json_post",
  "delivery_info": 0,
  "single_event": 0,
  "max_parallel": 10,
  "events": {
    "spam_block": [
      "*"
    ],
    "email_status": [
      "delivered",
      "opened",
      "clicked",
      "unsubscribed",
      "subscribed",
      "soft_bounced",
      "hard_bounced",
      "spam"
    ]
  }
}
```

| Name | Type | Required | Description |
|---|---|---|---|
| `url` | string(uri) | Required | URL that receives the notification. **Must be unique** for a user or a project. Only ASCII supported — convert to Punycode for non-ASCII. |
| `status` | string | Optional | Webhook status, **`active`** by default. **`disabled`** = disabled by the user; **`stopped`** = stopped by the system after 24 h of failed calls (min. 10 distinct events). |
| `event_format` | string | Optional | Notification format. **`json_post`** (default) or **`json_post_gzip`**. |
| `delivery_info` | integer | Optional | Whether detailed delivery info is returned (`1`) or not (`0`). When `1`: SMTP response + internal delivery status returned for `hard_bounced` and `soft_bounced`; user agent, recipient IP and geo for `opened`/`clicked`; URL for `clicked`. For `delivered`/`soft_bounced`/`hard_bounced` UniOne may also return `sender_ip` (the sending SMTP server IP) if available. |
| `single_event` | integer | Optional | `0` = several event notifications may be reported in a single webhook call; `1` = only a single event per call (**not recommended**). |
| `max_parallel` | integer | Optional | Maximum number of permitted parallel queries to your server. The more your server can handle, the better (up to 100). |
| `events` | object | Optional | Object containing the events to notify of. |
| `events.spam_block` | array | Optional | If present, spam-block events are reported. **Should contain a single array element with the `"*"` string.** |
| `events.email_status` | array | Optional | If present, email-status change events are reported. Contains the names of statuses to notify of (subset of the `email_status` enum). |

**`webhook/set` 200 response** (echoes the stored object, adding `id` and `updated_at`):

```json
{
  "status": "success",
  "object": {
    "id": 0,
    "url": "http://example.com",
    "status": "active",
    "event_format": "json_post",
    "delivery_info": 0,
    "single_event": 0,
    "max_parallel": 10,
    "updated_at": "string",
    "events": {
      "spam_block": ["*"],
      "email_status": [
        "delivered", "opened", "clicked", "unsubscribed",
        "subscribed", "soft_bounced", "hard_bounced", "spam"
      ]
    }
  }
}
```

- `object.id` — integer — webhook unique identifier.
- `object.updated_at` — string(utc-date-time) — last update in UTC, `"YYYY-MM-DD hh:mm:ss"` format.

**`webhook/delete`** takes `{ "url": "https://example.com/webhook" }` and returns `{ "status": "success" }`. You can also temporarily deactivate a webhook (without deleting) by setting `status` to `disabled` in `webhook/set`.

Error response for all webhook methods: `{ "status": "error", "message": "<English message>", "code": <integer> }`.

---

## 5. Webhook callback format — the exact JSON UniOne POSTs to your endpoint

UniOne generates **two types** of events distinguished by `event_name`:

- **`transactional_email_status`** — email delivery-status change event (you can subscribe to selected statuses only).
- **`transactional_spam_block`** — event of activating/deactivating a spam block for single or multiple SMTP servers.

### 5.1 Full sample payload

```http
POST https://yourhost.example.com/unione-webhook HTTP/1.1
Host: yourhost.example.com
Content-Type: application/json
```
```json
{
  "auth": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "events_by_user": [
    {
      "user_id": 456,
      "project_id": "6432890213745872",
      "project_name": "MyProject",
      "events": [
        {
          "event_name": "transactional_email_status",
          "event_data": {
            "job_id": "1a3Q2V-0000OZ-S0",
            "metadata": {
              "key1": "val1",
              "key2": "val2"
            },
            "email": "recipient.email@example.com",
            "status": "sent",
            "event_time": "2015-11-30 15:09:42",
            "url": "http://some.url.com",
            "delivery_info": {
              "delivery_status": "err_delivery_failed",
              "destination_response": "550 Spam rejected",
              "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
              "ip": "111.111.111.111",
              "country_code": "DE",
              "country": "Germany",
              "city": "Berlin",
              "sender_ip": "192.0.2.10"
            }
          }
        },
        {
          "event_name": "transactional_spam_block",
          "event_data": {
            "block_time": "YYYY-MM-DD HH:MM:SS",
            "block_type": "one_smtp",
            "domain": "domain_name",
            "SMTP_blocks_count": 8,
            "domain_status": "blocked"
          }
        }
      ]
    }
  ]
}
```

### 5.2 Top-level / envelope fields

| Name | Type | Required | Description |
|---|---|---|---|
| `auth` | string | Required | **MD5-hash of the message body, in which the value of `auth` is replaced by the API key** of the user/project. With this field the recipient can both **authenticate** and **verify the integrity** of the notification. |
| `events_by_user` | array | Required | Array with **only one element**, containing the events of a user/project. |
| `events_by_user[].user_id` | integer | Required | Unique user identifier. |
| `events_by_user[].project_id` | string | Optional | Project identifier — present only if the webhook was registered for the project using a project API key. |
| `events_by_user[].project_name` | string | Optional | Project name — present only if registered for the project using a project API key. |
| `events_by_user[].events` | array | Required | Array of events reported by the webhook. |
| `events[].event_name` | string | Optional | `"transactional_email_status"` or `"transactional_spam_block"`. |
| `events[].event_data` | object | Optional | Event properties; shape depends on `event_name`. |

### 5.3 `event_data` for `transactional_email_status`

| Name | Type | Description |
|---|---|---|
| `job_id` | string | Job identifier returned earlier by `email/send`. |
| `metadata` | object | Metadata passed in `email/send` (`recipients.metadata` or `global_metadata`). |
| `email` | string(email) | Recipient's email. |
| `status` | string | Email delivery status (see §1.2 enum: `accepted`, `sent`, `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam`). |
| `event_time` | string(utc-date-time) | Event date & time in UTC, `"YYYY-MM-DD hh:mm:ss"`. |
| `url` | string(uri) | URL for `opened` and `clicked` statuses. |
| `delivery_info` | object | Detailed delivery info. **Present only if the webhook's `delivery_info` property is set to `1`** and `event_name = transactional_email_status`. |

**`delivery_info` sub-object:**

| Name | Type | Description |
|---|---|---|
| `delivery_status` | string | UniOne internal detailed delivery status (see §2 for the full list). |
| `destination_response` | string | SMTP response (e.g. `"550 Spam rejected"`). |
| `user_agent` | string | Recipient's user agent. Present only if detected, for `clicked`/`opened`. |
| `ip` | string | Recipient's IP address. Present only if detected, for `clicked`/`opened`. |
| `country_code` | string | ISO 3166-1 alpha-2 country code from recipient IP. Present for `clicked`/`opened`. |
| `country` | string | Country detected from recipient IP. Present for `clicked`/`opened`. |
| `city` | string | City detected from recipient IP. Present for `clicked`/`opened`. |
| `sender_ip` | string | IP of the SMTP server that sent the message. Present only for `delivered`, `soft_bounced`, `hard_bounced`, if available. |

### 5.4 `event_data` for `transactional_spam_block`

| Name | Type | Description |
|---|---|---|
| `block_time` | string(utc-date-time) | Spam-block date & time in UTC, `"YYYY-MM-DD hh:mm:ss"`. |
| `block_type` | string | Spam block type — single or multiple sending SMTP. For a single SMTP block in the common pool, UniOne retries several other SMTPs. Observed values: `one_smtp`, `all_smtp`. |
| `domain` | string | The (recipient's) domain that blocked sending. |
| `SMTP_blocks_count` | integer | Number of sending SMTPs blocked. |
| `domain_status` | string | Whether it's a block or unblock event — `blocked` or `unblocked`. |

### 5.5 Authentication / signing model

- There is **no separate signature header**. Authentication and integrity verification are done via the body-level `auth` field.
- To verify: take the **received JSON body**, replace the value of the `auth` field with your **API key** (user or project API key, matching how the webhook was registered), compute the **MD5** of the resulting body, and compare it with the received `auth` value. A match authenticates UniOne as the sender and confirms the payload was not altered.
- Expected response from your endpoint: **HTTP 200 OK within 3 seconds**, otherwise the call is retried (see §4.1).

---

## 6. Spam blocking (`spam_block` events)

### 6.1 What it is

UniOne applies **automatic spam blocking** per its anti-spam policy. When recipient mail servers reject your messages as spam, UniOne progressively blocks the sending SMTP servers and, ultimately, sending to the recipient domain.

### 6.2 General principles of spam blocking

- If a user's emails sent from **one UniOne SMTP server** are rejected as spam by the recipient's server (e.g. gmail, hotmail.com, etc.) **10 times**, the system blocks sending from that current SMTP server and continues with other servers.
- If **5 UniOne servers are blocked for a particular domain**, the system **restricts sending to that domain** and will no longer try to send to recipients from that domain.

### 6.3 Getting spam-block info

Subscribe a webhook with `events: { "spam_block": ["*"] }`. UniOne then sends `transactional_spam_block` events. The returned `event_data`:

```json
{
  "event_name": "transactional_spam_block",
  "event_data": {
    "block_time": "YYYY-MM-DD HH:MM:SS",
    "block_type": "one_smtp",
    "domain": "domain_name",
    "SMTP_blocks_count": 8,
    "domain_status": "blocked"
  }
}
```

| Field | Meaning (spam-blocking article) |
|---|---|
| `block_time` | Outgoing SMTP blocking time (UTC). |
| `block_type` | `one_smtp` (a single SMTP was blocked) or `all_smtp` (all SMTPs were blocked for the recipient's domain). |
| `domain` | Recipient's domain name. |
| `SMTP_blocks_count` | Counter showing the quantity of blocked SMTPs. |
| `domain_status` | `blocked` or `unblocked` — whether the current domain is allowed to send to. |

> If a domain is restricted but you are sure your content is acceptable (not spam), contact UniOne support to resolve it.

---
