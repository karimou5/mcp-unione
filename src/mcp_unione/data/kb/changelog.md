---
title: API Changelog
source: https://docs.unione.io/en/api-changelog
synced: 2026-06-04
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
