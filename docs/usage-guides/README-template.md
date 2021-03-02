<p align="center"><!--<a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>-->
<img src="https://phseiff.com/gender-render/docs/images/title.svg" alt="{{gender*render}}"></p>

<p align="center" color="violet">Template-system for rendering gender-neutral text-, email- and RPG-text-templates properly gendered and with the correct pronouns of all people involved.</p>

Ever had the struggle of correctly gendering people in your automated emails? Are you sick of writing email templates that are unsupportive of non-binary people, gender everyone with ugly underscores, or clumsily avoid pronouns alltogether, costing you hours of work to frickle them together? With gender\*render, you can write easy, gender-neutral templates for your emails, and automatically render them into correctly gendered emails, given the pronouns and names of all people concerned! [[Jump to quickstart]](#quick-start-)

[![to quickstart](https://phseiff.com/gender-render/docs/images/idea-illustration.svg)](#quick-start-)

Gender\*render is not only a piece of software that can definitely come in handy if you want to write progressive automated emails, but also a proof of concept. Many people say that correctly gendering non-binary people, people with unusual pronouns, or people with no pronouns at all in automated fashions is impossible. And many live by said premise. gender\*render as a concept is supposed to be a proof that this is simply false, and that any such claims come from a mixture of missing will and laziness, with technical limitations merely being a pretext. Gender\*render comes with an in-depth specification, so you can easily implement it in any language of your choice, port it to other (human) languages or read about the thoughts behind this project! [[Download spec]](https://phseiff.com/gender-render/docs/specs/spec/latest.pdf)

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
5. [stats & links](#github-badges-)
6. [Mission Statement](#mission-statement-)
7. [License](#license)
8. [Development & Contributing](#development--contributing)
9. [Code of Conduct](#code-of-conduct)

{quick_start}

{spec_downloads}

## GitHub badges 🏅

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

## License

Specification and implementation are licensed separately.
For the specification, see [here](LICENSE-specification.txt) (OWFa 1.0).
For the implementation, see [here](LICENSE-implementation.txt) (MIT).

## Development & Contributing

Questions, suggestions and issues as well as pre-discussed pull requests are welcome.
See [here](CONTRIBUTING.md) for additional information.

## Code of Conduct

In general, be decent and don't put shame on the 21st century.
See [here](CODE_OF_CONDUCT.md) for additional information.
