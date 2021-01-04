<p align="center"><!--<a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>-->
<img src="docs/images/title.svg" alt="{{gender*render}}"></p>

<p align="center" color="violet">Template-system for rendering gender-neutral text- and email-templates properly gendered and with the correct pronouns of all people involved.</p>

Ever had the struggle of correctly gendering people in your automated emails? Are you sick of writing email templates that are unsupportive of non-binary people, gender everyone with ugly underscores, or clumsily avoid pronouns alltogether, costing you hours of work to frickle them together? With gender\*render, you can write easy, gender-neutral templates for your emails, and automatically render them into correctly gendered emails, given the pronouns and names of all people concerned! [[Jump to quickstart]](#example-usages)

[![to quickstart](docs/images/idea-illustration.svg)](#example-usages)

Gender\*render is not only a piece of software that can definitely come in handy if you want to write progressive automated emails, but also a proof of concept. Many people say that correctly gendering non-binary people, people with unusual pronouns, or people with no pronouns at all in automated fashions is impossible. And many live by said premise. gender\*render as a concept is supposed to be a proof that this is simply false, and that any such claims come from a mixture of missing will and laziness, with technical limitations merely being a pretext. Gender\*render comes with an in-depth specification, so you can easily implement it in any language of your choice, port it to other (human) languages or read about the thoughts behind this project! [[Download spec]](https://github.com/phseiff/gender-render/raw/main/docs/spec.pdf)

[![download spec](docs/images/download-spec.svg)](https://phseiff.com/gender-render/spec.pdf)

## Advantages/Features:

Using gender\*render offers a set of advantages over traditional "one for men and one for women"-email templates:

* **Supportive**: Supports addressing one or multiple people in your texts, talking about them in the first as well as second person and multiple grammatical contexts, supports addressing people with no preferred way of addressing, supports preferences regarding noun gendering, supports neo-pronouns.

* **Easy**: Easy enough for non-tech people to write templates with it - writing one template for all genders with gender*render may actually be easier than writing two templates for two genders.

* **Slim & Handy**: gender*render doesn't get into your way and doesn't cluster up your template with syntax for things you don't need right now.

* **Portable**: Comes as a python-module, but with a full specification that encourages re-implementation in different languages.

* **Reliable**: Tested with 100% code- and branch coverage and a more than 2:1 testing code to actual code ratio.

* **Well-documented**: Written with inspiration from literate programming, gender*render comes with a specification with in-depth elaboration on the underlying concepts, as well as full documentation of all methods and an introduction and getting started guide.

If your web forms ask your customers for their pronoun preferences instead of their gender, preferably with text entry boxes instead of dropdowns, and you have these pronoun information in a nice data base, you can easily automate the process of correctly gendering your emails based on the person they are directed to.

{quick_start}

## GitHub badges:

### Implementation:

attribute    | value
-------------|-----------------------------
PyPi | [![PyPI download total](https://img.shields.io/pypi/dm/gender-render.svg)](https://pypi.python.org/pypi/gh-md-to-html/) [![PyPI version](https://img.shields.io/pypi/v/gender-render.svg)](https://pypi.python.org/pypi/gh-md-to-html/) ![PyPI pyversions](https://img.shields.io/pypi/pyversions/gender-render.svg)
license | [![implementation license](https://img.shields.io/badge/license-MIT-lightgreen)](https://github.com/phseiff/gender-render/blob/master/LICENSE-implementation.txt)
maintenance | [![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render) [![Percentage of issues still open](http://isitmaintained.com/badge/open/phseiff/gender-render.svg)](http://isitmaintained.com/project/phseiff/gender-render)
tests | ![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen) ![vulture](https://img.shields.io/badge/vulture-100%25-brightgreen)
documentation | [here](https://phseiff.com/gender-render/docs/code-doc/gender_render/)
build | ![build](https://github.com/phseiff/gender-render/workflows/Build%20%uD83D%uDD27/badge.svg)
installation | `pip3 install gender-render`

### Specification:

attribute    | value
-------------|-----------------------------
license | [![implementation license](https://img.shields.io/badge/license-ToDo-lightgreen)](https://github.com/phseiff/gender-render/blob/master/LICENSE-specification.txt)
download latest | ToDo
download page | ToDo


## License:

Specification and implementation are licensed separately.
For the specification, see [here](LICENSE-specification.txt).
For the implementation, see [here](LICENSE-implementation.txt).

## Development & Contributing:

Active, and issues as well as pre-discussed pull requests are welcome.
See [here](CONTRIBUTING.md) for additional information.

## Code of Conduct:

In general, be decent and don't put shame on the 21st century.
See [here](CODE-OF-CONDUCT.md) for additional information.
