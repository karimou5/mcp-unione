---
title: SDKs & Integrations
source: https://docs.unione.io/en/integrations
synced: 2026-06-04
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
