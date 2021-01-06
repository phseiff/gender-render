## Quick Start 🚗💨

[Installation](#installation) • [Usage](#usage) • [Template Syntax](#template-syntax)

### Installation

```
pip3 install gender-render
```

### Usage

```python
import gender_render as gr

# use:
rendered_template_as_a_str = gr.render_template(
    template_as_a_string,
    pronoun_data_as_a_string_or_dict
)

# or:
rendered_template_as_a_str = gr.render_template(
    template_file_path,
    pronoun_data_file_path,
    takes_file_path=True
)
```

### Template Syntax

<table>
<tr>
<td> Template & Pronoun Data </td> <td> Result </td>
</tr>

<tr><td>

**Addressing one person**:

* Template:

```nohighlight
Dear {Mr_s Doe},
Yesterday, I was asked about your
wellbeing, "Is there reason to worry
about {them}?", and I told the
person who asked that [...]
```

* Pronoun Data:

```json
{
    "address": "Mrs",
    "family-name": "Smith",
    "object": "her"
}
```

Having more value in the pronoun data than needed is, of course, also allowed!

</td><td>

```nohighlight
Dear Mrs Smith,
Yesterday, I was asked about your
wellbeing, "Is there reason to worry
about her?", and I told the
person who asked that [...]
```

</td></tr>
<tr><td>

**Addressing multiple persons**:

* Template:


```nohighlight
Dear {seller* Mr_s Doe},

According to our guidelines, the
issue with {reseller* Mr_s Doe} is
best resolved if {reseller*they}
publically apologizes to
{buyer* Mr_s Doe} for {reseller*their}
behavior.

Best regards,
{customer_support* Jean Doe}
```

* Pronoun Data:

```json
{
 "seller": {
    "address": "Mrs",
    "name": "Brown"
  },
  "reseller": {
    "address": "Mr",
    "name": "Jones",
    "subject": "he",
    "dpossessive": "his"
  },
  "buyer": {
    "address": "Mx",
    "name": "Ainge"
  },
  "customer_support": {
    "first-name": "Emma",
    "name": "Ackernick"
  }
}
```

Note that all these attributes can take any value; not only "Mr" and "Mrs" is valid!

</td><td>

```nohighlight
Dear Mrs Brown,

According to our guidelines, the
issue with Mr Jones is
best resolved if he
publically apologizes to
Mx Ainge for his
behavior.

Best regards,
Emma Ackernick
```

</td></tr>
<tr><td>

**gender*render doesn't get into your way, since you can fuse any sequence of tags into one tag**:

* Template:

```nohighlight
"{Mr_s} {Doe}"

equals

"{Mr_s Doe}".
```

* Pronoun Data:

```json
{
  "address": "Ind.",
  "name": "Abrams"
}
```

</td><td>

```nohighlight
"Ind. Abrams"

equals

"Ind. Adams"
```

</td></tr>
<tr><td>

**Address individuals who don't want to get a special title**:

* Template:

```nohighlight
Dear {Mr_s Doe},
[...]
```

* Pronoun Data:

```json
{
  "gender-addressing": "false",
  "name": "Chase",
  "first-name": "Joey"
}
```

</td><td>

```nohighlight
Dear Joey Chase,
[...]
```

</td></tr>
<tr><td>

**Refer to individuals with hyponyms for person or by their profession**:

* Template:

```nohighlight
I hope the {actor} is doing well.
```

* Pronoun Data:

```json
{
  "gender-nouns": "female"
}
```

Available values are "male", "female" and "neutral".

</td><td>

```nohighlight
I hope the actress is doing well.
```

Note that this also works for words that start with capital letters - "Actor" would've been gendered as "Actress"!

</td></tr>
<tr><td>

***Every* gendered noun has a neutral version available**:

* Template:

```nohighlight
As a {salesman}, {they} had to face
great hardships!
```

* Pronoun Data:

```json
{
  "subject": "they",
  "gender-nouns": "neutral"
}
```

"neutral" is also the default value.

</td><td>

```nohighlight
As a salesperson, they had to face
great hardships!
```

</td></tr>
<tr><td>

**If a noun has no explicit specific version for a grammatical gender, the neutral version of the noun is used**:

* Template:

```nohighlight
Since tuesday, {they} serve as a
{cadet}.
```

* Pronoun Data:

```json
{
  "subject": "they",
  "gender-nouns": "female"
}
```

</td><td>

```nohighlight
Since tuesday, they serve as a
cadet.
```

</td></tr>
<tr></tr><td>

**Define your own properties**:

* Template:

```nohighlight
After {they} ate {their}
{<favorite_food>} like any
other {child}, {they} slept.
```

* Pronoun Data:

```json
{
  "subject": "ze",
  "dpossessive": "zen",
  "<favorite_food>": "spaghetti"
}
```

</td><td>

```noheighlight
After ze ate zen
spaghetti like any
other child, ze slept.
```

</td></tr>
</table>