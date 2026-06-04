---
title: Unsubscribe Link & Footer
source: https://docs.unione.io/en/unsubscribe
synced: 2026-06-04
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
