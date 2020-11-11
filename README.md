<p align="center"><a href="https://github.com/phseiff"><img src="https://phseiff.com/images/brought-to-you-by-phseiff.svg" alt="brought to you by phseiff:"></a>
<img src="images/title.svg" alt="{gender*render}"></p>

<p align="center" color="violet">Template-system for rendering gender-neutral text- and email-templates properly gendered and with the correct pronouns of all people involved.</p>

Ever had the struggle of correctly gendering people in your automated emails? Are you sick of writing email templates that are unsupportive of non-binary people, gender everyone with ugly underscores, or clumsily avoid pronouns alltogether, costing you hours of work to frickle them together? With gender\*render, you can write easy, gender-neutral templates for your emails, and automatically render them into correctly gendered emails, given the pronouns and names of all people concerned!

Advantages include:

* Works even if your text mentions or addresses *multiple* individuals with unknown genders.

* Syntax definitions for a template language to describe which individual is addressed at which point and in which grammatical form.

* Different implementation for rendering said templates based on data describing the pronoun differences of all people referenced in the template. These include:

  * A python module
  * a command line frontend
  * a self-hostable REST API written in flask with a ready-to-go docker compose file
  * a javascript module, which is also hosted online so you can easily embed it into your website
all of these methods share the same API, but provide different ways to use it in different systems and langauges.

* The data describing which persons use which pronouns is accepted in JSON syntax (and, of cause, as a python dict or javascript object, when using the respective APIs).

* Easy, yet powerful and sleek syntax.

* Supports ANY pronoun-sets or forms of addressing, including pronoun-less identities (as long as you include additional information to render those).

* Aids you you in being a decent human being by correctly genering persons in your automated emails!

## Developement:

This tool uses [README-driven developement](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html). Issues are welcome and addressed as fast as possible, especially is they address political issues with the project.
