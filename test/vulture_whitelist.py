"""
For gender-render to build correctly, some tests must pass. These include vulture, which fails if it finds dead code.
This file whitelists some parts of gender_render as not-dead code by importing them, such as parts of the user interface
that may be technically dead, but still exist to be called by users, or Warning types that don't do anything (yet), but
are still implemented for completeness.
"""

# Things that are there for a reason, yet technically dead:


render_template  # unused function (src/__init__.py:27)
FreeGenderedPersonNounWarning  # unused class (src/warnings.py:71)
FreePronounFoundWarning  # unused class (src/warnings.py:96)
ENABLE_ALL_LOGGING  # unused variable (src/warnings.py:147)
DISABLE_ALL_WARNINGS  # unused variable (src/warnings.py:149)

# Things that are there for debugging:


_.switch_escapement  # unused method (src/parse_templates.py:92)
_.unparse_gr_template_from_parsed_gr_template  # unused method (src/parse_templates.py:424)
