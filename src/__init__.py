#!/usr/bin/env python
"""

.. include:: ../README.md

.. include:: ../download_page.md

The gender*render-python reference implementation.
For documentation and a usage guide, see https://phseiff.com/gender-render/

This implementation follows the specification(s) found here:
https://phseiff.com/gender-render/#download-specifications

The interfaces defined by the main specification can be found as `gender_render.Template`, (from
`gender_render.template_interface`), `gender_render.PronounData` (from `gender_render.pronoun_data_interface`) and
`gender_render.render_template`.

To find out how to enable and disable warnings, refer to the documentation of `gender_render.warnings`.
"""

__author__ = "phseiff"
__version__ = "1.0.0"

import typing
from .handle_context_values import GRPD, IDPD

from . import warnings
from .pronoun_data_interface import PronounData
from .template_interface import Template

# the render_template function from the specification:


def render_template(template, pronoun_data: typing.Union[str, GRPD, IDPD], takes_file_path=False,
                    warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):
    """Accepts a gender*render template as a string and a string or dict of pronoun data or, if `takes_file_path` is
    True, two file paths to both, and returns the template rendered with the given pronoun data.
    Serves as a shortcut for Template(...).render(PronounData(...), ...)"""

    pd = PronounData(pronoun_data, takes_file_path, warning_settings)
    tr = Template(template, takes_file_path, warning_settings)
    return tr.render(pd, warning_settings=warning_settings)
