# UniOne — Email Statuses, Delivery Statuses, Webhooks, Spam Blocking & CC/BCC

> Exhaustive reference compiled verbatim from the official UniOne documentation.
>
> Sources:
> - https://docs.unione.io/en/email-statuses
> - https://docs.unione.io/en/web-api-ref (Webhook Methods + callback-format sections)
> - https://docs.unione.io/en/spam-blocking
> - https://docs.unione.io/en/cc-and-bcc
>
> All enum values, field names and JSON keys below are kept **verbatim**. Where the docs give two slightly different descriptions of the same `status` enum (the email-statuses article vs. the webhook callback-format reference), both are reproduced because they differ in wording, retry windows ("24 hours" vs "48 hours") and in which statuses exist (`accepted`, `subscribed` only appear in the webhook reference).

---

## 1. Email Statuses (`status` field)

The `status` field is returned via webhooks and downloaded using the `event-dump/*` methods. There are two documented descriptions of this enum.

### 1.1 Standard statuses (from the `email-statuses` article)

> "At the most basic level, there are eight standard email statuses."

| `status` | Meaning | Final? | Notes |
|---|---|---|---|
| `sent` | The email has been successfully checked and put in the queue for sending. At this stage we do not know yet whether it was delivered or not. | No | |
| `delivered` | The email has been successfully accepted by the recipient's mail server. Later this status may change to "opened", "clicked", "unsubscribed", or "spam". | No | |
| `opened` | The email has been delivered and read by the recipient. May still change to "clicked", "unsubscribed", or "spam". | No | Requires `track_read=1` when sending. |
| `clicked` | The email has been delivered and read, and the recipient has clicked one of the links. May change to "unsubscribed" or "spam". | No | Requires `track_links=1` in `email/send`. |
| `unsubscribed` | The email has been delivered and read, and the recipient has opted to unsubscribe (via the unsubscribe link or the `List-Unsubscribe` header). | **Yes** (per email-statuses article) | |
| `soft_bounced` | A transient error occurred while delivering. UniOne retries for **24 hours** from the first attempt. On success → `delivered`, otherwise → `hard_bounced`. | No | |
| `hard_bounced` | Delivery attempts failed; no further attempts. Common reasons: target address not available, message rejected as spam, mailbox has no free space. Extended info in `delivery_info.delivery_status`; full SMTP response in `delivery_info.destination_response`. | **Yes** | |
| `spam` | The message was successfully delivered and **manually marked as spam** by the addressee. Only available for FBL-supporting domains: `msn.com`, `outlook.com`, `hotmail.com`, `live.com`, `ukr.net`, `yahoo.com`, `aol.com`. | **Yes** | |

### 1.2 `status` enum as documented in the webhook callback-format reference

The webhook reference lists a **slightly different / extended** set of possible `status` values (note `accepted` and `subscribed` which are NOT in the 8-status list, and a **48-hour** soft-bounce window):

| `status` | Meaning (webhook reference wording) |
|---|---|
| `accepted` | The message has been accepted, but not sent yet. |
| `sent` | The message has been sent, but not delivered yet. |
| `delivered` | The message has been delivered. Can change to `opened`, `clicked`, `unsubscribed`, `subscribed` or `spam`. |
| `opened` | The message has been delivered and read. Can change to `clicked`, `unsubscribed`, `subscribed` or `spam`. |
| `clicked` | Delivered, read, and at least one link clicked. Can change to `unsubscribed`, `subscribed` or `spam`. |
| `unsubscribed` | Delivered and read, then the recipient unsubscribed. Can change to `subscribed`. |
| `subscribed` | Delivered and read; the recipient unsubscribed and then **subscribed again**. Can change to `unsubscribed`. |
| `soft_bounced` | Temporary delivery failure. UniOne retries during **48 hours**. On success → `delivered`; on failure to deliver within 48 hours → `hard_bounced`. |
| `hard_bounced` | Failed to deliver; no further attempts. Final status. Many possible reasons — use SMTP response in `delivery_info.destination_response` or UniOne classification in `delivery_info.delivery_status`. |
| `spam` | Delivered, but reported as spam by the recipient. UniOne receives/processes the complaint from several domains, including `msn.com`, `outlook.com`, `hotmail.com`, `live.com`, `ukr.net`, `yahoo.com`, `aol.com` using FBL. |

> The full set of `email_status` values you can subscribe a webhook to (see §3) is:
> `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam`.

---

## 2. Extended delivery statuses (`delivery_info.delivery_status`)

These appear when `delivery_info` is set to `1` on the webhook (or in CSV obtained via `event-dump/*`). They are derived from analyzing SMTP server responses.

> **Important caveat from UniOne:** "we do not provide an exhaustive list of extended statuses, and we cannot guarantee that the list will not be changed in the future; however, the semantics of existing statuses will remain unchanged." Extended statuses are not available for all events — if missing, rely on the standard statuses.

Below is **every** extended status documented, grouped by the system-action category UniOne uses in the email-statuses article.

### 2.1 Success

| `delivery_status` | Meaning |
|---|---|
| `ok_sent` | The message has been sent (intermediate status before delivery or non-delivery). |
| `ok_delivered` | The message has been delivered. |
| `ok_read` | The message has been delivered and opened by the recipient. |
| `ok_link_visited` | The message has been delivered and opened; the recipient clicked one of the links. |

### 2.2 Complaint or unsubscription

> The address is added to the list of complainers or unsubscribed addresses. Subsequent mailings to this address are blocked unless removed via `suppression/delete`.

| `delivery_status` | Meaning |
|---|---|
| `ok_spam_folder` | Delivered and placed into the Spam folder by the receiving server. |
| `ok_fbl` | Delivered and manually tagged as Spam by the recipient. |
| `ok_unsubscribed` | Delivered, and the addressee canceled the subscription using the unsubscribe link. |

### 2.3 Temporary failure (soft bounce — additional delivery attempts will be made)

| `delivery_status` | Meaning |
|---|---|
| `err_will_retry` | One or more delivery attempts were unsuccessful; the system will retry. **Not final.** |

### 2.4 Non-existent address

> The receiving SMTP server says the address does not exist. UniOne blocks sending to such addresses for a long period (6 months for most mailbox providers), after which the address is reactivated.

| `delivery_status` | Meaning |
|---|---|
| `err_user_unknown` | Address does not exist (and could never have existed). |
| `err_user_inactive` | A previously active address is no longer used; delivery has failed. |
| `err_mailbox_discarded` | The mailbox has been deleted. |

### 2.5 Rejected as spam

> The receiving SMTP server clearly stated the message will be rejected as spam. Does not always imply the next message from the same sender will also be declined.

| `delivery_status` | Meaning |
|---|---|
| `err_spam_rejected` | The message has been rejected as spam. |
| `err_spam_skipped` | Not sent because other messages from the same task were previously rejected by the recipient's server as spam. |
| `err_spam_removed` | Not sent because other messages from the same task were previously rejected as spam (same as previous, but at later stages of mailing). |

### 2.6 Long-term unreachable

> Numerous failed attempts in the past tagged the address as unreachable for a long period (6 months for most mailbox providers). Emails to such addresses are blocked.

| `delivery_status` | Meaning |
|---|---|
| `err_unreachable` | Address tagged as unreachable due to multiple delivery errors. |
| `skip_dup_unreachable` | Sending canceled because the address has been previously tagged as unreachable. |

### 2.7 Short-term unreachable

> Delivery attempts failed, but the address is tagged unreachable for only a few days, or is immediately available for further mailing.

| `delivery_status` | Meaning |
|---|---|
| `err_mailbox_full` | Mailbox is full. |
| `skip_dup_mailbox_full` | Sending canceled because recent attempts resulted in a "mailbox full" response. |
| `err_too_large` | The receiving server says the message is too large. |
| `err_unsubscribed` | The addressee has unsubscribed from your messages. |
| `err_blacklisted` | The message was rejected because the sender domain or IP was found on a blacklist. |
| `err_skip_letter` | Sending canceled because the target address is temporarily unreachable. |
| `err_domain_inactive` | The target domain does not exist or does not accept mail. |
| `err_destination_misconfigured` | The target domain does not accept mail due to a solvable issue (e.g. SMTP service temporarily down). |
| `skip_dup_temp_unreachable` | Sending canceled because the target address is temporarily unreachable. |
| `err_lost` | The email was not sent due to inconsistency of its structure, or lost due to an internal error. The user should re-send the letter. |
| `err_internal` | An internal error occurred. The user should re-send the letter. |
| `err_delivery_failed` | Delivery failed due to unspecified reasons. |

### 2.8 Additional `delivery_status` values listed only in the webhook reference

The webhook `callback-format` reference repeats several of the above and then adds the following note + extra values. UniOne states these are "provided as an example only, without any description" and reserves the right to change/add internal delivery statuses:

```
ok_sent, ok_delivered, ok_read, ok_link_visited, ok_unsubscribed,
ok_resubscribed, ok_spam_folder, ok_fbl, not_sent,
skip_dup_unreachable, skip_dup_temp_unreachable, skip_dup_mailbox_full,
err_spam_removed, err_resend, err_unknown, err_retry_letter,
err_src_invalid, err_dest_invalid, err_not_available, err_internal,
err_no_dns, err_no_smtp, err_giveup
```

Net-new values from this list (not in §2.1–2.7) are therefore:
`ok_resubscribed`, `not_sent`, `err_resend`, `err_unknown`, `err_retry_letter`, `err_src_invalid`, `err_dest_invalid`, `err_not_available`, `err_no_dns`, `err_no_smtp`, `err_giveup`.

The webhook reference also gives these short descriptions for the most common ones:

| `delivery_status` | Description (webhook reference) |
|---|---|
| `err_user_unknown` | email address doesn't exist |
| `err_user_inactive` | email address isn't used anymore |
| `err_will_retry` | email was temporarily rejected, delivery will be retried later |
| `err_mailbox_discarded` | email address was active earlier, but now it's deleted |
| `err_mailbox_full` | mailbox is full |
| `err_spam_rejected` | email was rejected as spam |
| `err_blacklisted` | email rejected because sender IP or sender domain is found in a blacklist |
| `err_too_large` | email size is over limit, according to recipient's server |
| `err_unsubscribed` | email was unsubscribed |
| `err_unreachable` | numerous delivery failures lead to marking this email address as permanently unavailable |
| `err_skip_letter` | sending canceled because the email address is temporarily unavailable |
| `err_domain_inactive` | the domain does not accept mail or does not exist |
| `err_destination_misconfigured` | the domain does not accept mail due to incorrect settings on the recipient's side; the server response contains a fixable cause (e.g. an inoperative blacklist) |
| `err_delivery_failed` | delivery failed due to other reasons |
| `err_spam_skipped` | sending canceled because the campaign has been blocked as spam |
| `err_lost` | not sent due to inconsistency of its parts, or lost due to failure on UniOne's side; sender must re-send (original not saved) |

---

## 3. Reasons to block sending (`email/send` blocking reasons)

When UniOne refuses to send a particular email, `email/send` returns the reason. These are **not the same as a delivery status** but are logically related. Also obtainable via `suppression/get` and `suppression/list`.

| Reason | Meaning |
|---|---|
| `unsubscribed` | The addressee unsubscribed (link in body / `List-Unsubscribe` header), or was added via `suppression/set`. |
| `temporary_unavailable` | One or more previous attempts failed; address tagged "temporarily unavailable". Cleared in a few days. Underlying causes (mailbox full, spam block, etc.) are described in the extended statuses table. |
| `permanent_unavailable` | Address permanently unavailable, verified by multiple sending attempts. Usually in effect ~half a year. |
| `complained` | The addressee tagged a previous letter as spam, complained in another form, or was added via `suppression/set`. |
| `blocked` | Address blocked by the system (small number — mostly spam traps or addresses like `support@gmail.com` that don't belong to a person). |
| `invalid` | The target address is invalid (e.g. the `@` sign is missing). |
| `duplicate` | The address was included in the same `email/send` call more than once. |

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

## 7. Sending CC and BCC (copies / blind copies)

You can send copies so each addressee sees the others in `To:` / `CC:`, or send a blind copy (BCC).

### 7.1 Via Web API (`email/send`)

The `email` parameter indicates the **primary recipient**; the `To:` and `CC:` headers carry the other addresses. Specify the headers in the `headers` parameter — UniOne sends them **as-is** (only MIME-encoding if necessary). Every address that should receive the email must also appear in the `recipients` array.

Simple example (John as primary, Mary as CC):

```json
"recipients": [
  {"email": "user@example.com"},
  {"email": "сс@example.org"}
],
"headers": {
  "To": " John <user@example.com>",
  "CC": " Mary <cc@example.org>"
}
```

Complex example (To: Miguel & José; CC: Helen & Habib; BCC: bcc@example.net — note the BCC recipient is in `recipients` but **not** in any header):

```json
"recipients": [
  {"email": "to_user1@example.com"},
  {"email": "to_user2@example.com"},
  {"email": "copy1@example.org"},
  {"email": "copy2@example.org"},
  {"email": "bcc@example.net"}
],
"headers": {
  "To": " Miguel <to_user1@example.com>, José <to_user2@example.com>",
  "CC": " Helen <copy1@example.org>, Habib <copy2@example.org>"
}
```

Notes:
- Names in `To`/`CC` can be sent as-is, **without MIME-encoding** international characters.
- Substitutions can differ per recipient. To give everyone the same text, use identical substitutions or use `global_substitutions` instead of personal ones.
- Open/click tracking links and the unsubscribe link are **always unique per recipient**.
- **Your account is charged for each email in the `recipients` array.**

### 7.2 Via SMTP API

- **Default (non-strict) behavior:** UniOne does **not** strictly follow RFC. It sends each recipient from `To`/`CC` their own copy, with a single email address in the final `To` header matching the real recipient.
- **Strict mode:** for RFC compliance (i.e. sending without changing the `To:`/`CC:` MIME headers, e.g. to send real CC and BCC), enable it with `strict` set to `true` in the `X-UNIONE` header:
  ```
  X-UNIONE: {"strict":true}
  ```
  Or ask support to enable `{"strict":true}` for all your emails by default.
- In SMTP you are responsible for correct MIME encoding of headers.
- **Billing:** by default you're charged for each address in `To`/`CC`; in strict mode you're charged for each recipient in the SMTP `RCPT TO`.

### 7.3 Restrictions (apply to both Web API and SMTP strict mode)

- You **cannot** specify a `CC` header without a `To` header — this causes a sending error. A `To` header without `CC` **is** allowed.
- The `To` header is limited to **10 addresses**; same limit for `CC`. There can also be a **maximum of 10 blind copies**.
- If the `email` parameter address is **not** listed in `To` or `CC` (i.e. it's used as a blind copy), that address **must be on your own domain already verified in UniOne**. You cannot send blind copies to domains you don't own — enforced to prevent email phishing.

---

## 8. Quick cross-reference

- **Subscribable `email_status` values:** `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam`.
- **Full `status` enum in payloads:** add `accepted` and `sent` to the above.
- **`event_format`:** `json_post` (default), `json_post_gzip`.
- **Webhook `status`:** `active` (default), `disabled` (by user), `stopped` (by system).
- **`single_event`:** `0` (batch, default) / `1` (one event per call, not recommended).
- **`event_name`:** `transactional_email_status`, `transactional_spam_block`.
- **`block_type`:** `one_smtp`, `all_smtp`.
- **`domain_status`:** `blocked`, `unblocked`.
- **Auth:** body `auth` = MD5(body with `auth` value replaced by the API key).
- **SLA:** respond 200 OK in ≤3 s; retries every 10 min for 24 h with `retry_count`; auto-`stopped` after 24 h if ≥10 events all failed.
- **CC/BCC limits:** ≤10 in `To`, ≤10 in `CC`, ≤10 BCC; `CC` requires `To`; BCC-only address must be on a verified own domain.
