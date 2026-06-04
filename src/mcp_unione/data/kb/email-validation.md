---
title: Email Validation
source: https://docs.unione.io/en/email-validation
synced: 2026-06-04
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
