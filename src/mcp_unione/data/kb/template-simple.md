---
title: Simple Template Engine
source: https://docs.unione.io/en/simple-template-engine
synced: 2026-06-04
---

## 0. Overview — How an engine is selected

From the **template-engines** overview page:

> Each email sent with `email/send` method or each template referenced by group
> of template methods is using one of the **two supported template engines**:
>
> - **Simple template engine**: substitutes within double curly braces.
> - **Velocity template engine**: more sophisticated template processor.
>
> Templates allow send emails faster and make them more personalized, so take
> your chance to learn their abilities.

The overview page lists only two engines, but **Liquid** is a third, newer
engine documented on its own page and selectable via `template_engine: "liquid"`.

### `template_engine` parameter

Selected via the `template_engine` field in the `message` object of `email/send`
(and inside the `X-UNIONE` JSON header for the SMTP API). From the SMTP-API
parameter table:

| Name | Type | Description |
|------|------|-------------|
| `template_engine` | Optional string | Sets the template engine for handling the substitutions. Accepts values: `"simple"` and `"velocity"`. If the parameter is not passed, the system will use the default value — `"simple"` |
| `template_id` | Optional string | Optional identifier of the template that had been created by `template/set` method or in UniOne web interface. |
| `global_substitutions` | Optional object | Object for passing the substitutions (e.g., first name of recipient). |
| `global_metadata` | Optional object | Object for passing the metadata. |
| `global_language` | Optional string | Language used for unsubscribe footer and unsubscribe page interface. `"en"` by default. Supported languages: `be, de, en, es, fr, it, pl, pt, ru, kz, ua`. |

Accepted values in practice:

- `"simple"` (default if the field is omitted)
- `"velocity"`
- `"liquid"` (documented on the Liquid page; example request uses `"template_engine": "liquid"`)
- `"none"` — fully disables the template engine (see below)

**Disabling the engine** — from the API changelog (Oct 18, 2022, v.1.38):

> If you are allowed to disable the Unsubscribe link, you may fully disable the
> template engine by specifying `"template_engine":"none"` in `email/send` or
> SMTP call.

### How substitutions map: `global_substitutions` vs per-recipient `substitutions`

Two places provide the data fields referenced by templates:

- **`substitutions`** — set **per recipient** (inside each entry of the
  `recipients` array of `email/send`). These are unique to that addressee.
- **`global_substitutions`** — set **once for the whole message**
  (`email/send` and `template/set`). Applied to every recipient.

From the docs (cc-and-bcc / sending notes):

> It is important to keep in mind that **substitutions in a letter can be
> different for each recipient**. If you want all addressees to receive the same
> text, either use the same substitutions for each one, or use the
> `global_substitutions` parameter instead of personal substitutions.

> Links for tracking email opens and clicks, as well as the unsubscribe link,
> will always be unique for each recipient.

Practical mapping rules:

- Per-recipient `substitutions` are merged with `global_substitutions`;
  per-recipient values are what make each email personalized.
- For `template/set` (stored templates) only `global_substitutions` is available
  (there is no recipient array at template definition time); per-recipient
  `substitutions` are supplied later when the template is used in `email/send`.

### Where substitutions can be used (which fields are templated)

This list is the same for **all three** engines (from each engine's page):

- `body.html`
- `body.plaintext`
- `body.amp`
- `subject`
- `headers`
- `options.unsubscribe_url`
- `from_name`

(Methods: `email/send` and `template/set`.)

---

## 1. Simple Template Engine

Page: https://docs.unione.io/en/simple-template-engine
`template_engine`: `"simple"` (this is the **default** when the field is omitted)

> This template engine substitutes data fields surrounded by double curly braces.
> For example, if you have recipient's name in `Name` field you can use this
> expression: `{{Name}}`.
>
> There are a couple of extra possibilities also (**they do not work inside
> links** though):

### 1.1 Basic variable substitution

```
{{Name}}
```

Replaced by the value of the field `Name`.

### 1.2 Default value (fallback) — `{{Field|default}}`

| HTML example | Description |
|--------------|-------------|
| `{{Name\|Dear Subscriber}}` | This tag will be replaced by the value of the field "Name", and if "Name" is empty, it will be replaced by «Dear Subscriber» as if it was a «default value» of the field. Instead of the text, you can specify the name of another field, for example: `{{Name\|{{Email}}}}` |

So:

```
{{Name|Dear Subscriber}}      → value of Name, else "Dear Subscriber"
{{Name|{{Email}}}}            → value of Name, else value of Email
```

The part after `|` is the default; it may be literal text **or** a nested
substitution referencing another field.

### 1.3 Conditional output — `{{Field?text}}`

| HTML example | Description |
|--------------|-------------|
| `{{HasOrders?You have 10% discount}}` | If the field "Has Orders" is not empty and not equals zero, it will be replaced by the text «You have 10% discount», otherwise the result will be an empty string. Instead of the text you can specify the name of another field, for example: `{{HasOrders?{{Discount}}}}` |

So:

```
{{HasOrders?You have 10% discount}}   → text if HasOrders is non-empty and ≠ 0, else ""
{{HasOrders?{{Discount}}}}            → value of Discount if HasOrders truthy, else ""
```

The text after `?` may be literal **or** a nested substitution.

**Truthiness rule (Simple engine):** a field is considered "set" / true when it
is **not empty and not equal to zero**.

### 1.4 Combined example (verbatim)

> Look at more complicated example, which adds comma before the name, but only if
> name is not empty:

```
Congratulations{{Name?, }}{{Name}}!
```

- `{{Name?, }}` → outputs `", "` only if `Name` is non-empty, else nothing.
- `{{Name}}` → outputs the name.
- Result with `Name="John"` → `Congratulations, John!`
- Result with empty `Name` → `Congratulations!`

### 1.5 Rules / limitations (Simple)

- Syntax is **double curly braces**: `{{FieldName}}`.
- Two extra operators: default `|` and conditional `?`. Both accept either
  literal text or a nested `{{...}}` field reference.
- **The `|` and `?` extras do NOT work inside links** (per the docs). Plain
  `{{Field}}` substitution does work elsewhere.
- Missing / empty variable:
  - Plain `{{Field}}` → replaced with empty string (the value, which is empty).
  - `{{Field|default}}` → replaced with the default.
  - `{{Field?text}}` → empty string when the field is empty or zero.
- Allowed characters in variable names: the docs use plain identifiers
  (`Name`, `Email`, `HasOrders`, `Discount`). Field names mirror the keys in the
  `substitutions` / `global_substitutions` object. (The docs do not publish a
  formal grammar for allowed characters; examples use alphanumeric field names.)
- The Simple engine substitutes **flat fields**; it does not iterate arrays or
  evaluate objects/loops (use Velocity or Liquid for that).

### 1.6 Reserved/system variable (Simple)

Unsubscribe URL — insert anywhere in the body:

```html
<a href="{{UnsubscribeUrl}}">Unsubscribe</a>
```

(From the unsubscribe-link page: "For a Simple template engine, the link is
inserted in the following way: `<a href="{{UnsubscribeUrl}}">Unsubscribe</a>`.")

---
