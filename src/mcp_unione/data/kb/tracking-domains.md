---
title: Tracking Domains
source: https://docs.unione.io/en/tracking-domain
synced: 2026-06-04
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
