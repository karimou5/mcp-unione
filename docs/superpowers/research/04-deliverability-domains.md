# UniOne — Deliverability, Domain Authentication & Sending Infrastructure

> Exhaustive reference compiled from the official UniOne documentation. All DNS record names,
> types, and values are reproduced **verbatim** from the source pages. Where the docs use
> `example.com` / `example.org` as placeholders, those are kept as-is — substitute your own
> domain.
>
> Source pages:
> - https://docs.unione.io/en/dns-setup — *Email Authentication: Setting Up DNS Records*
> - https://docs.unione.io/en/sandbox-domain — *Sandbox Domain for Email Testing*
> - https://docs.unione.io/en/dedicated-ip — *Dedicated IP*
> - https://docs.unione.io/en/tracking-domains — *Tracking Domains*
> - https://docs.unione.io/en/ip-access — *IP Access — Secure Account Access by IP Address*
> - https://docs.unione.io/en/web-api-ref — *Web API reference* (for `domain/*` methods, `track_links`, `track_read`)

---

## Table of Contents

1. [DNS Setup & Domain Authentication](#1-dns-setup--domain-authentication)
2. [The Domain API methods (get-dns-records / validate-verification-record / validate-dkim / list)](#2-the-domain-api-methods)
3. [Sandbox Domain (test sending)](#3-sandbox-domain-test-sending)
4. [Dedicated IP & Warmup](#4-dedicated-ip--warmup)
5. [Tracking Domains (click/open tracking)](#5-tracking-domains-clickopen-tracking)
6. [IP Access Control](#6-ip-access-control)
7. [Cross-cutting notes for the MCP server](#7-cross-cutting-notes-for-the-mcp-server)

---

## 1. DNS Setup & Domain Authentication

In UniOne, **setting up DNS records for email authentication of the sender's domain is
mandatory for getting started.** Email authentication helps mailbox providers distinguish
legitimate mail from spam/phishing, which reduces the chance of landing in the spam folder.

### 1.1 Why each protocol matters

| Protocol | Purpose (verbatim summary) |
|----------|----------------------------|
| **SPF** | A protocol that determines which servers are authorized to send emails on behalf of your domain. The recipient's mail server checks whether the IP of the sending server matches the list in the SPF record. If it does not match, the email may be marked as spam or even rejected. |
| **DKIM** | An authentication method that uses a cryptographic signature to confirm the authenticity of the email. The email is automatically signed with your domain's private key; the recipient verifies it with the public key stored in your domain's DNS. If the signature matches, the email is considered authentic. |
| **DMARC** | A policy that lets the domain owner define how emails that fail SPF and DKIM checks should be handled. It also provides reports on how such emails are processed. |

### 1.2 Adding a domain in the UniOne UI

1. Go to **Settings → Sending domains** and add a new domain by clicking the **plus button**
   next to the page title.
2. A window opens where you enter:
   - your **sending domain name**, and
   - a **third-level domain** that will be used to track email reads and clicks on links
     (for the domain `example.com`, you can specify `send.example.com` or `link.example.com`).
3. Click **Save**.
4. After adding the domain, you'll see **several DNS records** to register in the DNS zone of
   your domain. You can re-view these anytime by clicking the **settings (gear) icon** next to
   the domain in the list.

### 1.3 The exact DNS records UniOne requires

For each record you must specify its **name**, **record type**, and **value**. The example below
uses GoDaddy as the registrar, but any registrar interface is similar.

> **Placeholders:** `@` = the root/apex of your domain (some providers don't accept `@` —
> specify the full domain name instead). `example.com` = your domain. The DKIM `p=...` and the
> verification hash are generated per-domain and retrieved from UniOne (UI or
> `domain/get-dns-records` API).

#### a) SPF record

- **Name:** `@`
- **Type:** `TXT`
- **Value:** `v=spf1 include:spf.unione.io ~all`

> **Merging with an existing SPF record:** A domain may have **only one** `v=spf1` TXT record.
> If you already have one, combine it into a single line by adding the `include:spf.unione.io`
> mechanism. Example given in the docs: if you already have
> `v=spf1 include:godaddy.com ~all` and you're adding `spf.unione.io`, the resulting value is:
>
> ```
> v=spf1 include:godaddy.com include:spf.unione.io ~all
> ```

#### b) DKIM record

- **Name (selector):** `us._domainkey`  ← the DKIM **selector is `us`**
- **Type:** `TXT`
- **Value:** the long string obtained from UniOne, which looks like:
  ```
  v=DKIM1; k=rsa; p=xxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

> **API note:** `domain/get-dns-records` returns only the **key part** of the DKIM value
> (the `p=...` payload). You must **prepend `k=rsa, p=`** (and, per the published record format
> above, `v=DKIM1;`) yourself before publishing. See §2.

#### c) Verification (ownership) record

To prove the domain belongs to you and that you may send from any address on it, add the
**verification record**:

- **Name:** `@`
- **Type:** `TXT`
- **Value:** the verification string supplied by UniOne, added **"as is"**. From the API it
  looks like:
  ```
  unione-validate-hash=483bb362ebdbeedd755cfb1d4d661
  ```

> Only domains whose verification record is in the **`confirmed`** status are allowed as sender
> domains (see `domain/list` schema in §2).

#### d) DMARC record

DMARC protects your recipients from unauthorized email pretending to come from your domain when
SPF/DKIM checks fail. Two supported ways:

**Option 1 — Publish your own DMARC TXT record.** Example value:

```
v=DMARC1; p=quarantine; rua=mailto:your@email.com
```

The `p` tag prescribes the action:
- `p=none` — do not take action (use temporarily while reconfiguring your system)
- `p=quarantine` — mark an offending email as spam
- `p=reject` — reject an email

If you already have a DMARC record, you can leave it as is.

**Option 2 — Delegate DMARC management to UniOne via CNAME.** If you don't have a DMARC record,
create:

- **Name:** `_dmarc`
- **Type:** `CNAME`
- **Value:** `example.com.dmarc.unione.io.`  *(note the trailing dot; substitute your domain)*

This delegates DMARC management to UniOne.

#### e) NS records (for the link-tracking subdomain)

The **last records, of type `NS`**, are required to set up the **link-tracking domain** (the
third-level domain you specified when adding the domain, e.g. `send.example.com`). These
delegate the tracking subdomain to UniOne's nameservers so UniOne can serve the tracking CNAME/
redirect endpoints.

> **Caveat:** Some hostings don't allow you to enter `NS`-type records — in that case you must
> contact your hosting's tech support. (See §5 for the alternative CNAME-based tracking-domain
> flow used by the standalone **Tracking domains** feature.)

### 1.4 Propagation & status check

- After adding all records, the DNS zone takes time to update — **usually from 30 minutes to
  several hours.**
- On **Settings → Sending domains**, click **Check** in the domain's row to see the current
  setup status.
- **Green check marks** appear when the process is complete.

### 1.5 Summary table of required records

| Record | Name / Selector | Type | Value (verbatim, placeholders) | Notes |
|--------|-----------------|------|--------------------------------|-------|
| SPF | `@` | `TXT` | `v=spf1 include:spf.unione.io ~all` | Merge into any existing `v=spf1` record |
| DKIM | `us._domainkey` | `TXT` | `v=DKIM1; k=rsa; p=xxxxxxxxxxxxxxxxxxxxxxxxxxx` | Selector is `us`; key supplied per-domain |
| Verification | `@` | `TXT` | `unione-validate-hash=<hash>` | Proves ownership; must reach `confirmed` |
| DMARC (own) | `_dmarc` | `TXT` | `v=DMARC1; p=quarantine; rua=mailto:your@email.com` | Optional if one already exists |
| DMARC (delegated) | `_dmarc` | `CNAME` | `example.com.dmarc.unione.io.` | Alternative to own TXT record |
| Tracking | tracking subdomain (e.g. `send.example.com`) | `NS` | UniOne nameservers (shown in UI) | Delegates the tracking subdomain |

---

## 2. The Domain API methods

All three methods are `POST` to the transactional API base
`https://api.unione.io/en/transactional/api/v1/...`, authenticated with the `X-API-KEY` header,
`Content-Type: application/json`. Each takes the same request body: `{ "domain": "example.com" }`.

These methods are the programmatic equivalent of the UI flow in §1: fetch the records to publish,
then ask UniOne to (re)validate them after you've published them in your DNS.

### 2.1 `domain/get-dns-records`

**Endpoint:** `POST .../domain/get-dns-records.json`
**Body:**
```json
{ "domain": "example.com" }
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `domain` | string (Required) | Domain to get DNS records for. |

**200 Response (example):**
```json
{
  "status": "success",
  "domain": "example.com",
  "verification-record": "unione-validate-hash=483bb362ebdbeedd755cfb1d4d661",
  "dkim": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDo7"
}
```

**Response schema (HTTP 200 — "Domain DNS info returned successfully"):**

| Name | Type | Description |
|------|------|-------------|
| `status` | string (Required) | `"success"` string. |
| `domain` | string (Required) | Domain to get DNS records for. |
| `verification-record` | string (Required) | Record to be added **"as is"** to verify ownership of this domain. |
| `dkim` | string (Required) | DKIM signature for the domain. **This property contains only the key part** — you must prepend it with the `"k=rsa, p="` part for the record to be valid (see example). |

**Error response (HTTP default):** `{ status: "error", message: <string>, code: <integer> }`.

> So `get-dns-records` returns exactly two of the values you must publish: the **verification
> TXT value** and the **DKIM key**. SPF (`v=spf1 include:spf.unione.io ~all`) and DMARC
> (`example.com.dmarc.unione.io.`) values are fixed/derivable and documented in §1, not returned
> by this method.

### 2.2 `domain/validate-verification-record`

**Endpoint:** `POST .../domain/validate-verification-record.json`
**Body:** `{ "domain": "example.com" }`

**Response schema:**
- **HTTP 200 — "Verification record is valid":** `{ status: "success", message: <Debug message> }`
- **HTTP default — "Error occured or record is invalid":** `{ status: "error", message: <string>, code: <integer> }`

> Call this **after** publishing the verification TXT record (the `@`/TXT `unione-validate-hash=...`
> value). On success, the domain's verification status moves toward `confirmed`, making it
> eligible as a sender domain.

### 2.3 `domain/validate-dkim`

**Endpoint:** `POST .../domain/validate-dkim.json`
**Body:** `{ "domain": "example.com" }`

**Response schema:**
- **HTTP 200 — "DKIM record validation has started successfully":** `{ status: "success", message: <Debug message> }`
- **HTTP default — "Error occured or record is invalid":** `{ status: "error", message: <string>, code: <integer> }`

> Note the wording: a 200 means validation **has started** (asynchronous). Call this after
> publishing the `us._domainkey` TXT record. On completion the DKIM status becomes `active`.

### 2.4 `domain/list` (status of all domains)

**Endpoint:** `POST .../domain/list.json`
**Body:**
```json
{ "domain": "example.com", "limit": 50, "offset": 0 }
```

**Response schema (HTTP 200):**

| Name | Type | Description |
|------|------|-------------|
| `status` | string (Required) | `"success"` string. |
| `domains` | array (Required) | Array of objects describing domains. |
| `» domain` | string (Required) | Domain name. |
| `» verification-record` | object (Required) | Object describing verification record value and status. |
| `»» value` | string (Optional) | Record to be added "as is" to verify ownership of this domain. |
| `»» status` | string (Optional) | **Only domains with `confirmed` verification record are allowed as sender domains.** |
| `» dkim` | object (Required) | Object describing DKIM record value and status. |
| `»» key` | string (Optional) | DKIM signature for the domain (key part only; prepend `k=rsa, p=` — see `domain/get-dns-records`). |
| `»» status` | string (Optional) | **Only domains with `active` DKIM record are allowed as sender domains.** |

### 2.5 How verification works end-to-end (UI ↔ API)

1. **Register** the domain (UI plus button, or it is created by the API workflow).
2. **Fetch records to publish** — `domain/get-dns-records` returns the `verification-record`
   value and the `dkim` key. SPF and DMARC values are the fixed strings from §1.
3. **Publish** all records (SPF TXT, `us._domainkey` DKIM TXT, `@` verification TXT, DMARC,
   tracking NS) in your DNS zone.
4. **Wait for propagation** (30 min – several hours).
5. **Validate** — call `domain/validate-verification-record` and `domain/validate-dkim`
   (or click **Check** in the UI).
6. **Eligibility** — a domain is usable as a **sender domain** only when its
   verification status is `confirmed` **and** its DKIM status is `active`
   (per the `domain/list` schema). Track both via `domain/list`.

---

## 3. Sandbox Domain (test sending)

### 3.1 What it is

A **sandbox domain** is a **temporary, already-verified** domain you obtain immediately after
signing up with UniOne. You can use it as a **sending domain to test your email integration**
while you set up your own domain.

**Important constraint:** you can **only send emails to confirmed addresses you add manually.**

The sandbox domain name has the form `@sandbox-xxxxxxx.unionemailer.com` (a unique
`sandbox-xxxxxxx` value is assigned to your account; e.g. `https://sandbox-xxxxxxx.unionemailer.com`).

### 3.2 Benefits

- **Instant onboarding:** start sending test emails right after signup, without verifying your
  primary domain.
- **Ideal for developers:** test your integrations, templates and automation logic.
- **Security and control:** sending is allowed to **confirmed addresses only**.

### 3.3 How to obtain a sandbox domain

1. Open the **Sending domains** page in your account.
2. Click **Get a test domain**.
3. A new domain is created automatically and is **instantly available for sending** — now you
   can use **any email address ending with `@sandbox-xxxxxxx.unionemailer.com`** (using the
   sandbox name assigned to you) as the **"From"** address when sending.
4. The new domain appears in your domains list with a **`sandbox` tag**.

**Lifetime:** the sandbox domain is **valid for 31 days**. After that it is **automatically
deleted**, but you can create a new one if needed.

### 3.4 How to add allowed recipient ("To") addresses

1. Press **Settings** in your domains list, or open **Account → General → Confirmed emails**.
2. Your **account email address** is added and available for tests as a **"To"** address by
   default (even though it isn't shown on the "Confirmed emails" page).
3. To add another address:
   - Press **Add**
   - Enter an email address
   - **Verify** the address by following a link in the verification email
   - After verification, the address is available as a **"To"** address for test emails.

**Limit:** a maximum of **10 addresses** is allowed, including your primary account email.

### 3.5 FAQ

**Q: Can I use a sandbox domain for a regular campaign?**
No. Sandbox domains are created **exclusively for testing** and cannot be used for marketing or
transactional mailings.

**Q: Do you charge for emails sent from sandbox domains?**
Yes — these emails are **charged according to your current plan** (also available on the **Free**
plan) and are **limited to 100 emails per day.**

### 3.6 Relevance to the MCP's safe-send mode

The sandbox domain is the natural backbone of a **safe-send / test-send mode** for the MCP:

- **From:** must be `something@sandbox-xxxxxxx.unionemailer.com` (the account's assigned sandbox
  domain — already verified, no DNS work needed).
- **To:** must be one of the **confirmed addresses** (max 10), otherwise the send is rejected by
  UniOne. The account owner's email is implicitly confirmed.
- **Guardrails baked in by UniOne:** sends are capped at **100/day**, the domain self-destructs
  after **31 days**, and sandbox domains are blocked from real campaigns — so a "test mode" that
  forces the sandbox From/To pair cannot accidentally blast real recipients.
- Emails are still **charged** (works on Free plan), so test sends are not free of accounting.

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

## 5. Tracking Domains (click/open tracking)

### 5.1 What it does

To register subscribers' **clicks**, all links in your emails are **replaced with links to a
dedicated link-tracking domain.** When a link is clicked, the click is registered and the reader
is redirected to the original target page. UniOne lets you use **your own domains** for link
tracking, which **increases credibility** because no unfamiliar domain names show up in the
email.

> This standalone **Tracking domains** feature complements the tracking subdomain configured
> during sending-domain setup (§1.3e, the `NS` records). Here the setup is via CNAME-style DNS
> records shown in the UI.

### 5.2 How to add your own tracking domain (UI flow)

1. Go to **Settings → Tracking domains** and click the **plus icon** next to the page title.
2. Enter the **domain name** to use for link tracking. UniOne recommends a **third-level domain**,
   preferably a **subdomain of your brand's primary domain** — for `example.com`, names like
   `send.example.com` or `link.example.com`. If you use **projects**, you can also assign
   projects to this domain. Click **Save**.
3. Status becomes **"Awaiting DNS setup."** Click the **gear icon** to view and copy the
   required **DNS records**, then add them in your registrar's control panel.
4. Wait for propagation and update in UniOne's system — **a few minutes to a couple of hours**,
   depending on your provider. If all is well, status changes to **"Setup in progress."**
5. Within the **next 48 hours**, UniOne specialists perform the required system setup; status
   changes to **"Ready."**
6. You may then **activate** the domain and, if needed, set it as **default** via the **star
   icon**. With multiple tracking domains, specify the **`custom_backend_id`** value in the
   `email/send` API call to use a particular one.
7. If status changes to **"Error,"** contact support.
8. To **delete** a tracking domain, click the **cross-out icon** on the right. If it was the
   default, a **system domain** is used instead.

### 5.3 `track_links` and `track_read` (email/send parameters)

Both are integer flags inside the `message` object of `email/send` (and default to **on**):

| Parameter | Type | Description (verbatim) |
|-----------|------|------------------------|
| `track_links` | integer (Optional) | `1` = **click tracking is on (default)**, `0` = click tracking is off. **To use `track_links = 0`, you need to ask support to enable this feature.** |
| `track_read` | integer (Optional) | `1` = **read (open) tracking is on (default)**, `0` = read tracking is off. **To use `track_read = 0`, you need to ask support to enable this feature.** |

Example fragment of an `email/send` request body:
```json
{
  "message": {
    "track_links": 0,
    "track_read": 0
  }
}
```

> **Key takeaway:** click tracking (`track_links`) is what rewrites links to the tracking domain;
> read tracking (`track_read`) embeds the open-tracking pixel. Both default to `1`. Setting either
> to `0` requires support to enable the capability on your account.

---

## 6. IP Access Control

### 6.1 What it is

The **IP Access** feature protects your account and API integrations from unauthorized access.
Even if an attacker obtains your **login credentials or API key**, they can't use them because
their IP address is **not whitelisted**.

### 6.2 How it works

You explicitly specify which IP addresses or subnets are allowed to:

- **log in** to the UniOne account;
- **send API requests** to the service.

**All other connections are blocked** by the security system. This ensures that even if your keys
are compromised, only **trusted servers or company employees** have access.

### 6.3 Where to find it

In your personal account: **Account → Security → IP Access.**
To enable filtering, **add one or more IP addresses or ranges** from which access is allowed.

### 6.4 Usage tips

- If you send API requests through a server with a **fixed IP**, specify that address in the
  list.
- If several employees work from the **same office**, add the **IP range** for your office
  network.
- For **temporary access** (e.g., a contractor), add their IP and remove it after the job is
  done.

> **MCP implication:** if the deploying account enables IP Access, the host running the MCP
> server must have its (static/egress) IP whitelisted, or all `email/send` (and other) API calls
> will be blocked regardless of a valid `X-API-KEY`.

---

## 7. Cross-cutting notes for the MCP server

- **Sender-domain eligibility gate:** a domain can be used as a `from_email` sender only when its
  **verification record status is `confirmed`** AND its **DKIM status is `active`** (from the
  `domain/list` schema). The MCP can pre-flight this with `domain/list` before attempting a send.
- **Programmatic domain onboarding loop:** `domain/get-dns-records` → publish → poll
  `domain/validate-verification-record` + `domain/validate-dkim` → confirm via `domain/list`.
  Remember `validate-dkim`'s 200 means validation **started** (async), so poll `domain/list`
  for the final `active` status.
- **DKIM value assembly:** the API gives only the key payload; prepend `v=DKIM1; k=rsa; p=`
  (record name `us._domainkey`, type `TXT`) before publishing.
- **Fixed values you can hardcode:** SPF `v=spf1 include:spf.unione.io ~all` (TXT @), DMARC
  delegation CNAME `_dmarc → <domain>.dmarc.unione.io.`.
- **Safe / test-send mode:** force `from_email` to the assigned
  `@sandbox-xxxxxxx.unionemailer.com` and restrict `to` to the account's confirmed addresses
  (≤10). This is bounded by UniOne (100/day, blocked from real campaigns, 31-day TTL).
- **Tracking toggles:** `track_links` and `track_read` default to `1`; turning either off needs
  support to enable the feature first — the MCP should not assume `0` will be honored without
  prior account configuration.
- **Dedicated-IP routing:** to target a specific dedicated-IP backend or custom tracking domain
  on a send, pass `custom_backend_id` (value from the **Backend ID** column in the UI).
- **IP Access:** if enabled on the account, the MCP host's outbound IP must be whitelisted or all
  API calls are rejected (independent of the API key).
- **Endpoint base:** all referenced API methods are `POST` to
  `https://api.unione.io/en/transactional/api/v1/<method>.json` with header `X-API-KEY`.
