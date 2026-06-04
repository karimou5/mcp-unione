---
title: Extended Delivery Status Codes
source: https://docs.unione.io/en/email-statuses
synced: 2026-06-04
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
