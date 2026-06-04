---
title: Velocity Template Engine
source: https://docs.unione.io/en/velocity-template-engine
synced: 2026-06-04
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
