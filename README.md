<p align="center"><!--<a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>-->
<img src="docs/images/title.svg" alt="{gender*render}"></p>

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

## Table of content:

1. [Usage examples](#example-usages)
2. [Template syntax](#template-syntax)
3. [Describing pronoun-use with json data](#describing-pronoun-use-with-json-data)
4. [Installing and using the renderer](#installing-and-using-the-renderer)

## Content:

### Example Usages

### Template syntax

### Describing pronoun-use with json data

### Installing and using the renderer

### The renderer API

## Development:

This tool used [README-driven developement](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html), except with a spec instead of a README. Give it a try, it really works!
 
 Issues are welcome and addressed as fast as possible, especially is they address political issues with the project.
