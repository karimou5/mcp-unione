---
title: Getting Started with UniOne
source: https://docs.unione.io/en/getting-started
synced: 2026-06-04
---

## 1. Getting started

### Account & domain setup flow

The onboarding flow is:

1. **Add your sender domain** by clicking the **[+]** button on **Settings / Sending domains**.
2. **Add the DNS records** displayed (in the docs view, press the *setup* icon to see the
   required records) to the DNS control panel of your domain's registrar. After ~10–15 minutes,
   click the **Verify** link next to the domain on **Settings / Sending domains**. Green
   checkmarks mean the domain is set up correctly. Record propagation usually takes no more than
   half an hour, but in rare cases up to **48 hours**. The domain is ready for sending when all
   checkmarks show up.
3. **Send the first email to your own domain** using **SMTP** or **Web API**. A new account is on
   the **"Free"** plan by default, which lets you send up to **100 emails per day** to any domain
   you've added and verified.
4. **Change your subscription plan** to a paid one to send to all domains (not only your own).
   You can start with the **"StartUp 6K"** plan, which is free for **4 months after registration**.

Once domains are verified and a plan is selected, setup is complete. The docs then point users to
Web API capabilities (real-time event notifications, templates, suppression/unsubscribe
management), the knowledge base, and the integration libraries.

### Where to get the API key

The account API key is found on the **API** page of the user info area:

> **`https://cp.unione.io/en/user/info/api`**  — "API key of your account".

- The API key is passed to the API via the **`X-API-KEY`** HTTP header (this auth method was
  added in v.1.14, Jan 4 2021). Older `username`/`password` style auth has been removed — the user
  is authorized **only by API key** (v.1.5, Mar 3 2020).
- For **SMTP**, the `password` is the **API key of your account** (`cp.unione.io/en/user/info/api`)
  or a **`project_api_key`** (obtained via `project/create`, `project/list`, or on the
  **Projects** page at `cp.unione.io/en/user/project`).
- The **Tech support / Support** shared-access role can view Settings in read-only mode but the
  **API key is NOT displayed** to that role.
- **IP Access** (whitelisting) can protect the account and API integrations: even if an attacker
  obtains login credentials or the API key, requests from non-whitelisted IPs are blocked.

API base URL (for reference): `https://api.unione.io/en/transactional/api/v1/...`

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
