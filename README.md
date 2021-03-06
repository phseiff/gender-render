<p align="center"><!--<a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>-->
<img src="https://phseiff.com/gender-render/docs/images/title.svg" alt="{gender*render}"></p>

<p align="center" color="violet">Template-system for rendering gender-neutral text-, email- and RPG-text-templates properly gendered and with the correct pronouns of all people involved.</p>

Ever had the struggle of correctly gendering people in your automated emails? Are you sick of writing email templates that are unsupportive of non-binary people, gender everyone with ugly underscores, or clumsily avoid pronouns alltogether, costing you hours of work to frickle them together? With gender\*render, you can write easy, gender-neutral templates for your emails, and automatically render them into correctly gendered emails, given the pronouns and names of all people concerned! [[Jump to quickstart]](#quick-start-)

[![to quickstart](https://phseiff.com/gender-render/docs/images/idea-illustration.svg)](#quick-start-)

Gender\*render is not only a piece of software that can definitely come in handy if you want to write progressive automated emails, but also a proof of concept. Many people say that correctly gendering non-binary people, people with unusual pronouns, or people with no pronouns at all in automated fashions is impossible. And many live by said premise. gender\*render as a concept is supposed to be a proof that this is simply false, and that any such claims come from a mixture of missing will and laziness, with technical limitations merely being a pretext. Gender\*render comes with an in-depth specification, so you can easily implement it in any language of your choice, port it to other (human) languages or read about the thoughts behind this project! [[Download spec]](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf) [[other versions & changelog]](#download-specifications--changelog)

[![download spec](https://phseiff.com/gender-render/docs/images/download-spec.svg)](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf)

## Advantages/Features

Using gender\*render offers a set of advantages over traditional "one for men and one for women"-email templates:

* **Supportive**: Supports addressing one or multiple people in your texts, talking about them in the first as well as second person and multiple grammatical contexts, supports addressing people with no preferred way of addressing, supports preferences regarding noun gendering, supports neo-pronouns.

* **Easy**: Easy enough for non-tech people to write templates with it - writing one template for all genders with gender*render may actually be easier than writing two templates for two genders.

* **Slim & Handy**: gender*render doesn't get into your way and doesn't cluster up your template with syntax for things you don't need right now.

* **Portable**: Comes as a python-module, but with a full specification that encourages re-implementation in different languages.

* **Reliable**: Tested with 100% code- and branch coverage and a more than 2:1 testing code to actual code ratio.

* **Well-documented**: Written with inspiration from literate programming, gender*render comes with a specification with in-depth elaboration on the underlying concepts, as well as full documentation of all methods, and a getting started guide.

If your web forms ask your customers for their pronoun preferences instead of their gender, preferably with text entry boxes instead of dropdowns, and you have these pronoun information in a nice data base, you can easily automate the process of correctly gendering your emails based on the person they are directed to.

## Content 📖

0. [Introduction](#top)
1. [Advantages & Features](#advantagesfeatures)
2. [Content](#content-) <-- you are here
3. [Quick start](#quick-start-)
4. [Spec downloads & changelog](#download-specifications--changelog)
5. [stats & links](#github-badges)
6. [Mission Statement](#mission-statement-)
7. [License](#license)
8. [Development & Contributing](#development--contributing)
9. [Code of Conduct](#code-of-conduct)

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

<tr></tr>
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
<tr></tr>
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
<tr></tr>
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
<tr></tr>
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
<tr></tr>
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
<tr></tr>
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
<tr></tr>
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
<tr></tr>
<tr><td>

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

## Download Specifications & Changelog

gender\*render follows a strict set of easily implementable specifications.
The implementations explain in-depth which design decision was taken why and how gender\*render works exactly, but also define guidelines for re-implementing gender\*render for different programming- and well as natural languages, and contain various findings and ideas/ concepts on how to deal with various aspects of grammatical gender and automated gendering in a technical context, some of whom might help you in writing related or similar tools.

There is one main specification ("spec"), as well as several extensions specifications ("ext-...").
To get started, you can download the [main specification](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf), which dives further into the versioning scheme of gender\*render specifications, their vision and development model, or download any specification in any version from the following list.

Clicking a version number downloads the specification as a pdf file, whilst the <sup>[html<img alt="↗" src="docs/images/external-link-black.svg" height="10em">]</sup>-link next to every specification version leads to a hosted html version of the specification.

* spec:
  * [download latest](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf)
  * [v0.6.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.6.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.6.0.html)</sup> - Add capitalization system, suggest error hierarchy, list implementation-specific warnings.
  * [v0.5.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.5.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.5.0.html)</sup> - Add instructions for word splitting for ungendered-word-warnings to the specification.
  * [v0.4.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.4.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.4.0.html)</sup> - Change "gripd" to "idpd".
  * [v0.3.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.3.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.3.0.html)</sup> - Extend on how to determine whether an implementation follows the standard or not regarding the extension specs.
  * [v0.2.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.2.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.2.0.html)</sup> - Add the concept of canonical context values and direct-mapped context values to the specification.
  * [v0.1.1](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.1.1.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.1.1.html)</sup> - Mention RGB-dialogues as a possible use case.
  * [v0.1.0](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.1.0.pdf)
    <sup>[[html<img alt="↗" src="docs/images/external-link-blue.svg" height="10em">]](https://phseiff.com/gender-render/docs/specs/spec/spec-v0.1.0.html)</sup> - Initial release



## GitHub badges

### Implementation

attribute    | value
-------------|-----------------------------
PyPi | [![PyPI download total](https://img.shields.io/pypi/dm/gender-render.svg)](https://pypi.python.org/pypi/gender-render/) [![PyPI version](https://img.shields.io/pypi/v/gender-render.svg)](https://pypi.python.org/pypi/gender-render/) ![PyPI pyversions](https://img.shields.io/pypi/pyversions/gender-render.svg)
license | [![implementation license](https://img.shields.io/badge/license-MIT-lightgreen)](https://github.com/phseiff/gender-render/blob/main/LICENSE-implementation.txt)
maintenance | [![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render) [![Percentage of issues still open](http://isitmaintained.com/badge/open/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render)
tests |[![codecov](https://codecov.io/gh/phseiff/gender-render/branch/main/graph/badge.svg?token=HWQ4PNEHB1)](https://codecov.io/gh/phseiff/gender-render) [![vulture](https://img.shields.io/badge/vulture-100%25-brightgreen)](https://github.com/phseiff/gender-render/blob/main/.github/workflows/build-and-test-code.yml)
documentation | [![here](https://img.shields.io/badge/documentation-here%20%F0%9F%94%97-lightblue)](https://phseiff.com/gender-render)
build | [![build](https://github.com/phseiff/gender-render/workflows/Build/badge.svg)](https://github.com/phseiff/gender-render/blob/main/.github/workflows/build-and-test-code.yml)

### Specification

attribute    | value
-------------|-----------------------------
license | [![implementation license](https://img.shields.io/badge/license-OWFa%201.0-lightgreen)](https://github.com/phseiff/gender-render/blob/main/LICENSE-specification.txt)
download latest | [![dowload](https://img.shields.io/badge/download-here-brightgreen)](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf)
other downloads | [![here](https://img.shields.io/badge/dowloads-here%20%F0%9F%94%97-lightblue)](#download-specifications--changelog)

## Mission Statement 📕

gender\*render (as a project) is motivated by a column of three numerated goals and visions, that it is committed to and that define its vision:

1. **enable** people and corporations to use fully gender-inclusive language in auto-generated texts, be it in an email, notification or computer game (that's what the implementation is for).
2. **proof** that gender-inclusive language in tech and even auto-generated by an algorithm is very well possible (by providing a specification system for this and related subjects).
3. (passively) **raise** awareness to the necessity and practicability of gender-inclusive language and specifically the use and acceptance of gender-inclusive language systems in tech and algorithms (by providing 1 & 2).

These three missions are listed in ascending order of importance (3 is the end goal or the bigger picture, whilst 1 and 2 are the means), as well as vaguely descending order according to how active the project pursues them (3 is pursued purely passively by simply providing 1 and 2, yet serves as their motivation).

In addition to being devoted to its mission, gender\*render is dedicated to the ideals of its [code of conduct](#code-of-conduct).

<!-- ToDo: would this be more elegant?:
In addition to being devoted to its mission, this project is also committed to upholding the moral standards expected of every contributor in our [code of conduct](#code-of-conduct), to the extend applicable to a project.
-->

## License

Specification and implementation are licensed separately.
For the specification, see [here](LICENSE-specification.txt) (OWFa 1.0).
For the implementation, see [here](LICENSE-implementation.txt) (MIT).

For the data sets (e.g. of gendered nouns) that gender\*render uses, refer to the individual licenses included in the files in the `src/data` directory in the TAR-ball from PyPi;
these data sets are all licensed under permissive licenses, but might require different forms of attributions to different people in case you want to modify or redistribute them.

## Development & Contributing

Questions, suggestions and issues as well as pre-discussed pull requests are welcome.
See [here](CONTRIBUTING.md) for additional information.

## Code of Conduct

In general, be decent and don't put shame on the 21st century.
See [here](CODE_OF_CONDUCT.md) for additional information.
