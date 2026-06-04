---
title: Dedicated IP & Warmup
source: https://docs.unione.io/en/dedicated-ip
synced: 2026-06-04
---

## 4. Dedicated IP & Warmup

### 4.1 What it is / when needed

Dedicated IP addresses let you build your **own reputation scores**, **independent of other
clients** who use UniOne's common pool of IPs. This gives substantial deliverability benefits,
but requires time to implement because **new IPs must be "warmed up"** before full-scale usage to
minimize the risk of blocks/spam. Mailbox providers are suspicious of large volumes from new IPs
or domains, so the per-IP volume must be increased gradually — this procedure is the **"IP
warmup."**

Use dedicated IPs when you have **high, steady sending volume** and want reputation isolation.

### 4.2 Sizing — how many IPs you need

- UniOne **guarantees no less than 70,000 messages/hour** from each **fully warmed-up** IP
  (actual range ~70K–100K depending on overall load and target-domain distribution).
- Quick estimate formula:
  ```
  number_of_IPs = emails_per_day / 85000   (rounded upwards)
  ```
- Worked example: to send ~10 million emails/month = 333,000/day →
  `333000 / 85000 = 3.9` → **4 dedicated IPs.**
- Based on campaign content, UniOne specialists may advise ordering one or more **extra IPs** to
  mitigate delivery issues; their anti-spam service monitors deliverability and advises on the
  needed count.
- If you need **separate IPs for different domains**, create **separate projects** for each
  domain.

### 4.3 Initial setup (UI flow)

1. Calculate the number of IPs needed (formula above) and prepare your list of sending domains.
2. Open **Settings → Dedicated IPs** and click the **plus icon**.
3. Enter a **third-level domain name** that serves as the **IP pool name and tracking domain**
   (for `example.com`, something like `send.example.org`). Specify the **number of IPs** and
   click **Save**.
4. **Billing on save:** the account is charged **$20 per dedicated IP** (one-time setup fee)
   **plus prorated IP rent** per the formula:
   ```
   $40 / 30 * (days left in the current accounting period)
   ```
   Thereafter the **monthly service fee** for the IPs is charged with your regular payment.
   *(For custom contracts, payment follows the contract's terms.)*
5. On **Settings → Dedicated IPs**, click the **gear icon** next to your domain to see the
   **DNS records** to add in your registrar's console. Initial status: **"Awaiting DNS setup."**
6. Once the records are picked up (usually **up to two hours**, depending on provider), status
   changes to **"Domain setup in progress."**
7. Over the **next 48 hours** UniOne specialists perform the setup; status changes to
   **"Active."** The domain is then ready — you can activate it and set it as default.
   - To pick a specific backend when sending, pass the corresponding **`custom_backend_id`** value
     in `email/send`. The values are listed in the **Backend ID** column on the same page.
8. If records don't appear after two days, ask support to investigate. If DNS corrections are
   needed, return to step 5.
9. **Once DNS is in effect, the warm-up starts automatically.** It usually takes **40 days**,
   during which the system **automatically adjusts mailing volumes per-hour and per-domain** to
   minimize spam-block risk and gradually build IP reputation.

### 4.4 Warmup behavior & limit schemes

Consistency, gradualness and regularity are vital. Large campaigns may be **partially delayed**.
Two schemes handle overflow:

- **"Hard limit" (default):** the system allocates as many emails as can be sent from the new
  IPs during a **10-hour period**; any daily emails over this quota are sent via the **common IP
  pool**. Guarantees proper warmup and queue management, but **maximum queueing delay is 10
  hours.**
- **"Soft limit" (on request):** instantly redistributes emails between dedicated and common
  IPs. With small or irregular flows, dedicated IPs may not warm up properly (the common pool
  has much higher throughput). Recommended **only if you can provide a steady flow** of emails
  matching the hourly limits table below.

During warmup, it is **highly recommended to send the required number of emails each day.**
Warmup is automatic; UniOne's anti-spam team monitors delivery rates per IP and advises on quota
adjustments.

### 4.5 Warmup limits table (verbatim)

Approximate **hourly** limits for Gmail and Yahoo Mail (reference only; exact quotas vary by
provider, day of sequence, and many factors):

| Day of warmup | Google (emails/hour) | Yahoo (emails/hour) |
|---------------|----------------------|---------------------|
| 1  | 48 | 48 |
| 2  | 57 | 57 |
| 8  | 225 | 225 |
| 15 | 1100 | 1000 |
| 23 | 12000 | 2500 |
| 28 | 47000 | 5000 |
| 35 | unlimited | 10000 |
| 40 | unlimited | unlimited |

To learn your **current exact quotas**, contact UniOne tech support. When warmup is over
(typically **40 days**), **all limits are removed** and the IPs are used for all your mailings.

---
