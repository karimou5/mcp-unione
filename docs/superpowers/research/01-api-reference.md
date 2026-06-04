# UniOne (Unisender Go) Transactional Web API — Complete Reference

> API version: **Web API v1.87**
> Sources (both render identical content — the single-page MODX reference):
> - https://docs.unione.io/en/web-api-ref
> - https://docs.unione.io/en/api
>
> All content below was extracted verbatim from the static HTML of those pages (parameter tables, response schemas, error tables, enums and code samples). Both URLs serve the same "Web API v1.87" reference document.

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

## 4. HTTP Status Codes (transport level)

| HTTP Code | Meaning |
|---|---|
| 200 | OK – Request was successfully processed. |
| 400 | Bad Request – Your request is invalid. Check request format and parameters. |
| 401 | Unauthorized – Your API key is wrong. |
| 403 | Forbidden – Not enough rights to process the request. |
| 404 | Not Found – The specified endpoint not found. |
| 413 | Request Entity Too Large – Request size is too large, reduce size to 10 MB. |
| 429 | Too Many Requests – Please slow down request rate. |
| 50x | Internal Server Error – Problem on the server (500, 502, 503, etc.). Try again later. |

The HTTP error code gives generic information; a JSON object (see §3) usually accompanies it with the API error code (see §6).

---

## 5. Rate Limits & Size Limits (documented)

- **Request body size**: max **10 MB** (HTTP 413 / API code 199 if exceeded).
- **`email/send`**: max **500 recipients** per request; max request size 10 MB.
- **Attachments / inline attachments**: max file size **7 MB** (= 9 786 710 bytes in base64); attachment name max 255 bytes; `/` not allowed in names.
- **`email-validation/single`**: a maximum of **2 concurrent requests** are allowed; exceeding returns an error (API code 3800 cites 4 concurrent in one message variant — the page text states 2). Also a per-day call limit (API code 3803).
- **HTTP 429** ("Too Many Requests – please slow down request rate") is the generic throttling response — no fixed numeric request-per-second rate is published in the reference.
- **Per-user daily sending limit** exists (auto-increases with good delivery, resets nightly) — API codes 901/902/906.
- **Tags**: max 10 000 per project; max 4 per email; ≤ 50 chars each.
- **Templates**: max 10 000 per account.
- **Event dumps**: max 10 concurrent dumps per user; data retained up to 32 days (tariff-dependent).
- **Scheduled send** (`options.send_at`): up to 24 hours in advance.
- **Metadata**: max 10 keys; key ≤ 64 chars; value ≤ 1024 chars; total metadata ≤ 4000 bytes.

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

# 7. Method Reference (28 methods)

> Common: every method on error returns the error envelope from §3 (`status:"error"`, `message`, `code`). For brevity the error envelope is not repeated per method below.
> Column legend for parameter tables: **Name** (`»` denotes nesting depth) | **Type** | **Req?** | **Default** | **Allowed / Enum** | **Description**.

---

## 7.1 `email/send.json`

`POST /en/transactional/api/v1/email/send.json`
Sends an email or a bunch of emails. While sending you can provide substitutions (merge tags), use a template, turn on read/click tracking, etc.

**Restrictions:**
- maximum request size is **10 MB**
- maximum number of recipients is **500**
- the symbol `/` is not allowed in attachment names
- if the recipient list contains invalid, non-existent, duplicate, or unsubscribed emails, those are returned in `failed_emails` and the email is still sent to the other valid addresses.
- if **all** addresses fall into `failed_emails`, sending is not carried out and **API error 204** is returned.

### Parameters (all under top-level `message` object)

| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `message` | object | **Required** | — | — | Object containing all message properties. |
| `message.recipients` | array | **Required** | — | max 500 | Array of recipients with emails, substitutions and metadata. |
| `message.recipients[].email` | string(email) | **Required** | — | — | Recipient email. |
| `message.recipients[].substitutions` | object | Optional | — | — | Per-recipient substitutions (merge tags). Usable in `body.html`, `body.plaintext`, `body.amp`, `subject`, `from_name`, `headers["List-Unsubscribe"]`, `options.unsubscribe_url`. Names: latin chars/numbers/`_`, must start with a letter. Special `to_name` substitution puts the recipient name in the SMTP "To" header (max 78 chars). |
| `message.recipients[].metadata` | object | Optional | — | — | Per-recipient metadata `"key":"value"`. Max 10 keys; key ≤ 64 chars; value ≤ 1024 chars (combined ≤ 4000 bytes). Returned by webhook & event-dump. A `campaign_id` key (≤128-bit) is treated as campaign identifier in statistics. |
| `message.template_id` | string(uuid) | Optional | — | — | Identifier of a template created via `template/set`. Template fields fill in any omitted `email/send` fields (e.g. `body`, `subject`). |
| `message.tags` | array of strings | Optional | — | each ≤ 50 chars; up to 4; unique; ≤ 10000/project | Categorize emails; passed by event-dump. |
| `message.skip_unsubscribe` | integer | Optional | `0` | `0` = append footer, `1` = skip | Whether to skip appending the default unsubscribe footer. `1` requires support approval. |
| `message.global_language` | string | Optional | — | `be`,`de`,`en`,`es`,`fr`,`it`,`pl`,`pt`,`ru`,`ua`,`kz` | Language of unsubscribe footer & page. |
| `message.template_engine` | string | Optional | `simple` | `simple`, `velocity`, `liquid`, `none` | Template engine for handling substitutions. |
| `message.global_substitutions` | object | Optional | — | — | Substitutions common to all recipients (e.g. company name). Per-recipient `substitutions` override duplicates. Usable in `body.html/plaintext/amp`, `subject`, `from_name`, `options.unsubscribe_url`. |
| `message.global_metadata` | object | Optional | — | — | Metadata common to all recipients. Same limits as recipient metadata. System key `campaign_id` accepts a ≤128-bit non-negative integer or a UUID (`c7703772-...`); invalid values treated as `0`. |
| `message.body` | object | **Required** | — | — | HTML/plaintext/AMP parts; **either `html` or `plaintext` required**. |
| `message.body.html` | string | Optional | — | — | HTML part of the email body. |
| `message.body.plaintext` | string | Optional | — | — | Plaintext part. |
| `message.body.amp` | string | Optional | — | — | AMP part. |
| `message.subject` | string | **Required** | — | — | Email subject. |
| `message.from_email` | string(email) | Optional* | — | — | Sender's email. *Required only if `template_id` is empty. Must be on a verified domain. |
| `message.from_name` | string | Optional | — | — | Sender's name. |
| `message.reply_to` | string | Optional | — | — | Reply-To email (if different from sender). |
| `message.reply_to_name` | string | Optional | — | — | Reply-To name (if `reply_to` set and you want a display name). |
| `message.track_links` | integer | Optional | `1` | `0`,`1` | `1` = click tracking on (default), `0` = off (needs support to enable). |
| `message.track_read` | integer | Optional | `1` | `0`,`1` | `1` = read tracking on (default), `0` = off (needs support to enable). |
| `message.bypass_global` | integer | Optional | `0` | `0`,`1` | `1` = ignore the global unavailability list. May be ignored for some addresses. |
| `message.bypass_unavailable` | integer | Optional | `0` | `0`,`1` | `1` = ignore current user's/project's unavailability list. Works only if `bypass_global=1`. |
| `message.bypass_unsubscribed` | integer | Optional | `0` | `0`,`1` | `1` = ignore unsubscribed list. Works only if `bypass_global=1`; requires the "omit unsubscribe link" right (support). |
| `message.bypass_complained` | integer | Optional | `0` | `0`,`1` | `1` = ignore complaint list. Works only if `bypass_global=1`; requires "omit unsubscribe link" right (support). |
| `message.idempotence_key` | string | Optional | — | ≤ 64 chars | Unique message key to prevent duplicates; resending the same key within 1 minute is declined. |
| `message.headers` | object | Optional | — | max 50 | Email headers. Only `X-` prefixed accepted (others ignored), e.g. `X-UNIONE-Global-Language`, `X-UNIONE-Template-Engine`. Standard `To`/`CC`/`BCC` passed without `X-` (with restrictions). With support approval: `List-Unsubscribe`, `List-Subscribe`, `List-Help`, `List-Owner`, `List-Archive`, `In-Reply-To`, `References`. |
| `message.headers["X-UNIONE-Global-Language"]` | string | Optional | — | `be`,`de`,`en`,`es`,`fr`,`it`,`pl`,`pt`,`ru`,`ua`,`kz` | Unsubscribe footer/page language. |
| `message.headers["X-UNIONE-Template-Engine"]` | string | Optional | `simple` | `simple`,`velocity`,`liquid`,`none` | Template engine; has priority over `template_engine`. |
| `message.attachments` | array | Optional | — | — | Array of attachments. |
| `message.attachments[].type` | string | **Required** | — | MIME type | Attachment MIME type; if unsure use `application/octet-stream`. |
| `message.attachments[].name` | string | **Required** | — | unique; no `/`; ≤ 255 bytes | Filename `name.extension`. |
| `message.attachments[].content` | string(byte) | **Required** | — | ≤ 7 MB (9786710 bytes base64) | File contents in base64. |
| `message.inline_attachments` | array | Optional | — | — | Inline attachments (e.g. embed images by CID). |
| `message.inline_attachments[].type` | string | **Required** | — | MIME type | Attachment MIME type. |
| `message.inline_attachments[].name` | string | **Required** | — | — | Content ID; referenced in HTML as `<img src="cid:NAME">` (e.g. `IMAGECID1`). |
| `message.inline_attachments[].content` | string(byte) | **Required** | — | ≤ 7 MB | File contents in base64. |
| `message.options` | object | Optional | — | — | Additional message options. |
| `message.options.send_at` | string | Optional | — | `YYYY-MM-DD hh:mm:ss` UTC | Schedule sending up to 24h in advance. |
| `message.options.unsubscribe_url` | string | Optional | — | — | Custom unsubscribe link. |
| `message.options.custom_backend_id` | integer | Optional | — | — | Backend-domain (dedicated IP) identifier. Default used if absent. |
| `message.options.smtp_pool_id` | string(uuid) | Optional | — | — | SMTP pool identifier; usually auto-selected (requires `custom_backend_id` if passed). |

**Request body example:**
```json
{
  "message": {
    "recipients": [
      { "email": "email@example.com",
        "substitutions": { "tag": "value" },
        "metadata": { "key": "value" } }
    ],
    "template_id": "00000000-0000-0000-0000-000000000000",
    "tags": [],
    "skip_unsubscribe": 0,
    "global_language": "en",
    "template_engine": "velocity",
    "global_substitutions": { "property1": "string", "property2": "string" },
    "global_metadata": { "property1": "string", "property2": "string" },
    "body": {
      "html": "<b>Hello, {{to_name}}</b>",
      "plaintext": "Hello, {{to_name}}",
      "amp": "<!doctype html><html amp4email>...</html>"
    },
    "subject": "UniOne test email",
    "from_email": "email@example.com",
    "from_name": "John Smith",
    "reply_to": "email@example.com",
    "reply_to_name": "John Smith",
    "track_links": 0,
    "track_read": 0,
    "bypass_global": 0,
    "bypass_unavailable": 0,
    "bypass_unsubscribed": 0,
    "bypass_complained": 0,
    "idempotence_key": "SG1VsbG68sIH2dvc5mx890kIQ",
    "headers": { "X-MyHeader": "some data" },
    "attachments": [ { "type": "text/plain", "name": "readme.txt", "content": "SGVsbG8sIHdvcmxkIQ==" } ],
    "inline_attachments": [ { "type": "image/gif", "name": "IMAGECID1", "content": "R0lGODdh..." } ],
    "options": {}
  }
}
```

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `job_id` | string | Required | Job identifier (useful for error investigation). |
| `emails` | array | Optional | Recipient emails successfully accepted for sending. |
| `failed_emails` | object | Optional | Map of rejected email → status. Possible statuses: `unsubscribed`, `invalid`, `duplicate`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` (new statuses may be added). |

```json
{
  "status": "success",
  "job_id": "1ZymBc-00041N-9X",
  "emails": ["user@example.com"],
  "failed_emails": {
    "email1@gmail.com": "temporary_unavailable",
    "bad@address": "invalid",
    "email@example.com": "duplicate",
    "root@example.org": "permanent_unavailable",
    "olduser@example.net": "unsubscribed"
  }
}
```

**`failed_emails` status meanings:**
- `unsubscribed` — the email is unsubscribed.
- `invalid` — the email does not exist or is malformed.
- `duplicate` — already present in the request (duplication prevented).
- `temporary_unavailable` — unavailable; for the next 3 days sending will error (spam rejection, full/unused mailbox, domain not accepting mail, blacklisted sending server, etc.).
- `permanent_unavailable` — permanently unavailable or globally unsubscribed.
- `complained` — recipient reported spam in previous emails.
- `blocked` — sending prohibited by UniOne administration.

---

## 7.2 `email/subscribe.json`

`POST /en/transactional/api/v1/email/subscribe.json`

### Parameters
| Name | Type | Req? | Allowed / Alias | Description |
|---|---|---|---|---|
| `from_email` | string(email) | **Required** | alias `email_address_from` | Sender's email. |
| `from_name` | string | **Required** | alias `name_from` | Sender's name. |
| `to_email` | string(email) | **Required** | alias `email_address_to` | Recipient's email. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

```json
{ "status": "success" }
```

---

## 7.3 `email-validation/single.json`

`POST /en/transactional/api/v1/email-validation/single.json`
A maximum of **two concurrent requests** are allowed (else an error is returned). There is also a daily call limit (error 3803).

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `email` | string(email) | **Required** | Email address to be checked. |

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Required | — | `"success"`. |
| `email` | string(email) | Required | — | The checked email. |
| `result` | string | Required | `valid`, `invalid`, `suspicious`, `unknown` | Validation result. `unknown` = could not validate (mail server timeout). |
| `cause` | string | Required | `no_mx_record`, `syntax_error`, `possible_typo`, `mailbox_not_found`, `global_suppression`, `disposable`, `role`, `abuse`, `spamtrap`, `smtp_connection_failed` | Detailed reason. |
| `validity` | integer | Required | 0–100 | Validity score (0 invalid → 100 valid). |
| `local_part` | string | Required | — | Local part (before `@`). |
| `domain` | string | Required | — | Domain part. |
| `mx_found` | boolean | Required | — | True if the domain has an MX record. |
| `mx_record` | string | Required | — | Preferred MX record for the domain. |
| `did_you_mean` | string(email) | Required | — | Suggested fixed variant when `cause=possible_typo`. |
| `processed_at` | string(utc-date-time) | Required | `YYYY-MM-DD hh:mm:ss` UTC | Check date/time. |

```json
{
  "status": "success", "email": "user@example.com", "result": "suspicious",
  "cause": "disposable", "validity": 10, "local_part": "user",
  "domain": "example.com", "mx_found": true, "mx_record": 10,
  "did_you_mean": "user@example.com", "processed_at": "2023-01-01 22:14:59"
}
```

---

## 7.4 `template/set.json`

`POST /en/transactional/api/v1/template/set.json`
Creates a new template (omit `id`) or edits an existing one (provide `id`).

### Parameters (all under top-level `template` object)
| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `template` | object | **Required** | — | — | All template properties. |
| `template.id` | string(uuid) | Optional | — | — | Omit to create; provide to edit an existing template. |
| `template.name` | string | **Required** | — | — | Template name. |
| `template.editor_type` | string | Optional | `html` | `html`, `visual` | Editor type. `visual` can only be created in the web interface. |
| `template.template_engine` | string | Optional | `simple` | `simple`, `velocity`, `liquid`, `none` | Template engine. |
| `template.global_substitutions` | object | Optional | — | — | Substitutions common to all recipients. |
| `template.global_metadata` | object | Optional | — | — | Metadata common to all recipients (max 10 keys, key ≤ 64, value ≤ 1024; `campaign_id` supported). |
| `template.body` | object | Optional | — | — | HTML/plaintext/AMP parts; either `html` or `plaintext` required. |
| `template.body.html` | string | Optional | — | — | HTML part. |
| `template.body.plaintext` | string | Optional | — | — | Plaintext part. |
| `template.body.amp` | string | Optional | — | — | AMP part. |
| `template.subject` | string | Optional | — | — | Email subject. |
| `template.from_email` | string | **Required** | — | — | Sender's email. |
| `template.from_name` | string | Optional | — | — | Sender's name. |
| `template.reply_to` | string | Optional | — | — | Reply-To email. |
| `template.reply_to_name` | string | Optional | — | — | Reply-To name. |
| `template.track_links` | integer | Optional | `1` | `0`,`1` | Click tracking (0 needs support). |
| `template.track_read` | integer | Optional | `1` | `0`,`1` | Read tracking (0 needs support). |
| `template.headers` | object | Optional | — | max 50 | Same rules as `email/send` headers. |
| `template.headers["X-UNIONE-Global-Language"]` | string | Optional | — | be/de/en/es/fr/it/pl/pt/ru/ua/kz | Unsubscribe language. |
| `template.headers["X-UNIONE-Template-Engine"]` | string | Optional | `simple` | simple/velocity/liquid/none | Engine; priority over `template_engine`. |
| `template.attachments[]` | array | Optional | — | — | `type` (req), `name` (req, unique, no `/`), `content` (req, base64 ≤ 7 MB). |
| `template.inline_attachments[]` | array | Optional | — | — | `type` (req), `name` (req, content-id), `content` (req, base64 ≤ 7 MB). |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `template` | object | Required | The stored template object (same fields as input, including assigned `id`). |

---

## 7.5 `template/get.json`

`POST /en/transactional/api/v1/template/get.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `id` | string(uuid) | **Required** | Template id. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `template` | object | Required | Full template object (same structure as in `template/set`, plus `created` date returned). |

---

## 7.6 `template/list.json`

`POST /en/transactional/api/v1/template/list.json`

### Parameters
| Name | Type | Req? | Default | Description |
|---|---|---|---|---|
| `limit` | integer | Optional | `50` | Number of templates returned. |
| `offset` | integer | Optional | `0` | Index of first template (0-based). |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `templates` | array | Required | Array of template objects. |
| `templates[].id` | string(uuid) | Required | Template id. |
| `templates[].name` | string | Required | Template name. |
| `templates[].editor_type` | string | Optional | `html`/`visual`. |
| `templates[].template_engine` | string | Optional | simple/velocity/liquid/none. |
| `templates[].global_substitutions` | object | Optional | Common substitutions. |
| `templates[].global_metadata` | object | Optional | Common metadata. |
| `templates[].body` | object | Required | html/plaintext/amp. |
| `templates[].subject` | string | Optional | Subject. |
| `templates[].from_email` | string | Required | Sender email. |
| `templates[].from_name` | string | Optional | Sender name. |
| `templates[].reply_to` / `reply_to_name` | string | Optional | Reply-To. |
| `templates[].track_links` / `track_read` | integer | Optional | Tracking flags. |
| `templates[].headers` | object | Optional | Headers. |
| `templates[].attachments` / `inline_attachments` | array | Optional | Attachments. |
| `templates[].created` | string(utc-date-time) | Required | Creation date/time `YYYY-MM-DD hh:mm:ss` UTC. |
| `templates[].user_id` | integer | Required | Unique user id. |
| `templates[].project_id` | string | Optional | Project id (≤ 36 chars ASCII). |
| `templates[].project_name` | string | Optional | Project name. |

---

## 7.7 `template/delete.json`

`POST /en/transactional/api/v1/template/delete.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `id` | string(uuid) | **Required** | Template id. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.8 `webhook/set.json`

`POST /en/transactional/api/v1/webhook/set.json`

### Parameters
| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `url` | string(uri) | **Required** | — | ASCII only (Punycode for non-ASCII) | URL receiving notifications; unique per user/project. |
| `status` | string | Optional | `active` | `active`, `disabled`, `stopped` | `disabled` = disabled by user; `stopped` = stopped by system after 24h of failed calls (≥ 10 distinct events). |
| `event_format` | string | Optional | `json_post` | `json_post`, `json_post_gzip` | Notification format. |
| `delivery_info` | integer | Optional | — | `0`,`1` | `1` returns detailed delivery info (SMTP response & internal status for bounces; user-agent/IP/geo for opened/clicked; URL for clicked; `sender_ip` for delivered/bounced when available). |
| `single_event` | integer | Optional | — | `0`,`1` | `0` = batch events per call; `1` = single event per call (not recommended). |
| `max_parallel` | integer | Optional | — | 5–100 (per error 2707) | Max parallel queries to your server. |
| `events` | object | Optional | — | — | Events to notify of. |
| `events.spam_block` | array | Optional | — | single element `"*"` | Report spam-block events. |
| `events.email_status` | array | Optional | — | `delivered`,`opened`,`clicked`,`unsubscribed`,`subscribed`,`soft_bounced`,`hard_bounced`,`spam` (and `accepted`,`sent`) | Status-change events to report. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `object` | object | Required | Webhook object. |
| `object.id` | integer | Required | Webhook id. |
| `object.url` | string(uri) | Required | URL. |
| `object.status` | string | Required | `active`/`disabled`/`stopped`. |
| `object.event_format` | string | Required | `json_post`/`json_post_gzip`. |
| `object.delivery_info` | integer | Required | 0/1. |
| `object.single_event` | integer | Required | 0/1. |
| `object.max_parallel` | integer | Required | Max parallel. |
| `object.updated_at` | string(utc-date-time) | Optional | Last update `YYYY-MM-DD hh:mm:ss` UTC. |
| `object.events` | object | Optional | `spam_block[]`, `email_status[]`. |

### Webhook callback payload (`callback-format`)
The webhook POSTs the following body to your `url`:

| Name | Type | Req? | Description |
|---|---|---|---|
| `auth` | string | Required | MD5 hash of the message body with `auth` value replaced by the user/project API key (authentication + integrity check). |
| `events_by_user` | array | Required | Single-element array containing the user's/project's events. |
| `» user_id` | integer | Required | Unique user id. |
| `» project_id` | string | Optional | Present only if webhook registered with project API key. |
| `» project_name` | string | Optional | Present only for project webhooks. |
| `» events` | array | Required | Array of reported events. |
| `»» event_name` | string | Optional | `transactional_email_status` or `transactional_spam_block`. |
| `»» event_data` | object | Optional | Event properties (depends on `event_name`). |
| `»»» job_id` | string | Optional | Job id (email_status events). |
| `»»» metadata` | object | Optional | Metadata from `email/send` (email_status events). |
| `»»» email` | string(email) | Optional | Recipient email (email_status events). |
| `»»» status` | string | Optional | `accepted`,`sent`,`delivered`,`opened`,`clicked`,`unsubscribed`,`subscribed`,`soft_bounced`,`hard_bounced`,`spam`. |
| `»»» event_time` | string(utc-date-time) | Optional | Event time UTC. |
| `»»» url` | string(uri) | Optional | URL for opened/clicked. |
| `»»» delivery_info` | object | Optional | Detailed delivery info (only when webhook `delivery_info=1`). |
| `»»»» delivery_status` | string | Optional | Internal delivery status (see event-dump filter.delivery_status enum). |
| `»»»» destination_response` | string | Optional | SMTP response. |
| `»»»» user_agent` | string | Optional | Recipient UA (clicked/opened). |
| `»»»» ip` | string | Optional | Recipient IP (clicked/opened). |
| `»»»» country_code` | string | Optional | ISO 3166-1 alpha-2 (clicked/opened). |
| `»»»» country` / `city` | string | Optional | Geo from IP (clicked/opened). |
| `»»»» sender_ip` | string | Optional | Sending SMTP server IP (delivered/bounced, if available). |
| `»»» block_time` | string(utc-date-time) | Optional | Spam-block time (spam_block events). |
| `»»» block_type` | string | Optional | `single`/`multiple` (spam_block events). |
| `»»» domain` | string | Optional | Domain that blocked sending. |
| `»»» SMTP_blocks_count` | integer | Optional | Number of SMTPs blocked. |
| `»»» domain_status` | string | Optional | Block or unblock event. |

---

## 7.9 `webhook/get.json`

`POST /en/transactional/api/v1/webhook/get.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `url` | string(uri) | **Required** | Webhook URL. |

### Response (HTTP 200)
Same as `webhook/set` response: `status` + `object` (id, url, status, event_format, delivery_info, single_event, max_parallel, updated_at, events).

---

## 7.10 `webhook/list.json`

`POST /en/transactional/api/v1/webhook/list.json`

### Parameters
| Name | Type | Req? | Default | Description |
|---|---|---|---|---|
| `limit` | integer | Optional | (50 recommended) | Number of webhooks returned. |
| `offset` | integer | Optional | `0` | Index of first webhook. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `objects` | array | Optional | Array of webhook objects (same fields as `webhook/set` `object`). |

---

## 7.11 `webhook/delete.json`

`POST /en/transactional/api/v1/webhook/delete.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `url` | string(uri) | **Required** | Webhook URL. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.12 `suppression/set.json`

`POST /en/transactional/api/v1/suppression/set.json`

### Parameters
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `email` | string(email) | **Required** | — | Email to add to suppression list. |
| `cause` | string | **Required** | `unsubscribed`, `temporary_unavailable`, `permanent_unavailable`, `complained` | Cause of suppression. |
| `created` | string(utc-date-time) | Optional | `YYYY-MM-DD hh:mm:ss` UTC | When suppression was created. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.13 `suppression/get.json`

`POST /en/transactional/api/v1/suppression/get.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `email` | string(email) | **Required** | Email to get suppression details for. |
| `all_projects` | boolean | Optional | If projects enabled, `true` searches across all projects' data. |

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Required | — | `"success"`. |
| `email` | string(email) | Required | — | The requested email. |
| `suppressions` | array | Required | — | Array (may be empty if not suppressed). |
| `suppressions[].project_id` | string | Optional | — | Project id (≤ 36 chars). |
| `suppressions[].cause` | string | Required | `unsubscribed`,`temporary_unavailable`,`permanent_unavailable`,`complained`,`blocked` | Suppression cause. |
| `suppressions[].source` | string | Required | `user`,`system`,`subscriber` | `user` = via `suppression/set`; `system` = system-prohibited (e.g. multiple hard bounces); `subscriber` = recipient complained/unsubscribed. |
| `suppressions[].is_deletable` | boolean | Required | — | Whether deletable via `suppression/delete`. |
| `suppressions[].created` | string(utc-date-time) | Required | — | Creation time UTC. |

```json
{ "status": "success", "email": "user@example.com",
  "suppressions": [ { "project_id": "6123462132634", "cause": "unsubscribed",
    "source": "user", "is_deletable": true, "created": "2021-12-19 10:15:49" } ] }
```

---

## 7.14 `suppression/list.json`

`POST /en/transactional/api/v1/suppression/list.json`

### Parameters
| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `cause` | string | Optional | — | `unsubscribed`,`temporary_unavailable`,`permanent_unavailable`,`complained`,`blocked` | Filter by cause. |
| `source` | string | Optional | — | `user`,`system`,`subscriber` | Filter by source. |
| `start_time` | string(utc-date) | Optional | — | `YYYY-MM-DD hh:mm:ss` | List from this time to present. Ignored if `cursor` set. |
| `cursor` | string | Optional | — | — | Pagination cursor from previous response; empty/omitted for first chunk. |
| `limit` | integer | Optional | `50` | — | Records per page. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `suppressions` | array | Required | Array of suppression objects. |
| `suppressions[].email` | string(email) | Optional | The email. |
| `suppressions[].cause` | string | Required | (same enum as above). |
| `suppressions[].source` | string | Required | `user`/`system`/`subscriber`. |
| `suppressions[].is_deletable` | boolean | Required | Deletable flag. |
| `suppressions[].created` | string(utc-date-time) | Required | Creation time UTC. |
| `cursor` | string | Required | Cursor for the next chunk. |

---

## 7.15 `suppression/delete.json`

`POST /en/transactional/api/v1/suppression/delete.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `email` | string(email) | **Required** | Email to delete from suppression list. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.16 `domain/get-dns-records.json`

`POST /en/transactional/api/v1/domain/get-dns-records.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `domain` | string | **Required** | Domain to get DNS records for. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `domain` | string | Required | The domain. |
| `verification-record` | string | Required | TXT record to add as-is to verify ownership. |
| `dkim` | string | Required | DKIM key part only — prepend `k=rsa, p=` for a valid record. |

```json
{ "status": "success", "domain": "example.com",
  "verification-record": "unione-validate-hash=483bb362ebdbeedd755cfb1d4d661",
  "dkim": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDo7" }
```

---

## 7.17 `domain/validate-verification-record.json`

`POST /en/transactional/api/v1/domain/validate-verification-record.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `domain` | string | **Required** | Domain to validate verification record for. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `message` | string | Required | Debug message (e.g. `"Record updated"`). |

---

## 7.18 `domain/validate-dkim.json`

`POST /en/transactional/api/v1/domain/validate-dkim.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `domain` | string | **Required** | Domain to validate DKIM record for. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `message` | string | Required | Debug message. |

---

## 7.19 `domain/list.json`

`POST /en/transactional/api/v1/domain/list.json`

### Parameters
| Name | Type | Req? | Default | Description |
|---|---|---|---|---|
| `domain` | string | Optional | — | Get status of a single domain only. |
| `limit` | integer | Optional | `50` | Number of domains returned. |
| `offset` | integer | Optional | `0` | Index of first domain. |

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Required | — | `"success"`. |
| `domains` | array | Required | — | Array of domain objects. |
| `domains[].domain` | string | Required | — | Domain name. |
| `domains[].verification-record` | object | Required | — | `{value, status}`. |
| `domains[].verification-record.value` | string | Optional | — | TXT record value. |
| `domains[].verification-record.status` | string | Optional | `confirmed` (required to send) | Verification status. |
| `domains[].dkim` | object | Required | — | `{key, status}`. |
| `domains[].dkim.key` | string | Optional | — | DKIM key part. |
| `domains[].dkim.status` | string | Optional | `active` (required to send) | DKIM status. |

> Note: `domain/delete.json` also exists in the reference (parameter `domain` required; returns `status` + `message:"Domain deleted"`). It is listed in the docs under Domain Methods although not in the 28-method scope of this task.

---

## 7.20 `event-dump/create.json`

`POST /en/transactional/api/v1/event-dump/create.json`

### Parameters
| Name | Type | Req? | Default | Allowed / Enum | Description |
|---|---|---|---|---|---|
| `start_time` | string(utc-date-time) | **Required** | — | `YYYY-MM-DD hh:mm:ss` | Period start. Data retained up to 32 days (tariff-dependent). |
| `end_time` | string(utc-date-time) | Optional | — | `YYYY-MM-DD hh:mm:ss` | Period end (non-inclusive). |
| `limit` | integer | Optional | `50` | — | Max events. If > 100 000, multiple files (100 000 events each). |
| `all_projects` | boolean | Optional | — | `true`/`false` | Fetch data for all projects (accounts with projects). |
| `filter` | object | Optional | — | — | Event dump filter (mutually exclusive with `aggregate`). |
| `filter.job_id` | string | Optional | — | — | Job id from `email/send`. |
| `filter.status` | string | Optional | — | `accepted`,`sent`,`delivered`,`opened`,`clicked`,`unsubscribed`,`subscribed`,`soft_bounced`,`hard_bounced`,`spam` | Email status. |
| `filter.delivery_status` | string | Optional | — | comma-separated, e.g. `err_user_unknown`,`err_user_inactive`,`err_will_retry`,`err_mailbox_discarded`,`err_mailbox_full`,`err_spam_rejected`,`err_blacklisted`,`err_too_large`,`err_unsubscribed`,`err_unreachable`,`err_skip_letter`,`err_domain_inactive`,`err_destination_misconfigured`,`err_delivery_failed`,`err_spam_skipped`,`err_lost` (plus undocumented: `ok_sent`,`ok_delivered`,`ok_read`,`ok_link_visited`,`ok_unsubscribed`,`ok_resubscribed`,`ok_spam_folder`,`ok_fbl`,`not_sent`,`skip_dup_unreachable`,`skip_dup_temp_unreachable`,`skip_dup_mailbox_full`,`err_spam_removed`,`err_resend`,`err_unknown`,`err_retry_letter`,`err_src_invalid`,`err_dest_invalid`,`err_not_available`,`err_internal`,`err_no_dns`,`err_no_smtp`,`err_giveup`) | UniOne internal detailed delivery status. |
| `filter.email` | string(email) | Optional | — | — | Recipient email. |
| `filter.email_from` | string(email) | Optional | — | — | Sender email. |
| `filter.domain` | string | Optional | — | — | Recipient domain. |
| `filter.campaign_id` | string | Optional | — | ≤128-bit int or UUID | Campaign identifier (metadata `campaign_id`). |
| `dump_fields` | array | Optional | default field list | Allowed (default order): `project_id`,`event_time`,`job_id`,`from_email`,`email`,`status`,`delivery_status`,`metadata`,`destination_response`,`user_agent`,`url`,`ip`,`tags`; plus optional `subject` (not included by default) | Columns to include, in order. |
| `aggregate` | string | Optional | `""` (empty) | `day_status` or empty | Aggregated statistics (filter must be empty when used). |
| `delimiter` | string | Optional | `,` | `,` or `;` | Field delimiter. |
| `format` | string | Optional | `csv` | `csv`, `csv_gzip` | File format. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `dump_id` | string | Required | Dump id, used with `event-dump/get`. |

---

## 7.21 `event-dump/get.json`

`POST /en/transactional/api/v1/event-dump/get.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `dump_id` | string | **Required** | Dump id from `event-dump/create`. |

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Required | — | `"success"`. |
| `event_dump` | object | Required | — | Dump info. |
| `event_dump.dump_id` | string | Required | — | Dump id. |
| `event_dump.dump_status` | string | Required | `queued`,`in_process`,`ready`,`failed` | Task status. |
| `event_dump.files` | array | Optional | — | Files ready for download (may begin while `in_process`; empty array if no events). |
| `event_dump.files[].url` | string | Required | — | Download URL (`.csv` or `.csv.gz`). |
| `event_dump.files[].size` | integer | Required | — | File size. |

```json
{ "status": "success",
  "event_dump": { "dump_id": "Gqfasjh34tlasd", "dump_status": "in_process",
    "files": [ { "url": "https://eu1.unione.io/event-dump/...-1.csv", "size": 512345 } ] } }
```

---

## 7.22 `event-dump/list.json`

`POST /en/transactional/api/v1/event-dump/list.json`
(No request parameters documented.)

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `event_dumps` | array | Required | Array of dump objects (same shape as `event-dump/get` `event_dump`). |
| `event_dumps[].dump_id` | string | Required | Dump id. |
| `event_dumps[].dump_status` | string | Required | `queued`/`in_process`/`ready`/`failed`. |
| `event_dumps[].files[].url` | string | Required | Download URL. |
| `event_dumps[].files[].size` | integer | Required | File size. |

---

## 7.23 `event-dump/delete.json`

`POST /en/transactional/api/v1/event-dump/delete.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `dump_id` | string | **Required** | Dump id from `event-dump/create`. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.24 `tag/list.json`

`POST /en/transactional/api/v1/tag/list.json`
(No request parameters documented.)

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `tags` | array | Required | Array of tag objects. |
| `tags[].tag_id` | integer | Required | Unique tag id. |
| `tags[].tag` | string | Required | Tag name. |

---

## 7.25 `tag/delete.json`

`POST /en/transactional/api/v1/tag/delete.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `tag_id` | integer | **Required** | Unique tag id. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |

---

## 7.26 `project/create.json`

`POST /en/transactional/api/v1/project/create.json`
(Only callable with the **user API key**, not a project key.)

### Parameters (under top-level `project` object)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `project` | object | **Required** | — | Project properties. |
| `project.name` | string | **Required** | unique per account; ≤ 255 chars | Project name. |
| `project.country` | string | Optional | ISO-3166 alpha-2 | Treats personal data per country laws (e.g. GDPR). |
| `project.send_enabled` | boolean | Optional | `true`/`false` | Whether sending is enabled. |
| `project.custom_unsubscribe_url_enabled` | boolean | Optional | `true`/`false` | `true` avoids default footer and permits custom/no unsubscribe URL (requires support approval). Defaults to user value if omitted. |
| `project.backend_domain_id` | integer | Optional | — | Tracking domain / dedicated IP pool default. |
| `project.unsubscribe_page_id` | integer | Optional | — | Default unsubscribe page id. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `project_id` | string | Required | Unique project id (≤ 36 chars ASCII). |
| `project_api_key` | string | Required | Project API key (usable instead of user key in all non-`project/*` methods). |

---

## 7.27 `project/update.json`

`POST /en/transactional/api/v1/project/update.json`
Identify the project by **`project_id`** (recommended) **or** `project_api_key` (exactly one).

### Parameters
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `project_id` | string | Optional* | — | Identify project to update (recommended). |
| `project_api_key` | string | Optional* | — | Alternative identifier. *Exactly one of `project_id`/`project_api_key` is required. |
| `project` | object | **Required** | — | Project properties. |
| `project.name` | string | **Required** | unique; ≤ 255 chars | Project name. |
| `project.country` | string | Optional | ISO-3166 alpha-2 | Country. |
| `project.send_enabled` | boolean | Optional | `true`/`false` | Sending enabled. |
| `project.custom_unsubscribe_url_enabled` | boolean | Optional | `true`/`false` | Custom unsubscribe behaviour (support-gated). |
| `project.backend_domain_id` | integer | Optional | — | Backend domain id. |
| `project.unsubscribe_page_id` | integer | Optional | — | Unsubscribe page id. |
| `project.email_counter` | integer | Optional | only `0` accepted | Reset counter to zero (null/absent = unchanged). |
| `project.email_counter_limit` | integer | Optional | ≥ 0 (0 = no limit) | Max emails the project may send. |
| `project.email_counter_mode` | string | Optional | `default`, `permanent` | `default` resets each accounting period; `permanent` never auto-resets. |

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"`. |
| `project_api_key` | string | Optional | Returned only when the project was identified by `project_api_key` (not when identified by `project_id`). |

---

## 7.28 `project/list.json`

`POST /en/transactional/api/v1/project/list.json`

### Parameters
| Name | Type | Req? | Description |
|---|---|---|---|
| `project_id` | string | Optional | Limit list to a single project. |
| `project_api_key` | string | Optional | Limit list to a single project. |

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Optional | — | `"success"`. |
| `projects` | array | Optional | — | One object per project. |
| `projects[].id` | string | Required | — | Project id (≤ 36 chars). |
| `projects[].api_key` | string | Required | — | Project API key. |
| `projects[].name` | string | Required | — | Project name. |
| `projects[].country` | string | Required | ISO-3166 alpha-2 | Country. |
| `projects[].reg_time` | string(utc-date-time) | Required | `YYYY-MM-DD hh:mm:ss` UTC | Creation time. |
| `projects[].send_enabled` | boolean | Required | — | Sending enabled. |
| `projects[].custom_unsubscribe_url_enabled` | boolean | Required | — | Custom unsubscribe flag. |
| `projects[].backend_domain_id` | integer | Required | — | Backend domain id. |
| `projects[].email_counter` | integer | Required | — | Counter value (increments per email sent). |
| `projects[].email_counter_limit` | integer | Required | 0 = no limit | Email send limit. |
| `projects[].email_counter_mode` | string | Required | `default`, `permanent` | Counter mode. |
| `projects[].unsubscribe_page_id` | integer | Required | — | Unsubscribe page id. |

### `project/delete.json`
`POST /en/transactional/api/v1/project/delete.json`

**Parameters:** `project_id` (optional) **or** `project_api_key` (optional) — exactly one identifies the project (`project_id` recommended).
**Response (HTTP 200):** `{ "status": "success" }`.

---

## 7.29 `system/info.json`

`POST /en/transactional/api/v1/system/info.json`
(No request parameters.)

### Response (HTTP 200)
| Name | Type | Req? | Allowed / Enum | Description |
|---|---|---|---|---|
| `status` | string | Required | — | `"success"`. |
| `user_id` | integer | Required | — | Unique user id. |
| `email` | string(email) | Required | — | User's email. |
| `project_id` | string | Optional | — | Present only when the request used a project API key. |
| `project_name` | string | Optional | — | Present only for project key. |
| `project_accounting` | object | Optional | — | Email counter props. Present only with **user** API key. |
| `project_accounting.email_counter` | integer | Required | — | Counter value. |
| `project_accounting.email_counter_limit` | integer | Required | 0 = no limit | Send limit. |
| `project_accounting.email_counter_mode` | string | Required | `default`,`permanent` | Counter mode. |
| `accounting` | object | Optional | — | Accounting period props. Present only with **user** API key. |
| `accounting.period_start` | string(utc-date-time) | Required | — | Accounting period start UTC. |
| `accounting.period_end` | string(utc-date-time) | Required | — | Accounting period end UTC. |
| `accounting.emails_included` | integer(int64) | Required | — | Emails included in the period. |
| `accounting.emails_sent` | integer(int64) | Required | — | Emails sent (may exceed included on overage). |

---

## 7.30 `system/ping.json` (exists)

`POST /en/transactional/api/v1/system/ping.json`
(No request parameters.) Validates the API key.

### Response (HTTP 200)
| Name | Type | Req? | Description |
|---|---|---|---|
| `status` | string | Required | `"success"` (API key is valid). |
| `user_id` | integer | Required | Unique user id. |

---

## 8. Obsolete Methods (deprecated — superseded by `suppression/*`)

The reference still lists these under "Obsolete Methods":
- `unsubscribed/set.json`
- `unsubscribed/check.json`
- `unsubscribed/list.json`

Use the `suppression/*` methods instead.

---

## 9. Quick Enum Reference

| Concept | Allowed values |
|---|---|
| `template_engine` / `X-UNIONE-Template-Engine` | `simple` (default), `velocity`, `liquid`, `none` |
| `global_language` / `X-UNIONE-Global-Language` | `be`, `de`, `en`, `es`, `fr`, `it`, `pl`, `pt`, `ru`, `ua`, `kz` |
| `editor_type` (template) | `html` (default), `visual` |
| webhook `status` | `active` (default), `disabled`, `stopped` |
| webhook `event_format` | `json_post` (default), `json_post_gzip` |
| webhook `email_status` events | `accepted`, `sent`, `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam` |
| webhook `spam_block` | single element `"*"` |
| webhook `event_name` | `transactional_email_status`, `transactional_spam_block` |
| suppression `cause` | `unsubscribed`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` |
| suppression `source` | `user`, `system`, `subscriber` |
| email validation `result` | `valid`, `invalid`, `suspicious`, `unknown` |
| email validation `cause` | `no_mx_record`, `syntax_error`, `possible_typo`, `mailbox_not_found`, `global_suppression`, `disposable`, `role`, `abuse`, `spamtrap`, `smtp_connection_failed` |
| event-dump `format` | `csv` (default), `csv_gzip` |
| event-dump `delimiter` | `,` (default), `;` |
| event-dump `aggregate` | `day_status`, `""` (empty/default) |
| event-dump `status` (filter) | `accepted`, `sent`, `delivered`, `opened`, `clicked`, `unsubscribed`, `subscribed`, `soft_bounced`, `hard_bounced`, `spam` |
| event-dump `dump_status` | `queued`, `in_process`, `ready`, `failed` |
| project `email_counter_mode` | `default`, `permanent` |
| `failed_emails` values (email/send) | `unsubscribed`, `invalid`, `duplicate`, `temporary_unavailable`, `permanent_unavailable`, `complained`, `blocked` |

---

*Document generated from the static HTML of the UniOne Web API v1.87 reference. The "Interactive API Request" widget at the bottom of the page is JS-rendered and contains no additional parameter documentation.*
