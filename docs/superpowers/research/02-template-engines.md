# UniOne Email Template Engines — Exhaustive Reference

Research compiled from the official UniOne documentation:

- https://docs.unione.io/en/simple-template-engine
- https://docs.unione.io/en/velocity
- https://docs.unione.io/en/liquid-template-engine

Supporting pages used for substitution wiring and reserved variables:

- https://docs.unione.io/en/template-engines (overview)
- https://docs.unione.io/en/velocity-use-cases
- https://docs.unione.io/en/velocity-example
- https://docs.unione.io/en/unsubscribe-link
- https://docs.unione.io/en/smtp-api (X-UNIONE header parameters)

> Note on code examples below: the UniOne docs deliberately insert invisible
> spacing inside `{{ }}` in some of their HTML so the page itself is not parsed
> by the engine. Examples here are reproduced with the **real** intended syntax
> (no extra spaces inside braces), but otherwise verbatim.

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

## 2. Velocity Template Engine

Page: https://docs.unione.io/en/velocity
`template_engine`: `"velocity"`
Backed by **Apache Velocity** (UniOne references the Apache Velocity 1.7 user
guide).

> Apache Velocity template engine can handle objects and arrays substitutions
> using loops and if/else conditions. This will significantly reduce the time
> spent on the same letter templates development or development of the template
> parts. Using Velocity once is enough to create a pattern, which will be filled
> automatically by structured substitutions processed in the request. Depending
> on the conditions specified in the template, Velocity will handle
> substitutions, replacing the variables with the values or transforming their
> values by a given algorithm. Using complex substitutions (objects, arrays)
> will also reduce the size of requests, thereby increasing the processing speed,
> and speed up sending emails as a result.

> Using Velocity in UniOne allows you to use the substitutions with objects and
> arrays to create emails with dynamic content. This significantly reduces the
> size of the traffic and automates the process of creating templates with
> identical structures that differ only by the content.

### 2.1 References (variable syntax)

Velocity uses the **`$` reference** syntax (not curly braces):

- `$person.name` — property access on an object
- `$petList.get(0)` — method call
- `$UpperCASE.toString().toLowerCase()` — chained method calls

### 2.2 Directives

The UniOne Velocity use-cases page demonstrates these directives verbatim:

- `#foreach( $item in $collection ) ... #end` — iterate an array
- `#if( ... ) ... #elseif( ... ) ... #else ... #end` — conditionals
- (Standard Velocity also supports `#set`, `#macro`, and `##`/`#* *#` comments;
  UniOne's published examples focus on `#foreach` and `#if/#elseif/#else/#end`.)

### 2.3 Velocity use cases (verbatim from the page)

The page enumerates the supported use cases:

- Accessing the embedded object
- Array iteration (in embedded object / array)
- Call the Nth array element
- Access the index of the current array element
- Convert to lowercase
- URL and HTML escaping
- Date and time formatting
- if/else conditions

#### 2.3.1 Accessing an embedded object

> Allows you to access the variables found in the substitutions object.

Substitution example (parameter `global_substitutions` — `email/send`,
`template/set`; `substitutions` — `email/send`):

```json
...
"substitutions":
{
    "person":
    {
        "name":"John",
        "secondName":"Doe",
        "age":"26"
    }
}
```

Usage example (parameters `body.html`, `body.plaintext`, `body.amp`, `subject`,
`headers`, `options.unsubscribe_url`, `from_name`):

```
"html":"<h2>Hello, $person.name $person.secondName !</h2>"
```

#### 2.3.2 Array iteration (in embedded object / array)

> Returns and iterates the elements of the array of substitutions.

Substitution example:

```json
...
 "substitutions":
        {
          "petList":
            [
                {
                  "name":"John",
                  "price":"30"
                },
                {
                  "name":"Harold",
                  "price":"15"
                }
            ]
        }
```

Usage example:

```
"html":
 "#foreach( $pet in $petList )
    $pet.name for only $pet.price
 #end"
```

Nested iteration — substitution example:

```json
...
 "substitutions":
        {
          "DogsAndCats":
            [
              {
               "pet":
                 [
                  {
                   "concreteAnimal":"Brown Cat"
                  }
                 ]
              }
            ]
        }
```

Usage example:

```
"html":
"#foreach( $pet in $DogsAndCats)
  #foreach( $concreteAnimal in $pet.pet)
    Buy this $concreteAnimal.concreteAnimal
  #end
#end"
```

#### 2.3.3 Call the Nth array element

> Сalls the array element with a specified index.

Substitution example:

```json
...
 "substitutions":
        {
          "petList":
            [
                {
                  "name":"John",
                  "price":"30"
                }
            ]
        }
```

Usage example:

```
"html":
"$petList.get(0).get("name")"
```

#### 2.3.4 Access the index of the current array element

> Returns the current array index.

Substitution example:

```json
...
 "substitutions":
        {
          "catsArray":
            [
              "cat":"black"
            ]
        }
```

Usage example:

```
"html":
"#foreach( $cat in $catsArray )
  Index of $cat is  $catsArray.indexOf($cat)
#end"
```

#### 2.3.5 Convert to lowercase

> Converts the string to lowercase.

Substitution example:

```json
...
 "substitutions":
        {
          "UpperCASE":"TEST"
        }
```

Usage example:

```
"html":
"$UpperCASE.toString().toLowerCase()"
```

#### 2.3.6 URL and HTML escaping

> Replaces URL and HTML special characters with the correct entities.

Substitution example:

```json
...
 "substitutions":
        {
          "url": "hello here & there",
          "html_code":"\’bread\" & \"butter\’"
        }
```

Usage example:

```
"html":
"$esc.html($html_code)
$esc.url($url)"
```

- `$esc.html($var)` — HTML-escape
- `$esc.url($var)` — URL-escape

#### 2.3.7 Date and time formatting

> Returns the "date" data type in a convenient format for further usage.
>
> **Note:** the variables for substitutions of the "date" data type **should
> begin with `date_`** for correct processing, e.g. `date_Birthdate`.

Available date formats:

- `dd/mm/yyyy`
- `dd-mm-yyyy hh:mm:ss`
- `yyyy/mm/dd HH:mm:ss`
- `yyyy mm dd HH:mm:ss`
- ISO 8601 `2004-02-12T15:19:21+00:00`
- RFC 2822 `Thu, 21 Dec 2000 16:01:07 +0200`

Substitution example:

```json
...
 "substitutions":
        {
          "date_Birthdate":"01/01/1970"
        }
```

Usage example:

```
"html":
"$dateFormat.format('yyyy-M-d', $date_Birthdate)"
```

> `$dateFormat.format` changes the format of the passed date. The following
> formats are available:

```
 $date                                    -> Oct 19, 2003 9:54:50 PM
 $date.long                             -> October 19, 2003 9:54:50 PM PDT
 $date.medium_time                -> 9:54:50 PM
 $date.full_date                       -> Sunday, October 19, 2003
 $date.get('default','short')       -> Oct 19, 2003 9:54 PM
 $date.get('yyyy-M-d H:m:s')   -> 2003-10-19 21:54:50
```

#### 2.3.8 If/else conditions

> Allows you to insert if / else conditional statements into the email template.

Substitution example:

```json
...
 "substitutions":
        {
          "shoeSize":"5"
        }
```

Usage example:

```
"html":
"These shoes are
  #if( $shoeSize > 5 )
      too big
  #elseif( $shoeSize < 5 )
      too small
   #else
      just right
   #end
   for my brother."
```

### 2.4 Available context / built-in tools (Velocity)

UniOne exposes these helper objects in the Velocity context:

- `$esc` — escaping tool: `$esc.html(...)`, `$esc.url(...)`
- `$dateFormat` — date formatter: `$dateFormat.format('<pattern>', $date_var)`
- `$date` / `$date.long` / `$date.medium_time` / `$date.full_date` /
  `$date.get('default','short')` / `$date.get('<pattern>')` — date rendering
- Your own substitution keys become references (`$person`, `$petList`, ...).
- Array helper methods available on collections: `.get(n)`, `.indexOf($item)`.
- String methods on values: `.toString()`, `.toLowerCase()`.
- **Date variables must be prefixed `date_`** to be treated as dates.

### 2.5 Full worked example (`velocity-example` page)

Steps:

> **1. Create an email template.** First, create the email body without
> substitutions in order to have an idea of the final design of the letter in
> the recipient's inbox.
>
> **2. Create the substitution structure.** The substitutions can be set in the
> parameters `substitutions` and `global_substitutions` of `email/send`, or in
> the parameter `global_substitutions` of `template/set`.
>
> **3. Create `email/send` request.** Replace the changing content in body and
> other parameters by the substitutions using use cases.

Request body, `email/send` (key fields reproduced verbatim; long inline HTML
abbreviated where marked but template references kept intact):

```json
{
  "api_key": "KEY",
  "message":
  {
    "template_engine" : "velocity",
    "body":
    {
      "html": "...<span ...>Your promo code: $trigger.promocode</span>...Hello<a href=\"#\" ...> $user.name.</a>...You have been looking for a $lookingfor.deviceType with $lookingfor.screenResolution display, $lookingfor.ppi ppi, $lookingfor.ram RAM. ...Our managers will help you to make the right choice by phone: $trigger.deliverytelephone. ...Your $trigger.discount promo code: <span ...>$trigger.promocode</span>...The discount is valid till $dateFormat.format('full_date', $date_exptime)...#foreach( $product in $products ) ...<a href=\"$product.url\"><img src=\"$product.imgUrl\" width=\"130\"/></a>...<a href=\"$product.url\" ...>$product.title</a>...$product.price...$product.description...#end ...Unsubscribe..."
    },
    "subject": "Recommendations",
    "from_email": "sender@mail.com",
    "from_name": "SENDER",
    "recipients": [
      {
        "email": "recipient@mail.com",
        "substitutions":
        {
          "date_exptime":"15/09/2017",
          "user":
          {
            "name":"John"
          },
          "trigger":
          {
            "promocode":"SUPERFREE1000",
            "deliverytelephone":"+1031341553356",
            "discount":"-5%"
          },
          "lookingfor":
          {
            "deviceType":"tablet",
            "screenResolution":"1920 X 1080",
            "ppi":"326",
            "ram":"2GB"
          },
          "products":
          [
              {
                "title":"Amazon Tablet",
                "price":"50$",
                "description":"One of the best tablets for such a low price. ...",
                "imgUrl":"https://unisenderfiles.storage.unisender.com/KBpictures/UniOne/amazonkindlefire.jpg",
                "url":"#"
              },
              {
                "title":"Lenovo Tablet",
                "price":"75$",
                "description":"One of the most stylish tablets on the market. ...",
                "imgUrl":"https://unisenderfiles.storage.unisender.com/KBpictures/UniOne/lenovo.png",
                "url":""
              },
              {
                "title":"Asus Tablet",
                "price":"100$",
                "description":"One of the most handy tablets on the market. ...",
                "imgUrl":"https://unisenderfiles.storage.unisender.com/KBpictures/UniOne/P_500.jpg",
                "url":"#"
              }
          ]
        }
      }
    ]
  }
}
```

Note in the example: the date substitution key is `date_exptime` (prefixed
`date_`) and is rendered via `$dateFormat.format('full_date', $date_exptime)`.

### 2.6 Reserved/system variable (Velocity)

Unsubscribe URL (note: `$` reference form, **no** curly braces):

```html
<a href="$UnsubscribeUrl">Unsubscribe</a>
```

(From the unsubscribe-link page: "For a Velocity template engine, the proper
format is: `<a href="$UnsubscribeUrl">Unsubscribe</a>`.")

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
