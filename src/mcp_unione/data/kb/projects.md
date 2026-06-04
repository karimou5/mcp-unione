---
title: Projects
source: https://docs.unione.io/en/projects
synced: 2026-06-04
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
