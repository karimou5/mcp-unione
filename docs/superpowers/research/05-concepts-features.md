# UniOne — General Concepts & Account Features (Exhaustive Reference)

> Source: official UniOne documentation (`docs.unione.io/en/*`) and the Web API reference
> (`docs.unione.io/en/web-api-ref`). All enum/parameter values are quoted **verbatim**
> from the docs.
>
> Pages covered: get-started, email-validation, suppression-lists, projects,
> unsubscribe-link, unsubscribe-page, shared-access, 2fa, delivery-report,
> non-delivery-report, campaigns-report, performance-report, api-changelog,
> integrations, statistics.

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

## 2. Email validation

UniOne validates a single address via the **`email-validation/single`** API method
(`POST .../email-validation/single.json`). It checks an address for correct syntax and
functionality, to discard addresses that are invalid or that could harm sender reputation.

### Behavior / limitations

- A maximum of **two simultaneous requests** are allowed; exceeding it returns an error.
- The check must be fast: if a recipient's mail server does not respond within **5 seconds**, the
  validation result may be undefined (`unknown`).

### Request

```json
{ "email": "email@example.com" }
```

| Field   | Type             | Required | Description                |
|---------|------------------|----------|----------------------------|
| `email` | string(email)    | Required | Email address to be checked |

### Response example

```json
{
  "status": "success",
  "email": "user@example.com",
  "result": "suspicious",
  "cause": "disposable",
  "validity": 10,
  "local_part": "user",
  "domain": "example.com",
  "mx_found": true,
  "mx_record": 10,
  "did_you_mean": "user@example.com",
  "processed_at": "2023-01-01 22:14:59"
}
```

### Response fields (HTTP 200)

| Field          | Type                  | Description |
|----------------|-----------------------|-------------|
| `status`       | string (Required)     | "success" string |
| `email`        | string(email)         | Email address that was checked |
| `result`       | string (Required)     | Validation result — see status enum below |
| `cause`        | string (Required)     | Reason the result was set — see cause enum below |
| `validity`     | integer (Required)    | Validity score, **from 0 to 100** (0 = invalid, 100 = valid) |
| `local_part`   | string (Required)     | Local part (everything preceding the `@` sign) |
| `domain`       | string (Required)     | Domain-name part |
| `mx_found`     | boolean (Required)    | `true` if the address's domain has an MX record, `false` if not |
| `mx_record`    | string (Required)     | Preferred MX record for the domain |
| `did_you_mean` | string(email)         | For addresses likely to have a typo (`cause=possible_typo`), a suggested variant with the typo fixed |
| `processed_at` | string(utc-date-time) | Check date/time, `YYYY-MM-DD hh:mm:ss` UTC |

On error (HTTP default): `status` = "error", `message` (human-readable English), `code` (API error code).

### `result` — ALL possible validation statuses (verbatim)

| `result`      | Meaning |
|---------------|---------|
| `valid`       | The address is valid |
| `invalid`     | The address is invalid |
| `suspicious`  | The address looks suspicious |
| `unknown`     | Could not perform validation — the domain's mail server did not respond within the time limit |

### `cause` — ALL possible causes for a validation result (verbatim)

| `cause`                  | Meaning |
|--------------------------|---------|
| `no_mx_record`           | No MX record found for the target domain |
| `syntax_error`           | The address syntax is invalid |
| `possible_typo`          | The address is likely to have a typo (see `did_you_mean`) |
| `mailbox_not_found`      | The address does not exist |
| `global_suppression`     | The address has been marked unreachable due to multiple previous delivery errors |
| `disposable`             | A disposable one-time email address (usually valid for only a few minutes) |
| `role`                   | Not likely to belong to an actual person, but rather to a business staff role (e.g. `info@`, `support@`) |
| `abuse`                  | Known to be a source of a large number of complaints, sometimes issued automatically |
| `spamtrap`               | A spam trap — published openly but never used for actual email; sending here has a huge negative reputation impact |
| `smtp_connection_failed` | The domain's SMTP server does not respond; the address may contain a typo |

> Note: there is **no separate `accept_all` / catch-all status** exposed by UniOne's
> `email-validation/single`. The four `result` values are the complete set (`valid`, `invalid`,
> `suspicious`, `unknown`), and "accept-all"-style situations surface through `result=suspicious`
> /`unknown` with the relevant `cause`. Concepts like `disposable` and `role` are returned as
> **`cause`** values, not as separate `result` statuses.

---

## 3. Suppression lists

Suppression lists (lists of unreachable addresses) protect sender reputation. UniOne
automatically filters out any addresses found in these lists. An address may be suppressed because
it is syntactically invalid, the owner unsubscribed or complained, or the receiving server is
known to block certain emails.

### How an address becomes suppressed — three sources

| Source (concept) | Description |
|------------------|-------------|
| **The system**   | An address is considered unreachable after many failed delivery attempts, or because it is registered as a spam trap |
| **The owner**    | A subscriber cancels their subscription or issues a complaint |
| **The client**   | You explicitly add an address to a list with an appropriate status (unsubscribed, complainer, etc.) via `suppression/set` |

The source is returned in the **`source`** field of `suppression/get`; the related reason is
returned in **`cause`**.

### Two types of suppression lists (global vs local/project)

| List       | Scope | Possible sources |
|------------|-------|------------------|
| **Global suppression list** | Addresses considered unreachable **for all users** | Only the **system** and the **address owner** — **never a client** |
| **Local suppression list**  | Addresses suppressed **for your mailings only**, based on your previous sending attempts or the owner's actions | system / owner / client |

The global list is a major benefit: it suppresses mailings to addresses already known to be
unreachable, protecting deliverability and sender reputation.

### `cause` — COMPLETE list of suppression cause values (verbatim)

Used in `suppression/set` (param), `suppression/get` and `suppression/list` (response/filter):

| `cause`                 | Meaning |
|-------------------------|---------|
| `unsubscribed`          | Email is unsubscribed |
| `temporary_unavailable` | The address is unavailable; over the next **three days** sending returns an error. Causes include: a previous email rejected by the recipient's server for spam; the recipient's mailbox is full or unused; the recipient's domain does not accept mail; the sending server was rejected due to blacklisting |
| `permanent_unavailable` | The address is permanently unavailable due to **multiple hard bounces** |
| `complained`            | The recipient reported spam in previous emails |
| `blocked`               | Sending to the email is prohibited by the **administration of UniOne** *(appears in `suppression/get`/`suppression/list`; the docs note "We may add some new causes in the future.")* |

> `suppression/set` accepts only `unsubscribed`, `temporary_unavailable`, `permanent_unavailable`,
> `complained` as `cause`. The `blocked` cause is system/admin-set and appears only in
> read responses.

### `source` — COMPLETE list of suppression source values (verbatim)

Returned by `suppression/get` / `suppression/list` (and usable as a filter in `suppression/list`):

| `source`     | Meaning |
|--------------|---------|
| `user`       | Suppressed by the user via `suppression/set` |
| `system`     | Sending prohibited by the system, e.g. due to multiple hard bounces |
| `subscriber` | The recipient reported spam or unsubscribed in previous emails |

> The conceptual doc describes the three *origins* as **system / owner / client**; the API maps
> these to the verbatim `source` enum **`system` / `subscriber` / `user`** respectively. There is
> no separate `admin` source value — admin/UniOne-side blocks surface as `cause=blocked` (and
> typically `source=system`).

### `suppression/get` — read suppression details for one address

Request:

```json
{ "email": "email@example.com", "all_projects": false }
```

| Param          | Type    | Required | Description |
|----------------|---------|----------|-------------|
| `email`        | string(email) | Required | Email to get suppression details for |
| `all_projects` | boolean | Optional | If projects functionality is enabled, pass `all_projects=true` to search across **all projects'** data |

Response contains a `suppressions` array of objects with: `project_id`, `cause`, `source`,
`is_deletable` (whether `suppression/delete` can remove it), and `created`
(`YYYY-MM-DD hh:mm:ss` UTC). The array can be empty if the address is not suppressed.

### `suppression/list` — paginated list

Optional filters/params: `cause`, `source`, `start_time` (`YYYY-MM-DD hh:mm:ss` — from
start_time to present; ignored if `cursor` is set), `cursor` (pagination — empty for the first
chunk, then the value returned in the previous response), and `limit` (records per page,
default **50**). Each item has `email`, `cause`, `source`, `is_deletable`, `created`.

### `suppression/set` — add an address (client/user source)

| Param     | Type    | Required | Description |
|-----------|---------|----------|-------------|
| `email`   | string(email) | Required | Email to add |
| `cause`   | string  | Required | One of `unsubscribed` / `temporary_unavailable` / `permanent_unavailable` / `complained` |
| `created` | string(utc-date-time) | Optional | When suppression was created (UTC) |

### `suppression/delete`

Removes an address (only where `is_deletable=true`).

### Global vs local & how `all_projects` works

- **Local list removal** is unrestricted — you can remove addresses from your local suppression
  list whenever you like.
- **Global list removal** is limited to a **few addresses per day** and may be unavailable for
  certain addresses.
- **`all_projects=true`** (in `suppression/get`, available only when projects functionality is
  enabled) searches suppression data **across all projects** rather than just the current one.
  Because each project is isolated, unsubscribing from one project does **not** affect others.

### Bypassing suppression on send (`email/send` parameters)

Default `email/send` parameters are optimized for marketing email (both global + local lists
applied). To relax this:

| Parameter             | Effect |
|-----------------------|--------|
| `bypass_global=1`     | Ignore the **global** suppression list (regular transactional messages) |
| `bypass_unavailable=1`| Send to addresses marked temporarily/permanently unavailable |
| `bypass_unsubscribed=1`| Send to unsubscribed addresses |
| `bypass_complained=1` | Send to complainers |

Recommended scenarios:
- **Marketing** — defaults (global + local applied).
- **Regular transactional** — `bypass_global=1` (use local list only).
- **High-priority transactional** (password resets, security) — `bypass_global=1` +
  `bypass_unavailable=1` (and optionally `bypass_unsubscribed=1`, `bypass_complained=1`).

### Managing & best practice

Manage via the `suppression/*` Web API methods, or per-address via **Tools / Email search** in the
account. If you implement your own unsubscribe mechanism, UniOne **strongly recommends** also
adding unsubscribed addresses via `suppression/set` with `cause=unsubscribed`.

---

## 4. Projects

Projects **completely isolate** data for different independent domains, suppression lists,
templates, mailing settings, etc.

**Typical scenarios:** white-label / per-client separation; per-department isolation combined with
Shared access; per-country campaigns with dedicated sender domains, dedicated IPs, and custom
settings.

**Key properties:**

- You still manage all projects and pay through your **primary UniOne account**, benefiting from
  a single cost-effective tariff based on combined volume across all projects.
- **Each project has its own API key** (`project_api_key`). API calls made with a project key
  affect only that project's data. Projects are fully independent — unsubscribing from one project
  does not affect subscriptions to others.
- Manage projects via **Settings / Projects** (`cp.unione.io/en/user/project`) or via the
  **`project/*`** API methods. **Disabled by default for security** — contact support to enable
  projects functionality.
- For maximum independence, a sender domain is verified/enabled **separately** for the main
  account and each project. To share verified domains from the main account across projects,
  contact support.
- You can limit users' access to statistics, templates, etc. by listing the projects available to
  them via **Shared access**.

### Project API parameters (`project/create`, `project/update`, `project/list`)

The request wraps a `project` object:

| Parameter (`project.*`)          | Type    | Req. | Description |
|----------------------------------|---------|------|-------------|
| `name`                           | string  | Required | Project name, unique per user account |
| `country`                        | string  | Optional | **ISO-3166 alpha-2** country code. If set, UniOne treats project personal data per country laws (e.g. **GDPR** for European countries) |
| `send_enabled`                   | boolean | Optional | Whether email sending is enabled for this project |
| `custom_unsubscribe_url_enabled` | boolean | Optional | `false` → UniOne adds the default unsubscribe footer to every email sent with this project's API key. `true` → the default footer is **not** appended, and sending with a custom unsubscribe URL (or with none) is permitted. `true` is only available if removing the unsubscribe link is approved for the account by support. If skipped on creation, inherited from the user/account setting |
| `backend_domain_id`              | integer | Optional | Unique domain identifier determining the default **tracking domain or dedicated IP pool**. If absent, a default backend domain is assigned. *(Introduced in the changelog as `backend_id` in v.1.44.)* |
| `unsubscribe_page_id`            | integer | Optional | Unique identifier of the default **unsubscribe page**. If absent, the system default unsubscribe page is used *(added v.1.72)* |

**`project/create` response:** `status` ("success"), `project_id` (ASCII string up to 36 chars),
and `project_api_key` — usable instead of the user API key in **all methods except `project/*`**.

Also configurable via `project/update` and retrievable via `project/list` / `system/info`:
the email counter controls **`email_counter`**, **`email_counter_limit`**, **`email_counter_mode`**
(added v.1.64, Sep 17 2024).

---

## 5. Unsubscribe link

The unsubscribe link should be in **every** email (transactional or mass). Anti-spam systems use
its presence when deciding whether a message is spam; without it, recipients may file a spam
complaint instead of simply unsubscribing. **UniOne appends an unsubscribe block to every email**
by default.

### Default unsubscribe footer

- Contains the original target address (so the reader knows the real recipient even after
  redirects) plus the unsubscribe link, which leads to a neutral unsubscribe page.
- Language of the footer and page is set by the API call's **URI language** (e.g. `/en/`) or by
  the **`global_language`** parameter in the `X-UNIONE` header (for SMTP).
  Supported languages: **be, de, en, es, fr, it, pl, pt, ru, ua** (and **kz** added later — see
  changelog).
- UniOne also adds a **`List-Unsubscribe`** email header for one-click unsubscribing; many email
  clients render an Unsubscribe button from it.
- UniOne tracks all unsubscribed addresses and denies further sending. Check via `suppression/get`
  / `suppression/list` (`cause="unsubscribed"`), or the **Email search** page. Reset via
  `suppression/delete`, the Email Search page, or by re-inviting with `email/subscribe`.

### Substitution variables (custom link placement)

To place the link yourself, insert the unsubscribe URL into the email body. The exact token
depends on the **template engine**:

| Template engine | Substitution token |
|-----------------|--------------------|
| **Simple template engine** | `<a href="{{UnsubscribeUrl}}">Unsubscribe</a>` |
| **Velocity template engine** | `<a href="$UnsubscribeUrl">Unsubscribe</a>` |

When you place the link yourself, you usually also disable the default footer to avoid duplication.

### `skip_unsubscribe` and disabling the footer

Disabling the footer requires **contacting support** (and possibly signing a responsibility
agreement). Two modes:

- **Dynamic disabling** — add the **`skip_unsubscribe`** parameter to the `email/send` request (or
  to the `X-UNIONE` header for SMTP) to remove both the footer **and** the `List-Unsubscribe`
  header for specific emails. *(`skip_unsubscribe` was added in v.1.10, Sep 24 2020.)* Recommended
  as the most flexible option.
- **Forced disabling** — remove the default footer from **all** emails regardless of
  `skip_unsubscribe`. The `List-Unsubscribe` header is still added, but you can replace it with
  your own.

You can set the `List-Unsubscribe` header value via the **`options.unsubscribe_url`** parameter of
`email/send`. Best practice: make the link unsubscribe directly (no confirmation), which Gmail and
others require. If you disable UniOne's link you own the unsubscribe handling — never email
unsubscribed addresses, and call `suppression/set` with `cause="unsubscribed"` for each request.

### Projects & unsubscribe links

`custom_unsubscribe_url_enabled` (set via `project/create` / `project/update`) governs per-project
behavior:

- `custom_unsubscribe_url_enabled=true` → an unsubscribe link is added to **all** emails for that
  project regardless of `skip_unsubscribe`.
- `custom_unsubscribe_url_enabled=false` → no link added when `skip_unsubscribe=1` (added by
  default if the parameter is omitted); requires **dynamic disabling**.
- If unset for a new project → inherited from the global account setting; changeable later via
  `project/update`.

### Custom unsubscribe pages

Lets you build a branded unsubscribe page. Configure at **Settings → Unsubscribe pages**.

- Two built-in defaults: **"system standard"** (more flourish) and **"system simple"**
  (minimalistic).
- Create a custom page via **"+"**. Fields: **Title** (required), **Language** (multiple language
  versions allowed), **Headline / subheader**, **Unsubscribe reason** list (custom reasons
  allowed; hidden if empty), **Footer / background / button color**, and **Favicon / logo /
  image**.
- A custom page is actually **four connected pages**: *Before unsubscribing* (main),
  *Resubscribe*, *After resubscribing*, *After a complaint*.
- Row actions in the list: **Eye** (preview), **Star** (set default), **Pencil** (edit),
  **Cross** (delete — if the page is in use, "system standard" is used instead).
- **Language selection:** the API URL language segment (e.g. `/en/`) sets the page language unless
  overridden by `global_language`.
- **Unsubscribe reasons** can be obtained via **webhooks** or the **`event-dump`** API method.
- Complaints mark the address as "complaining"; no more emails are sent. Such addresses can only
  be reactivated by contacting support or if the user re-subscribes via the link.
- With projects, each project can have its own unsubscribe page; a new project is associated with
  the main account's default unsubscribe page.

---

## 6. Shared access (roles)

UniOne lets you grant collaborators scoped access (designers manage templates, marketers get
statistics, admins manage domain settings). Configure at **Settings – Shared Access** (invite via
the **+** button; specify the member's email and rights; a **Readonly** checkbox makes access
view-only). The invitee receives a confirmation email and can then switch into your account.
Modify with the pencil icon, remove with the cross; temporarily revoke by unchecking all boxes.

### Predefined roles (verbatim)

| Role | Access |
|------|--------|
| **Administrator** | Maximum rights — controls every setting **except** the primary email address and password |
| **Developer**     | Like Administrator, but some settings are read-only (account details, payment settings, tariff) |
| **Marketer**      | Access to all **Tools** and **Statistics** pages — templates, deliverability rates, CSV event download (including email addresses), delivery-problem analysis, address-status management |
| **Tech support** (Support) | Same rights as Marketer, **plus** read-only Settings (the **API key is not displayed**) |
| **Accountant**    | Full access to tariff, balance, payment history; can change the tariff plan; can view statistics but **cannot** download CSV |
| **Designer**      | View and edit templates only |
| **Client**        | Access to **Statistics only**, including the ability to download data |
| **Customized**    | Custom permissions — check exactly the options you want to grant |

Access can also be scoped to specific **projects** (select the allowed projects in the Shared
access menu).

---

## 7. Two-factor authentication (2FA)

2FA protects the account from intruders. After logging in with email + password, the system
prompts for a code from **Google Authenticator** (iOS / Android) on the user's mobile device; the
code changes every **30 seconds**.

- **Enable:** Account → Security (`cp.unione.io/en/settings/security/two-fa-auth`) → **Configure** →
  add the account to Google Authenticator (scan the QR code or enter the digital code) → enter the
  six-digit code → **Enable**. (Device time must be set automatically, or codes may desync.)
- **Login:** email + password, then the six-digit code.
- **Password recovery with 2FA:** enter email → **Recover password** → open Google Authenticator →
  enter the six-digit code → **Recover password** again.
- **Disable:** on the 2FA management page, enter the six-digit code → **Disable**.
- **Lost device:** if you can't access Google Authenticator, contact support.

2FA covers the **web control-panel login** (and password recovery). It does **not** affect API
authentication, which is the API key (`X-API-KEY`).

---

## 8. Statistics & reports

UniOne exposes statistics four ways:

1. **Statistics section** (control panel) — detailed visual charts (delivery / non-delivery /
   campaigns / performance reports).
2. **Dashboard** on the main page — last-week summary, real-time, no filtering.
3. **Event-dump methods** — CSV export of events for a time period.
4. **Webhook API** — real-time per-event notifications.

### Backing data for each report

- **Visual reports** (delivery / non-delivery / performance) are based on UniOne's internally
  processed/indexed event data (the same event stream surfaced by webhooks / event-dump). They lag
  slightly (usually ≤ 1 hour) versus the real-time dashboard.
- **Event-dump (`event-dump/*`)** — CSV export of raw events; data stored up to **45 days** (high-
  volume senders default to **7 days**, extendable on request). Filterable by recipient/sender
  address, **campaign IDs**, etc. (`aggregate` and `dump_fields` params added v.1.61.)
- **Webhook API** — unlimited retention (you store it), most complete raw data, real-time.

### 8a. Delivery report

Delivery events over the **last 32 days** (today included). Pick any period within 32 days; a
1-day period shows an **hourly** breakdown, longer periods a **daily** breakdown (day defined by
**UTC**). Filter by sender email and/or recipient domain (click **Apply** after changing
filters/dates).

Two display modes:
- **All events** — every event is counted (e.g. an email sent, delivered after a third retry, then
  read twice = 1 send + 1 delivery + 3 retries + 2 reads).
- **Unique events** — only events unique per message within a day/hour.

Event groups:

| Group         | Definition |
|---------------|------------|
| **Sent**        | The first send attempt to the recipient's SMTP server (retries not counted; soft bounces go to Failures) |
| **Delivered**   | Recipient's server accepted the message (not a guarantee it reached the inbox) |
| **Opened**      | Read tracked via a 1×1 pixel; requires `track_read = 1` on `email/send` (may be blocked by some clients) |
| **Clicked**     | Clicks on any links except unsubscribe links; requires `track_links = 1` on `email/send` |
| **Unsubscribed**| Only unsubscribes via the UniOne unsubscribe link/block or the UniOne-generated `List-Unsubscribe` header |
| **Complained**  | Addresses whose owners clicked "this is spam" (detected via **FBL** technology) |
| **Bounced**     | Soft bounces (temporary) + hard bounces (permanent); reason breakdown is in the non-delivery report |

Current-day stats may lag (usually ≤ 1 hour). With projects, switch between a single project, the
main account, or **"all projects"** (summary).

### 8b. Non-delivery report

Undeliverable / complaint data over the **last 32 days**. Same period/filter/mode mechanics as the
delivery report (hourly vs daily by UTC; All vs Unique events).

Event groups:

| Group               | Definition |
|---------------------|------------|
| **Retries**           | "Soft bounces" — temporary failures; UniOne retries for **two days** |
| **Unavailable**       | Addresses UniOne deems impossible/prohibited to deliver to (repeated rejections, prior complaints, or permanent block requests). Some statuses resettable via **Email Search** |
| **Non-existent**      | Server says the address does not exist / is inactive — a **hard bounce** |
| **Rejected as spam**  | Server rejected the message as spam — also a **hard bounce** |
| **Other non delivery**| Rejected for other reasons or reason not reliably identified — also a **hard bounce** |

Last week's SMTP error messages (per email) are available on the **Delivery Issues** page.
Project switching ("all projects") supported.

### 8c. Campaigns report

Campaign statistics for emails grouped by **same sender + subject**, or by the same
**`campaign_id`** in API calls. Retained **up to 400 days** (longer than other data). Includes a
**heat map** per campaign.

- Report shows: campaign ID, subject, send date, emails sent/delivered, opens, clicks (broken down
  by each unique link), delivery errors, unsubscribes.
- **Heat map** shows the **absolute** number of clicks (not unique visitors).
- **Disabled by default** for privacy. Enable at **Statistics – Campaigns**, choosing a retention
  period of **45 days** (monthly reports) or **400 days** (annual). A separate option saves a
  **sample letter** per campaign (required for the heat map).
- **`campaign_id`**: a non-negative decimal integer or **UUID up to 128 bits**, in the metadata
  field `campaign_id`. If omitted, the system auto-generates one (grouping emails with the same
  subject + sender sent the same UTC day to 2+ recipients in one request). **Max 1000 saved
  campaigns per day** — for highly personalized sends, pass `campaign_id` explicitly.
- `campaign_id` can also filter `event-dump/create` and statistical charts.
- Pass **`campaign_id=0`** for transactional emails to exclude them from the report. If event
  storage is disabled, campaign stats are not collected.

### 8d. Performance report

Analyzes recipient engagement, keyed to the **email send date** (not the event date). Available
for the past **185 days**; each report selects a period of up to **31 days**.

- For each email with a unique **`message_id`**, each status is counted **once** (e.g. opened +
  two clicks + one unsubscribe = 1 open, 1 click, 1 unsubscribe).
- Displayed as an **area chart** showing both percentages and absolute event numbers.

Three display modes (radio buttons above the graph):

| Mode | Statuses shown |
|------|----------------|
| **Reads / Clicks / Unsubscribes** | Delivered (100% baseline), Reads, Clicks, Unsubscribes — % of unique emails read / with ≥1 click / unsubscribed, relative to total delivered |
| **Clicks to Reads** | Read (100%), Clicks — % of emails with ≥1 click relative to total opened |
| **Deliverability** | Sent (100%), Delivered — % delivered relative to sent |

Access at **Statistics → Performance**.

---

## 9. API changelog (notable versions)

| Date / Version | Notable change(s) |
|----------------|-------------------|
| **Apr 11, 2026 (v.1.85)** | `system/ping` method added — checks API key validity and returns user ID |
| **Aug 04, 2025 (v.1.76)** | New email delivery status **"accepted"** |
| **Mar 27, 2025 (v.1.72)** | New `unsubscribe_page_id` param in `project/create`, `project/update`, `project/list`; SMTP API supports `idempotence_key` |
| **Jan 09, 2025 (v.1.69)** | `email/send` supports `message.idempotence_key` |
| **Oct 11, 2024 (v.1.64)** | `domain/delete` method added (delete domains via API) |
| **Sep 17, 2024 (v.1.64)** | Email counter config: `email_counter`, `email_counter_limit`, `email_counter_mode` via `project/update`; retrievable via `project/list` & `system/info` |
| **May 22, 2024 (v.1.61)** | New `aggregate` and `dump_fields` params for `event-dump/create` |
| **Sep 27, 2023 (v.1.52)** | SMTP strict `To:`/`CC:`/`BCC:` handling (`strict` param); new unsubscribe language **"kz"**; new webhook event **"subscribed"** |
| **May 11, 2023 (v.1.46)** | New `email-validation/single` method; `List-Unsubscribe-Post` header allowed (with footer-removal right) |
| **Mar 1, 2023 (v.1.44)** | New `backend_id` param in `project/create`/`update`/`list`; `custom_backend_id` & `smtp_pool_id` usable without contacting support |
| **Feb 14, 2023 (v.1.44)** | New `message.bypass_global`, `bypass_unavailable`, `bypass_unsubscribed`, `bypass_complained` for `email/send` |
| **Dec 23, 2022 (v.1.41)** | `message.tags` for `email/send`; `tag/list` & `tag/delete` methods; charts filterable by tags & campaign id |
| **Oct 18, 2022 (v.1.38)** | `event-dump/*` CSV export methods; `template_engine:"none"` (with unsubscribe-disable right); `campaign_id` usable as event-dump filter |
| **Jun 24, 2022 (v.1.34)** | `suppression/set` & `suppression/list` added; `References`/`In-Reply-To` headers allowed (with footer-removal right) |
| **Mar 18, 2022 (v.1.31)** | `template_id` in SMTP `X-UNIONE` header; new `country` param in `project/create`/`update`/`list` |
| **Feb 23, 2022 (v.1.30)** | `message.options.send_at`; unsubscribe-footer language via `message.global_language` / `X-UNIONE-Global-Language`; template-engine selection via `X-UNIONE-Template-Engine` |
| **Dec 28, 2021 (v.1.28)** | `suppression/get` & `suppression/delete` added |
| **Jul 5, 2021 (v.1.19)** | Unsubscribe-page languages: be, de, en, es, fr, it, pl, pt, ru, ua |
| **May 31, 2021 (v.1.17)** | New `email/send` `message.options.custom_backend_id` |
| **Mar 17, 2021 (v.1.16)** | API POST size limit raised to **10MB** (HTTP 413 / API code 199 on larger) |
| **Feb 24, 2021 (v.1.15)** | 2-day retry guarantee for `soft_bounced`; `message.options.smtp_pool_id`; "es"/"ua" unsubscribe languages |
| **Jan 4, 2021 (v.1.14)** | New auth: API key in **`X-API-KEY`** header; `List-Unsubscribe`/`List-Subscribe`/`List-Help`/`List-Archive`/`List-Owner` headers (with footer-removal right); substitutions in header values |
| **Dec 7, 2020 (v.1.13)** | `webhook/list`; webhook `status` field (disable/activate without deleting); auto-stop of constantly-failing webhooks |
| **Nov 20, 2020 (v.1.12)** | `system/info`; `project_id` in all-projects methods & webhook data; `project_id` SMTP login; custom `List-Unsubscribe` in SMTP (after approval); `editor_type` in template methods |
| **Oct 16, 2020 (v1.11)** | Updated SMTP API launched |
| **Sep 24, 2020 (v.1.10)** | New `skip_unsubscribe` & `force_send` for `email/send`; `metadata` renamed `global_metadata` (old name kept); `email/subscribe` params renamed to match `email/send` |
| **June 03, 2020 (v.1.7)** | Project API added; AMP improved (`message.body.amp`, `template.body.amp`; `is_amp` ignored); obsolete webhook `login` removed, `project_name` added |
| **March 03, 2020 (v.1.5)** | `username` ignored (auth by API key only); `user_id` added to webhooks; obsolete methods removed: `checked_email`, `set-domain`, `validate`, `getCheckedEmail`, `getSenderDomainList`, `setSenderDomain`, `validateSender` |

---

## 10. Integrations & official SDKs

### Official SDK repositories (`github.com/unione-repo/*`)

| SDK / Library | Repository | Status |
|---------------|------------|--------|
| **Python 3 SDK** | `https://github.com/unione-repo/python3-sdk` | **Beta** (public beta — interfaces may change) |
| **Java SDK**     | `https://github.com/unione-repo/java-sdk` | **Beta** (public beta) |
| **PHP 8+ SDK**   | `https://github.com/unione-repo/php8-sdk` | Stable |
| **PHP 7.x SDK**  | `https://github.com/unione-repo/php7-sdk` | Stable |
| **JavaScript SDK** | `https://github.com/unione-repo/javascript-sdk` | Stable |
| **Ruby gem**     | `https://github.com/unione-repo/unione-ruby` | Stable |
| **C# library (GitHub)** | `https://github.com/unione-repo/unione-csharp` | Stable |
| **C# library (NuGet)**  | `https://www.nuget.org/packages/UniOne.API.Lib` | Stable |
| **PHP library (obsolete)** | `https://github.com/unione-repo/unione-php` | **Obsolete** |

> **Beta note:** the Java and Python 3 SDKs are public beta — interfaces may change (including
> backward-incompatible changes). Test in staging before production. UniOne offers a discount on
> validated bug reports / useful suggestions.

### Integration platforms & other libraries

| Integration | URL |
|-------------|-----|
| **Make.com** (former Integromat) | `https://www.integromat.com/en/integrations/unione` |
| **Zapier** | `https://zapier.com/apps/unione/integrations` |
| **Albato** | `https://albato.com/apps/unione` |
| **Bloomreach / Exponea CDP** | `https://documentation.bloomreach.com/engagement/docs/unione` |
| **Fast Track** | `https://www.fasttrack-solutions.com/en/alliances/unione` |
| **OpenClaw Skill (ClawHub)** | `https://clawhub.ai/unione-repo/unione-api-skill` |
| **Drupal module** | `https://www.drupal.org/project/unione` |
| **Postman collection** | `assets/doc/integrations/UniOne API Methods.postman_collection.json` (downloadable from the docs site) |

For an unlisted service plugin or a library for another language, UniOne directs you to contact
support.

---

## Appendix — quick reference of all verbatim enums

**Validation `result`:** `valid`, `invalid`, `suspicious`, `unknown`

**Validation `cause`:** `no_mx_record`, `syntax_error`, `possible_typo`, `mailbox_not_found`,
`global_suppression`, `disposable`, `role`, `abuse`, `spamtrap`, `smtp_connection_failed`

**Suppression `cause`:** `unsubscribed`, `temporary_unavailable`, `permanent_unavailable`,
`complained`, `blocked`
*(`suppression/set` accepts only the first four)*

**Suppression `source`:** `user`, `system`, `subscriber`

**`email/send` `failed_emails` statuses** (related): `unsubscribed`, `invalid`, `duplicate`,
`temporary_unavailable`, `permanent_unavailable`

**Shared-access roles:** Administrator, Developer, Marketer, Tech support, Accountant, Designer,
Client, Customized

**Project params:** `name`, `country` (ISO-3166 alpha-2), `send_enabled`,
`custom_unsubscribe_url_enabled`, `backend_domain_id` (aka `backend_id`), `unsubscribe_page_id`,
`email_counter` / `email_counter_limit` / `email_counter_mode`

**Unsubscribe substitution tokens:** `{{UnsubscribeUrl}}` (Simple), `$UnsubscribeUrl` (Velocity)

**Unsubscribe / system languages:** be, de, en, es, fr, it, pl, pt, ru, ua, kz
