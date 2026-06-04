---
title: Sandbox Domain
source: https://docs.unione.io/en/sandbox
synced: 2026-06-04
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
