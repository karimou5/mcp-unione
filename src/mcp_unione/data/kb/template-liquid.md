---
title: Liquid Template Engine
source: https://docs.unione.io/en/liquid-template-engine
synced: 2026-06-04
---

## 3. Liquid Template Engine

Page: https://docs.unione.io/en/liquid-template-engine
`template_engine`: `"liquid"`
Liquid is the templating language developed by Shopify.

> Liquid is a templating language developed by Shopify. It's designed to work
> with objects and substitution arrays using loops, conditionals, and filters.
> This makes it easy to create flexible email templates that are automatically
> populated with dynamic data passed in the payload of the `email/send` and
> `template/set` methods. Using advanced substitution logic also helps reduce
> template size, speeds up request processing, and allows for more adaptable
> email campaigns with minimal effort.

> Substitution variables can be used in the following parameters of the
> `email/send` and `template/set` methods: `body.html`, `body.plaintext`,
> `body.amp`, `subject`, `headers`, `from_name`, `options.unsubscribe_url`.

### 3.1 Syntax basics

- **Objects / output**: `{{ ... }}` — e.g. `{{ person.name }}`
- **Tags / logic**: `{% ... %}` — e.g. `{% for ... %}`, `{% if ... %}`
- **Filters**: pipe inside an output tag — `{{ value | filter: args }}`

### 3.2 Liquid Use Cases (verbatim from the page)

#### 1. Accessing Nested Objects

> You can reference nested variables inside substitution objects. This is
> especially useful for structured data like user info, order details,
> addresses, etc.

Request (`global_substitutions` for `email/send` and `template/set`, or
`substitutions` for `email/send`):

```json
{
  "substitutions": {
    "person": {
      "name": "John",
      "secondName": "Doe",
      "age": "26"
    }
  }
}
```

Template:

```
"html": "<p>Hello, {{ person.name }} {{ person.secondName }}!</p>"
```

#### 2. Loops: Rendering Arrays

> Loops allow you to dynamically output lists – e.g., items in an order,
> recommendations, event attendees, survey answers, etc.

Request data containing an array:

```json
"substitutions": {
  "products": [
    {
      "title": "Samsung Galaxy A53",
      "price": "320$"
    },
    {
      "title": "Xiaomi Redmi Note 12",
      "price": "270$"
    },
    {
      "title": "Motorola G82",
      "price": "250$"
    }
  ]
}
```

Template:

```liquid
<ul>
  {% for product in products %}
    <li>
      {{ forloop.index }}. {{ product.title }} – {{ product.price }}
    </li>
  {% endfor %}
</ul>
```

(`forloop.index` — the current 1-based loop index object.)

#### 3. Generating Link Lists

> Use Liquid to add dynamic links based on user data, product names, IDs, and
> more – ideal for buttons, catalogs, and listings.

Request:

```json
"substitutions": {
  "products": [
    {
      "title": "Samsung Galaxy A53",
      "url": "https://shop.example.com/samsung-galaxy-a53"
    },
    {
      "title": "Xiaomi Redmi Note 12",
      "url": "https://shop.example.com/redmi-note-12"
    },
    {
      "title": "Motorola G82",
      "url": "https://shop.example.com/motorola-g82"
    }
  ]
}
```

Template:

```liquid
<ul>
  {% for product in products %}
    <li>
      <a href="{{ product.url }}">
        {{ product.title }}
      </a>
    </li>
  {% endfor %}
</ul>
```

#### 4. Conditional Statements

> Conditionals let you render different blocks of content depending on variable
> values. For example, you can show a custom greeting to new users or offer
> discounts to returning customers.

Request:

```json
{
  "substitutions": {
    "user": {
      "is_new": true
    }
  }
}
```

Template:

```liquid
{% if user.is_new %}
  Welcome!
{% else %}
  Glad to have you back!
{% endif %}
```

#### 5. Filters

> Filters let you format data right within the template – change text case, add
> prefixes, replacing strings, or format numbers and dates.

| Filter | JSON Data | Template Code | Rendered Output |
|--------|-----------|---------------|-----------------|
| `capitalize` (converts first letter to uppercase) | `{ "name": "ann" }` | `Hello, {{ Trigger.name \| capitalize }}!` | `Hello, Ann!` |
| `upcase` (converts the string to uppercase) | `{ "promo": "JULY2025" }` | `Promo code: {{ Trigger.promo \| upcase }}` | `Promo code: JULY2025` |
| `downcase` (converts the string to lowercase) | `{ "promo": "JULY2025" }` | `Promo code: {{ Trigger.promo \| downcase }}` | `Promo code: july2025` |
| `replace` (replaces a substring with new value) | `{ "phone": "(555) 012-34-56" }` | `Phone: {{ Trigger.phone \| replace: "(555)", "+1 (555)" }}` | `Phone: +1 (555) 012-34-56` |
| `default` (sets the default value) | `{ "name": "" }` | `Hi, {{ Trigger.name \| default: "customer" }}!` | `Hi, customer!` |
| `date` (formats date) | `{ "delivery_date": "2025-05-01" }` | `Delivery date: {{ Trigger.delivery_date \| date: "%d.%m.%Y" }}` | `Delivery date: 01.05.2025` |

The documented filter list is therefore: **`capitalize`, `upcase`, `downcase`,
`replace`, `default`, `date`** (plus the full standard Liquid filter set — the
page points to Shopify's official Liquid documentation for more).

Note: the filter examples reference data under a `Trigger.` object (e.g.
`{{ Trigger.name | capitalize }}`), i.e. the substitution keys nest under a
`Trigger` object in those examples.

### 3.3 Objects / tags / filters summary (Liquid)

- **Objects**: nested substitution objects (`person.name`), arrays (`products`),
  loop object `forloop` (`forloop.index`).
- **Tags**: `{% for x in collection %} ... {% endfor %}`,
  `{% if cond %} ... {% else %} ... {% endif %}`. (Full standard Liquid tag set
  applies — UniOne defers to Shopify docs.)
- **Filters**: documented `capitalize`, `upcase`, `downcase`, `replace`,
  `default`, `date` (+ standard Liquid filters).

### 3.4 Full example: `email/send` request using a Liquid template

> Below is a complete working example of a request:

```json
{
  "api_key": "KEY",
  "message": {
    "template_engine": "liquid",
    "body": {
      "html": "<h1>Hello, {{ user.name }}!</h1><p>Your selected {{ lookingfor.deviceType }}: {{ lookingfor.screenResolution }}, {{ lookingfor.ram }} RAM.</p>{% for product in products %}<div><a href='{{ product.url }}'>{{ product.title }}</a> — {{ product.price }}</div>{% endfor %}"
    },
    "subject": "Your Recommendations",
    "from_email": "sender@mail.com",
    "from_name": "SENDER_EMAIL",
    "recipients": [
      {
        "email": "recipient@mail.com",
        "substitutions": {
          "user": { "name": "John" },
          "lookingfor": {
            "deviceType": "tablet",
            "screenResolution": "1920x1080",
            "ram": "4GB"
          },
          "products": [
            {
              "title": "Amazon Tablet",
              "price": "$50",
              "url": "https://..."
            }
          ]
        }
      }
    ]
  }
}
```

> For more details on Liquid, check out Shopify's official Liquid documentation.

### 3.5 Reserved/system variable (Liquid)

The unsubscribe-link page only documents `{{UnsubscribeUrl}}` (Simple) and
`$UnsubscribeUrl` (Velocity). Because Liquid uses the same `{{ ... }}` output
syntax as the Simple engine, use the Liquid-output form
`{{ options.unsubscribe_url }}` / set `options.unsubscribe_url` for custom
unsubscribe links. (The Liquid page lists `options.unsubscribe_url` as a
templated parameter.)

---

## 4. Special / reserved substitution variables & system substitutions

| Variable | Engine | Form | Purpose |
|----------|--------|------|---------|
| `UnsubscribeUrl` | Simple | `{{UnsubscribeUrl}}` | UniOne-generated unsubscribe link, unique per recipient |
| `UnsubscribeUrl` | Velocity | `$UnsubscribeUrl` | Same, Velocity reference form |
| `options.unsubscribe_url` | all | parameter | Sets the `List-Unsubscribe` header value / custom unsubscribe URL (also templatable) |

Other system behaviors (from the unsubscribe-link page):

- UniOne **appends an unsubscribe block to every email** by default (footer +
  `List-Unsubscribe` header). You can place the link yourself in the body using
  the engine-specific form above and then disable the default footer.
- Footer/page language is set by the API call URI or `global_language` in the
  `X-UNIONE` header (SMTP). Supported: `be, de, en, es, fr, it, pl, pt, ru, ua`
  (the SMTP parameter table additionally lists `kz`).
- `skip_unsubscribe` parameter (in `email/send` or `X-UNIONE` header) removes the
  unsubscribe footer and `List-Unsubscribe` header on a per-email basis
  (requires "dynamic disabling" enabled by support).
- `custom_unsubscribe_url_enabled` (via `project/create` / `project/update`)
  controls per-project unsubscribe-link injection.
- Tracking links and the unsubscribe link are **always unique per recipient**.

**Important:** the docs for these three engine pages do **not** define a
`to_name` / `to_email` reserved substitution. The only reserved/system
substitution documented is the unsubscribe URL. Date-typed fields in Velocity
must be prefixed with `date_` (system convention).

---

## 5. Differences, limitations & recommendations

### Quick comparison

| Capability | Simple | Velocity | Liquid |
|------------|:------:|:--------:|:------:|
| `template_engine` value | `"simple"` (default) | `"velocity"` | `"liquid"` |
| Variable output syntax | `{{Field}}` | `$ref` / `$obj.prop` | `{{ obj.prop }}` |
| Nested objects | No (flat fields) | Yes (`$person.name`) | Yes (`{{ person.name }}`) |
| Arrays / loops | No | Yes (`#foreach ... #end`) | Yes (`{% for ... %}{% endfor %}`) |
| Conditionals | Limited (`{{F?text}}`) | Yes (`#if/#elseif/#else/#end`) | Yes (`{% if/elsif/else/endif %}`) |
| Default value | `{{F\|default}}` | via `#if` | `\| default:` filter |
| Filters / transforms | No | Tools: `$esc.html/url`, `$dateFormat`, string methods | Standard Liquid filters (`capitalize`, `upcase`, `downcase`, `replace`, `default`, `date`, ...) |
| Date formatting | No | `$dateFormat.format(...)`, `date_` prefix required | `\| date: "..."` filter |
| Escaping helpers | No | `$esc.html`, `$esc.url` | Standard Liquid escaping filters |
| Index access in loops | No | `$arr.get(n)`, `$arr.indexOf($x)` | `forloop.index` |
| Unsubscribe var | `{{UnsubscribeUrl}}` | `$UnsubscribeUrl` | `options.unsubscribe_url` output |
| Works inside links | Plain `{{F}}` yes; `\|`/`?` extras NO | Yes | Yes |

### Engine-specific limitations

- **Simple**: no objects, no arrays/loops, no filters. Conditionals/defaults
  (`?`, `|`) **do not work inside links**. Truthiness = non-empty **and** ≠ 0.
  Best for flat per-recipient merge fields only.
- **Velocity**: full object/array/conditional/loop support and helper tools, but
  uses Apache Velocity `$`/`#` syntax (steeper learning curve). Date fields
  **must** be prefixed `date_`. UniOne references Apache Velocity 1.7.
- **Liquid**: object/array/conditional/loop support plus a rich, well-known
  filter ecosystem and `{{ }}`/`{% %}` syntax familiar from Shopify. UniOne
  documents a subset of filters and defers to Shopify's docs for the rest.
- **`none`**: disables templating entirely (raw body sent as-is); only available
  if unsubscribe-link disabling is permitted on the account.

### Recommendations

- Use **Simple** for straightforward personalization (name, single merge tags)
  where the request stays small and no logic is needed. It is the default.
- Use **Velocity** when you need object/array iteration, conditional rendering,
  date formatting, or escaping and you are comfortable with Velocity syntax —
  the documented engine for the rich "recommendations" style transactional email.
- Use **Liquid** for the most readable/maintainable dynamic templates with
  loops, conditionals, and filters, especially if your team already knows
  Shopify Liquid. It is the newest engine and the only one with a published
  filter table.
- For all engines, prefer `global_substitutions` for content shared across all
  recipients and per-recipient `substitutions` for personalized values — this
  keeps requests smaller and avoids repeating identical data.
- Always include an unsubscribe link (`{{UnsubscribeUrl}}` / `$UnsubscribeUrl` /
  `options.unsubscribe_url`) — anti-spam systems weigh its presence.
