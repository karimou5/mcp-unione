---
title: API Error Codes
source: https://docs.unione.io/en/api-errors
synced: 2026-06-04
---

## 6. Global / Common API Error Codes

Format: `HTTP code` | `API code` | meaning & fix. (This is the near-complete list from the "API Errors" section.)

### Authentication / account / system (1xx)
| HTTP | API | Meaning / fix |
|---|---|---|
| 401 | 101 | API key not passed or empty. Pass correct `X-API-KEY` header or `api_key` JSON parameter. |
| 401 | 102 | Invalid key `$apiKey`. Use correct user API key or project API key. |
| 403 | 105 | API is turned OFF. Turn API on in settings. |
| 403 | 106 | User is inactive. Contact support. |
| 400 | 111 | JSON parsing error. Check your JSON request syntax. |
| 401 | 114 | User not found. Send the request to the host you registered at (us1.unione.io or eu1.unione.io). |
| 400 | 118 | No DNS TXT records found. Add DNS verification record from `domain/get-dns-records`. |
| 500 | 120 | Internal DKIM validation error. Contact support. |
| 400 | 121 | Timeout searching domain (DNS request timed out). Try later. |
| 400 | 122 | DKIM record not found. Add DKIM record from `domain/get-dns-records`. |
| 400 | 123 | DKIM record malformed. Set up DKIM properly. |
| 400 | 124 | DKIM record does not match expected. Use the key from `domain/get-dns-records`. |
| 400 | 125 | Several different DKIM keys in DNS entry. Set up DKIM properly. |
| 400 | 126 | Non-DKIM record types present in DNS record. Add the DKIM record from `domain/get-dns-records`. |
| 400 | 127 | Main domain DKIM record limit reached (max 10 DKIM records per primary domain). |
| 400 | 129 | Unknown DKIM validation error. Re-check DKIM record; contact support if persists. |
| 400 | 130 | Domain not allowed according to Registry policy. Use another domain. |
| 500 | 150 | An unknown internal error occurred. Try later or contact support. |
| 413 | 199 | Request too large. Data must be ≤ 10 MB. |

### email/send (2xx)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 201 | Message body is missing. |
| 400 | 202 | Sender email is missing. |
| 400 | 203 | Email subject is missing. |
| 400 | 204 | Email recipients passed improperly (must be array; each recipient an object with required `email`). Also returned if **all** addresses fall into `failed_emails`. |
| 400 | 205 | Invalid sender email. |
| 400 | 206 | Sender email is not verified. Use an email on a verified domain. |
| 400 | 207 | MIME file type is incorrect. |
| 400 | 208 | Invalid attachment filename. Forbidden symbol `$symbol`. |
| 400 | 209 | Attached file names are duplicated. |
| 400 | 210 | Inline attachment names are duplicated. |
| 400 | 211 | Invalid inline attachment filename. Forbidden symbol `$symbol`. |
| 400 | 212 | Recipients passed improperly (`substitutions` not set / too many / wrong type — string/integer only). |
| 400 | 213 | Invalid or non-existent `custom_backend_id`. |
| 403 | 215 | User is not allowed to send. Contact support. |
| 400 | 216 | `metadata` value should be a string or integer. |
| 400 | 217 | Too many metadata fields (max 10). |
| 400 | 218 | Metadata key length should be < 64. |
| 400 | 219 | Metadata value length should be < 1024. |
| 400 | 220 | Metadata key should not be blank. |
| 400 | 221 | `<html>` tag does not exist / invalid in the request. |
| 400 | 223 | Attachment `content` body missing or void. |
| 400 | 224 | Substitution name must be latin chars/numbers/`_`, starting with a letter. |
| 400 | 227 | Invalid or non-existent `smtp_pool_id`. |
| 400 | 228 | Passing `smtp_pool_id` requires `custom_backend_id`. |
| 400 | 229 | Custom backend domain or tracking domain required for sending. |
| 400 | 230 | Only default backend or tracking domain required for sending. |

### Webhook (3xx) & misc
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 303 | Events list contains an unsupported value / event not supported. |
| 400 | 304 | Webhook with specified URL not found. |
| 400 | 305 | URL not passed. |

### Template (6xx)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 601 | Template not found. Check template id. |
| 400 | 602 | Template name is missing. |
| 400 | 603 | Template name already belongs to another template. |
| 400 | 604 | Max number of templates reached (limit 10000). |

### Suppression cause (7xx)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 701 | Cause not found (invalid blocking reason). Contact support. |

### Sending limits / billing (9xx)
| HTTP | API | Meaning / fix |
|---|---|---|
| 403 | 901 | Sending blocked — daily limit reached (auto-increases; contact support). |
| 403 | 902 | Sending limit for free tariff reached. |
| 403 | 903 | Free tariff: only send to own domains with confirmed verification or checked emails. |
| 403 | 904 | Insufficient funds / card failure. |
| 403 | 905 | Reached the limit of emails included in subscription plan. |
| 400 | 906 | Exceeded the daily email reset limit. |
| 500 | 908 | Internal error, project owner not found. |

### email/subscribe (1000–1006)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 1000 | Missing recipient address. |
| 400 | 1001 | Invalid recipient address value. |
| 400 | 1002 | Missing sender address. |
| 400 | 1003 | Sender address not verified. |
| 400 | 1004 | Invalid sender address value. |
| 400 | 1005 | Sender name too long. |
| 400 | 1006 | Exceeded daily limit of `email/subscribe`. |

### Domain methods (1100–1104, 1200–1203, 1300–1306, 1350–1353, 1400–1403)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 1100 | Missing domain name (verification). |
| 400 | 1101 | Invalid domain value. |
| 400 | 1102 | Sending from domain example.ru is prohibited. Use another domain. |
| 400 | 1103 | Public free domains not allowed. Use your own domain. |
| 400 | 1104, 1203, 1306, 1403 | Trying to access sandbox domain records. Use another domain. |
| 400 | 1200 | Missing domain name (validating). |
| 400 | 1201 | Invalid domain value. |
| 400 | 1202 | Domain not registered in UniOne. Call `domain/get-dns-records`. |
| 400 | 1301 | Invalid domain value (verify). |
| 400 | 1302 | Invalid `limit` value (must be integer 1–100). |
| 400 | 1303 | Invalid `offset` value (≥ 0). |
| 400 | 1304 | Invalid `offset` type (must be int). |
| 400 | 1305 | Invalid `limit` type (must be int). |
| 400 | 1350 | `domain` field should not be blank. |
| 400 | 1351 | `domain` value is not a valid domain. |
| 400 | 1352 | Domain not added to your account. |
| 400 | 1353 | Unable to delete sandbox domain. |
| 400 | 1400 | Missing domain name (validating). |
| 400 | 1401 | Invalid or non-existent domain (A/AAAA/MX must exist; DNS propagation). |
| 400 | 1402 | Domain not registered. Call `domain/get-dns-records`. |

### email/send field validation (1506–1599)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 1506 | `headers` must be object. |
| 400 | 1507 | `headers` must contain ≤ 50 elements. |
| 400 | 1508 | `template_id` — no template with this ID. |
| 400 | 1510 | `body.html` must be string. |
| 400 | 1511 | `body.plaintext` must be string. |
| 400 | 1512 | `body.amp` must be string. |
| 400 | 1516 | `body.html` substitutions contain invalid values. |
| 400 | 1517 | `body.plaintext` substitutions contain invalid values. |
| 400 | 1518 | `body.amp` substitutions contain invalid values. |
| 400 | 1519 | `reply_to` must be string. |
| 400 | 1520 | `reply_to` invalid email. |
| 400 | 1521 | `from_name` must be string. |
| 400 | 1522 | `subject` must be string. |
| 400 | 1523 | `template_engine` invalid — one of `simple`, `liquid`, `velocity`, `none`. |
| 400 | 1524 | `recipients` must contain ≤ 500 elements. |
| 400 | 1525 | `options.send_at` must be ≤ 24 hours in advance. |
| 400 | 1526 | `headers["X-UNIONE-Template-Engine"]` invalid — `simple`/`liquid`/`velocity`/`none`. |
| 400 | 1527 | `headers["X-UNIONE-Global-Language"]` not allowed — one of be/de/en/es/fr/it/kz/ru/pl/pt/ua. |
| 400 | 1528 | `global_language` not allowed — one of be/de/en/es/fr/it/kz/ru/pl/pt/ua. |
| 400 | 1529 | `options.send_at` must be in the future. |
| 400 | 1530 | `options.send_at` must be a valid datetime string. |
| 400 | 1532 | `tags` should contain ≤ 4 elements. |
| 400 | 1533 | Cannot create more tags (max 10000). |
| 400 | 1534 | One or more tags too long (max 50 chars). |
| 400 | 1535 | One or more tags contains invalid symbols. |
| 400 | 1537 | `bypass_global` should equal 1. |
| 400 | 1538 | `bypass_unsubscribed` prohibited without `allow_skip_unsubscribe` flag. |
| 400 | 1539 | `bypass_complained` prohibited without `allow_skip_unsubscribe` flag. |
| 400 | 1540 | `metadata` max size 4000 bytes. |
| 400 | 1541 | `global_metadata` max size 4000 bytes. |
| 400 | 1542 | `metadata` + `global_metadata` combined max 4000 bytes. |
| 400 | 1543 | `global_metadata.campaign_id` must be string. |
| 400 | 1544 | `metadata.campaign_id` must be string. |
| 400 | 1545 | `metadata.campaign_id` not a valid number or uuid. |
| 400 | 1546 | `subject` substitutions invalid. |
| 400 | 1547 | `from_name` substitutions invalid. |
| 400 | 1548, 2527 | `options.unsubscribe_url` must be object. |
| 400 | 1549 | `options.unsubscribe_url` invalid substitution format. |
| 400 | 1550 | `options` must be object. |
| 400 | 1551 | `metadata`/`global_metadata` value must be a string. |
| 400 | 1554 | `headers['Cc']` — number of emails in "Cc" must not exceed N. |
| 400 | 1555 | `headers['Cc']` — Cc email must not differ from recipient emails. |
| 400 | 1556 | `headers['Cc']` allowed only with non-empty "To". |
| 400 | 1557 | `headers['To']` — number of emails in "To" must not exceed N. |
| 400 | 1558 | `headers['To']` — To email must not differ from recipient emails. |
| 400 | 1559 | `recipients` not in "To"/"Cc" or domain unconfirmed (BCC only on verified domain). |
| 400 | 1560 | `recipients` count must not exceed sum of "To" and "Cc". |
| 400 | 1561 | `headers['Cc']` not a valid Cc. |
| 400 | 1562 | `headers['To']` not a valid To. |
| 400 | 1565 | `body.html` invalid velocity substitution format. |
| 400 | 1566 | `subject` invalid velocity substitution format. |
| 400 | 1567 | `from_name` invalid velocity substitution format. |
| 400 | 1568 | `reply_to_name` invalid velocity substitution format. |
| 400 | 1569 | `body.plaintext` invalid velocity substitution format. |
| 400 | 1570 | `body.amp` invalid velocity substitution format. |
| 400 | 1571 | `options.unsubscribe_url` invalid velocity substitution format. |
| 400 | 1572 | `idempotence_key` too long (≤ 64 chars). |
| 400 | 1573 | Duplicate message with same `idempotence_key`. |
| 400 | 1574 | `from_email` denied — use address from a confirmed domain. |
| 400 | 1575 | User not allowed to send. |
| 400 | 1576 | `subject` should not be blank. |
| 400 | 1577 | `body` — no message body passed. |
| 400 | 1578 | `body.html` — no valid `<html>` tag. |
| 400 | 1579 | `global_substitutions` — max 2 substitutions. |
| 400 | 1580 | `global_substitutions` name must be latin/numbers/`_`, start with letter. |
| 400 | 1581 | `globalSubstitutions[...]` value must be string or integer. |
| 400 | 1582 | `global_metadata` should contain ≤ 10 elements. |
| 400 | 1583 | `global_substitutions` metadata value must be string or integer. |
| 400 | 1584 | `global_metadata` key should not be blank. |
| 400 | 1585 | `global_metadata` key length < 64. |
| 400 | 1586 | `global_metadata` value ≤ 1024 chars. |
| 400 | 1587 | `force_send` — no rights to use. |
| 400 | 1588 | `skip_unsubscribe` — no right for `skip_unsubscribe = 1`. |
| 400 | 1590 | `attachments.name` forbidden symbol `/`. |
| 400 | 1591 | `attachments` duplicated filename. |
| 400 | 1592 | `attachments.content` missing. |
| 400 | 1593 | `attachments.type` MIME skipped/empty. |
| 400 | 1594 | `inline_attachments.name` forbidden symbol `/`. |
| 400 | 1595 | `inline_attachments` duplicated filename. |
| 400 | 1596 | `inline_attachments.content` missing. |
| 400 | 1597 | `inline_attachments.type` MIME skipped/empty. |
| 403 | 1598 | `from_email` sandbox domain used with unconfirmed email. |
| 403 | 1599 | `from_email` sandbox domain daily sending limit exceeded. |

### Project methods (1601–1726, 1801–1905)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 1601, 1701 | `project` section absent. |
| 400 | 1602, 1702 | `name` should not be blank. |
| 400 | 1603, 1703 | `name` must be string. |
| 400 | 1604, 1704 | `name` ≤ 255 chars. |
| 400 | 1605, 1705 | `name` — project with such name already exists. |
| 400 | 1606 | `send_enabled` must be bool. |
| 400 | 1607 | `custom_unsubscribe_url_enabled` must be bool. |
| 400 | 1608, 1711 | Forbidden to use `custom_unsubscribe_url_enabled`. Contact support. |
| 400 | 1609, 1716 | `country` must be string. |
| 400 | 1610, 1717 | `country` not a valid country (ISO-3166 alpha-2). |
| 400 | 1611, 1718 | `backend_domain_id` must be int. |
| 400 | 1612, 1719 | `backend_domain_id` does not belong to user. |
| 400 | 1613, 1720 | `backend_domain_id` not active. |
| 400 | 1614, 1726 | `unsubscribe_page_id` must be int. |
| 400 | 1706 | `project_api_key` — one of [`project_api_key`/`project_id`] required. |
| 400 | 1707, 1802 | `project_api_key` — project not found. |
| 400 | 1708 | `project_api_key` must be string. |
| 400 | 1709 | `send_enabled` must be bool. |
| 400 | 1710 | `custom_unsubscribe_url_enabled` must be bool. |
| 400 | 1712, 1805, 1905 | `project_id` must be string. |
| 400 | 1713, 1804 | One of [`project_api_key`/`project_id`] must be empty. |
| 400 | 1714, 1806 | `project_id` — project with ID not exists. |
| 400 | 1715, 1807 | `project_id` not valid (use the one from `project/create`). |
| 400 | 1721 | `email_counter` must be int. |
| 400 | 1722 | `email_counter` must equal 0. |
| 400 | 1723 | `email_counter_limit` must be int. |
| 400 | 1724 | `email_counter_limit` ≥ 0. |
| 400 | 1725 | `email_counter_mode` must be bool/`default`/`permanent`. |
| 400 | 1801 | `project_api_key` — one of [`project_api_key`/`project_id`] required. |
| 400 | 1803, 1902 | `project_api_key` must be string. |
| 400 | 1904 | `project_id` not valid (digits only). |

### Template/recipients/editor (2306–2536) — used by template/set and email/send
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 2306 | `recipients` should not be blank. |
| 400 | 2307 | `recipients` must be string. |
| 400 | 2500 | `editor_type` — `html` is required. |
| 400 | 2501 | Template was created in visual editor (must be HTML). |
| 400 | 2502 | `editor_type` should not be blank (pass `html`). |
| 400 | 2503 | `id` — no template with this ID. |
| 400 | 2504 | `headers` must be object. |
| 400 | 2505 | `headers` ≤ 50 elements. |
| 400 | 2514 | `reply_to` must be string. |
| 400 | 2515 | `reply_to` not a valid email. |
| 400 | 2516 | `template_engine` invalid — `simple`/`liquid`/`velocity`/`none`. |
| 400 | 2517 | `subject` must be string. |
| 400 | 2518 | `subject` substitutions invalid. |
| 400 | 2519 | `from_name` must be string. |
| 400 | 2520 | `from_name` substitutions invalid. |
| 400 | 2521 | `from_name` invalid velocity substitution. |
| 400 | 2522 | `subject` invalid velocity substitution. |
| 400 | 2523 | `reply_to_name` invalid velocity substitution. |
| 400 | 2524 | `options` must be string. |
| 400 | 2525 | `options.unsubscribe_url` invalid substitution. |
| 400 | 2526 | `options.unsubscribe_url` invalid velocity substitution. |
| 400 | 2528, 10002 | `attachments.name` ≤ 255 bytes. |
| 400 | 2529, 10001 | `inline_attachments.name` ≤ 255 bytes. |
| 400 | 2530, 10003 | `body.html` invalid Liquid substitution format. |
| 400 | 2531, 10004 | `subject` invalid Liquid substitution format. |
| 400 | 2532, 10005 | `from_name` invalid Liquid substitution format. |
| 400 | 2533, 10006 | `reply_to_name` invalid Liquid substitution format. |
| 400 | 2534, 10007 | `body.plaintext` invalid Liquid substitution format. |
| 400 | 2535, 10008 | `body.amp` invalid Liquid substitution format. |
| 400 | 2536, 10009 | `options.unsubscribe_url` invalid Liquid substitution format. |

### Pagination / webhook / template content (2600–2804)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 2600 | `limit` ≥ 0. |
| 400 | 2601 | `limit` must be int. |
| 400 | 2602 | `offset` ≥ 0. |
| 400 | 2603 | `offset` must be int. |
| 400 | 2700 | `url` must be string. |
| 400 | 2701 | `url` should not be blank. |
| 400 | 2702 | `offset` ≥ 0. |
| 400 | 2703 | `eventFormat` invalid — `json_post` or `json_post_gzip` only. |
| 400 | 2704 | `deliveryInfo` value should be 1/0 or true/false. |
| 400 | 2705 | `singleEvent` value should be 1/0 or true/false. |
| 400 | 2706 | `maxParallel` must be int. |
| 400 | 2707 | `maxParallel` must be between 5 and 100. |
| 400 | 2708 | `events` must be array. |
| 400 | 2709 | `events` should not be blank. |
| 400 | 2710 | `events` — field `email_status` is required. |
| 400 | 2711 | `email_status` value invalid. |
| 400 | 2712 | `spam_block` value invalid. |
| 400 | 2713 | `url` — webhook domain name not found. |
| 400 | 2714 | `status` invalid — `active` or `disabled`. |
| 400 | 2715 | `status` must be string. |
| 400 | 2800 | `name` should not be blank. |
| 400 | 2801 | `name` must be string. |
| 400 | 2802 | `type` must be string. |
| 400 | 2803 | `content` must be string. |
| 400 | 2804 | `content` ≤ 7 MB (9786710 bytes base64). |

### Suppression (2900–3004, 3100–3107, 3200–3209) & email validation (3800–3803)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 2900, 3000, 3100 | `email` should not be blank. |
| 400 | 2901, 3001, 3101 | `email` must be string. |
| 400 | 2902, 3002, 3102 | `email` not a valid email. |
| 400 | 2903 | `all_projects` must be bool. |
| 400 | 3003 | `email` doesn't exist (not in suppression list). |
| 400 | 3004 | `email` cannot be deleted (e.g. severe reason like `blocked`). |
| 400 | 3103 | `cause` should not be blank. |
| 400 | 3104, 3200 | `cause` must be string. |
| 400 | 3105, 3201 | `cause` not allowed (use one of the available values). |
| 400 | 3106 | `created` must be string. |
| 400 | 3107 | `created` not a valid datetime. |
| 400 | 3202 | `source` must be string. |
| 400 | 3203 | `source` not allowed. |
| 400 | 3204 | `start_time` must be string. |
| 400 | 3205 | `start_time` not a valid datetime. |
| 400 | 3206 | `cursor` must be string. |
| 400 | 3207 | `cursor` not allowed. |
| 400 | 3208 | `limit` must be int. |
| 400 | 3209 | `limit` ≥ 0. |
| 400 | 3800 | `email` — max concurrent requests is 4. |
| 400 | 3801 | `email` should not be blank. |
| 400 | 3802 | `email` must be string. |
| 400 | 3803 | Exceeded daily limit of `email-validation/single`. |

### Event-dump (3300–3502, 3600–3602, 3700–3701) & idempotence (3900)
| HTTP | API | Meaning / fix |
|---|---|---|
| 400 | 3300 | `start_time` should not be blank. |
| 400 | 3301 | `start_time` not a valid datetime. |
| 400 | 3302 | `end_time` not a valid datetime. |
| 400 | 3303 | `limit` should be positive. |
| 400 | 3304 | `format` invalid — `csv` or `csv_gzip`. |
| 400 | 3305 | `delimiter` invalid — `;` or `,`. |
| 400 | 3308 | `all_projects` — user lacks required roles (projects methods disabled by default). |
| 400 | 3309 | Max 10 event dumps at a time. |
| 400 | 3310 | `start_time` earlier than allowed `$time`. |
| 400 | 3311 | `limit` must be integer. |
| 400 | 3312 | `delimiter` must be string. |
| 400 | 3313 | `format` must be string. |
| 400 | 3315 | `aggregate` must be string. |
| 400 | 3316 | Cannot use `filter` with `aggregate`. |
| 400 | 3317 | `dumpFields` must be array. |
| 400 | 3318 | `dumpFields` incorrect fields. |
| 400 | 3319 | `aggregate` invalid — only `day_status` or empty. |
| 400 | 3400 | `filter` must be object. |
| 400 | 3401 | `filter.job_id` must be string. |
| 400 | 3402 | `filter.status` must be string. |
| 400 | 3403 | `filter.status` invalid. |
| 400 | 3404 | `filter.email` must be string. |
| 400 | 3405 | `filter.email` not a valid email. |
| 400 | 3406 | `filter.email_from` must be string. |
| 400 | 3407 | `filter.email_from` not a valid email. |
| 400 | 3408 | `filter.domain` must be string. |
| 400 | 3409 | `filter.domain` not a valid domain. |
| 400 | 3410 | `filter.domain` differs from the domain in the email. |
| 400 | 3411 | `filter.delivery_status` must be string. |
| 400 | 3412 | `filter.delivery_status` invalid. |
| 400 | 3413 | `filter.campaign_id` must be string. |
| 400 | 3414 | `filter.campaign_id` invalid number (≤ 128 bit). |
| 400 | 3500, 3600 | `dump_id` should not be blank. |
| 400 | 3501, 3601 | `dump_id` not a valid UUID. |
| 400 | 3502, 3602 | `dump_id` event dump does not exist. |
| 400 | 3700 | `tag_id` should not be blank. |
| 400 | 3701 | `tag_id` must be int. |
| 400 | 3900 | `idempotence_key` must be string. |

---
