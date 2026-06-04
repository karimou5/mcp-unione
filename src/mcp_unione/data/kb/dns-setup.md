---
title: DNS Setup & Domain Authentication
source: https://docs.unione.io/en/dns-settings
synced: 2026-06-04
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
