---
title: Suppression Lists
source: https://docs.unione.io/en/suppression-list
synced: 2026-06-04
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
