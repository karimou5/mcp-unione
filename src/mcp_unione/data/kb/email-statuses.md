---
title: Email Statuses
source: https://docs.unione.io/en/email-statuses
synced: 2026-06-04
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
