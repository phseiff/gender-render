<p align="center"><!--<a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>-->
<img src="https://phseiff.com/gender-render/docs/images/title.svg" alt="{gender*render}"></p>

<p align="center" color="violet">Template-system for rendering gender-neutral text- and email-templates properly gendered and with the correct pronouns of all people involved.</p>

Ever had the struggle of correctly gendering people in your automated emails? Are you sick of writing email templates that are unsupportive of non-binary people, gender everyone with ugly underscores, or clumsily avoid pronouns alltogether, costing you hours of work to frickle them together? With gender\*render, you can write easy, gender-neutral templates for your emails, and automatically render them into correctly gendered emails, given the pronouns and names of all people concerned! [[Jump to quickstart]](#quick-start-)

[![to quickstart](https://phseiff.com/gender-render/docs/images/idea-illustration.svg)](#example-usages)

Gender\*render is not only a piece of software that can definitely come in handy if you want to write progressive automated emails, but also a proof of concept. Many people say that correctly gendering non-binary people, people with unusual pronouns, or people with no pronouns at all in automated fashions is impossible. And many live by said premise. gender\*render as a concept is supposed to be a proof that this is simply false, and that any such claims come from a mixture of missing will and laziness, with technical limitations merely being a pretext. Gender\*render comes with an in-depth specification, so you can easily implement it in any language of your choice, port it to other (human) languages or read about the thoughts behind this project! [[Download spec]](https://github.com/phseiff/gender-render/raw/main/docs/spec.pdf)

[![download spec](https://phseiff.com/gender-render/docs/images/download-spec.svg)](https://phseiff.com/gender-render/spec.pdf)

## Advantages/Features

Using gender\*render offers a set of advantages over traditional "one for men and one for women"-email templates:

* **Supportive**: Supports addressing one or multiple people in your texts, talking about them in the first as well as second person and multiple grammatical contexts, supports addressing people with no preferred way of addressing, supports preferences regarding noun gendering, supports neo-pronouns.

* **Easy**: Easy enough for non-tech people to write templates with it - writing one template for all genders with gender*render may actually be easier than writing two templates for two genders.

* **Slim & Handy**: gender*render doesn't get into your way and doesn't cluster up your template with syntax for things you don't need right now.

* **Portable**: Comes as a python-module, but with a full specification that encourages re-implementation in different languages.

* **Reliable**: Tested with 100% code- and branch coverage and a more than 2:1 testing code to actual code ratio.

* **Well-documented**: Written with inspiration from literate programming, gender*render comes with a specification with in-depth elaboration on the underlying concepts, as well as full documentation of all methods and an introduction and getting started guide.

If your web forms ask your customers for their pronoun preferences instead of their gender, preferably with text entry boxes instead of dropdowns, and you have these pronoun information in a nice data base, you can easily automate the process of correctly gendering your emails based on the person they are directed to.

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

**Template**:

Addressing one person:

```
Dear {Mr_s Doe},
Yesterday, I was asked about your
wellbeing, "Is there reason to worry
about {them}?", and I told the
person who asked that [...]
```

**Pronoun Data**

```json
{
    "address": "Mrs",
    "family-name": "Smith",
    "object": "her"
}
```

Having more value in the pronoun data than needed is, of course, also allowed!

</td><td>

```
Dear Mrs Smith,
Yesterday, I was asked about your
wellbeing, "Is there reason to worry
about her?", and I told the
person who asked that [...]
```

</td></tr>
<tr><td>

**Template**:

Addressing multiple persons:

```
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

**Pronoun Data**:

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

```
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

**Template**:

gender*render doesn't get into your way, since you can fuse any sequence of tags into one tag:

```
"{Mr_s} {Doe}"

equals

"{Mr_s Doe}".
```

**Pronoun Data**:

```json
{
  "address": "Ind.",
  "name": "Abrams"
}
```

</td><td>

```
Ind. Abrams

equals

Ind. Adams
```

</td></tr>
<tr><td>

**Template**:

Address individuals who don't want to get a special title:

```
Dear {Mr_s Doe},
[...]
```

**Pronoun Data**:

```json
{
  "gender-addressing": "false",
  "name": "Chase",
  "first-name": "Joey"
}
```

</td><td>

```
Dear Joey Chase,
[...]
```

</td></tr>
<tr><td>

**Template**:

Refer to individuals with hyponyms for person or by their profession:

```
I hope the {actor} is doing well.
```

**Pronoun Data**:

```json
{
  "gender-nouns": "female"
}
```

Available values are "male", "female" and "neutral".

</td><td>

```
I hope the actress is doing well.
```

Note that this also works for words that start with capital letters - "Actor" would've been gendered as "Actress"!

</td></tr>
<tr><td>

**Template**:

*Every* gendered noun has a neutral version available:

```
As a {salesman}, {they} had to face
great hardships!
```

**Pronoun Data**:

```json
{
  "subject": "they",
  "gender-nouns": "neutral"
}
```

"neutral" is also the default value.

</td><td>

```
As a salesperson, they had to face
great hardships!
```

</td></tr>
<tr><td>

**Template**:

If a noun has no explicit specific version for a grammatical gender, the neutral version of the noun is used:

```
Since tuesday, {they} serve as a
{cadet}.
```

**Pronoun Data**:

```json
{
  "subject": "they",
  "gender-nouns": "female"
}
```

</td><td>

```
Since tuesday, they serve as a
cadet.
```

</td></tr>
</table>

## GitHub badges

### Implementation

attribute    | value
-------------|-----------------------------
PyPi | [![PyPI download total](https://img.shields.io/pypi/dm/gender-render.svg)](https://pypi.python.org/pypi/gh-md-to-html/) [![PyPI version](https://img.shields.io/pypi/v/gender-render.svg)](https://pypi.python.org/pypi/gh-md-to-html/) ![PyPI pyversions](https://img.shields.io/pypi/pyversions/gender-render.svg)
license | [![implementation license](https://img.shields.io/badge/license-MIT-lightgreen)](https://github.com/phseiff/gender-render/blob/master/LICENSE-implementation.txt)
maintenance | [![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render) [![Percentage of issues still open](http://isitmaintained.com/badge/open/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render)
tests | ![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen) ![vulture](https://img.shields.io/badge/vulture-100%25-brightgreen)
documentation | ![here](https://img.shields.io/badge/documentation-here%20%F0%9F%94%97-lightblue)
build | ![build](https://github.com/phseiff/gender-render/workflows/Build/badge.svg)

### Specification

attribute    | value
-------------|-----------------------------
license | [![implementation license](https://img.shields.io/badge/license-ToDo-lightgreen)](https://github.com/phseiff/gender-render/blob/master/LICENSE-specification.txt)
download latest | ToDo
download page | ToDo


## License

Specification and implementation are licensed separately.
For the specification, see [here](LICENSE-specification.txt).
For the implementation, see [here](LICENSE-implementation.txt).

## Development & Contributing

Active, and issues as well as pre-discussed pull requests are welcome.
See [here](CONTRIBUTING.md) for additional information.

## Code of Conduct

In general, be decent and don't put shame on the 21st century.
See [here](CODE-OF-CONDUCT.md) for additional information.
