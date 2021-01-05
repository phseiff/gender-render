"""
The interface to gender*render template representations presented to the user.
"""

from . import warnings
from . import parse_templates
from . import render_pipeline
from . import pronoun_data_interface

# Template interface:


class Template:
    """Represents a parsed and preprocessed version of a gender*render template."""

    def __init__(self, template, takes_file_path=False,
                 warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):
        """Return a parsed and preprocessed version of a gender*render template. If takes_file_path is set to False,
        template is interpreted as the template itself; otherwise, it is interpreted as a path to the template."""

        warnings.WarningManager.set_warning_settings(warning_settings)

        if takes_file_path:
            if not template.endswith(".gr"):
                warnings.WarningManager.raise_warning("\"" + template.split(".")[-1] + "\" is not the right file type "
                                                      + "for templates; the right file type would be \".gr\".",
                                                      warnings.UnexpectedFileFormatWarning)
            with open(template, "r") as f_template:
                template = f_template.read()

        # get data from the parsed template:
        self.parsed_template = parse_templates.GRParser.full_parsing_pipeline(template)
        self.used_ids = parse_templates.GRParser.get_all_specified_id_values(self.parsed_template)
        self.contains_unspecified_ids = parse_templates.GRParser.template_contains_unspecified_ids(
            self.parsed_template)

    def render(self, pronoun_data, takes_file_path=False,
               warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):
        """Returns a rendered string. pronoun_data must be either a dict, a string of JSON gender*render pronoun data,
        or a file path to a .grpd/.grpd file if takes_file_path is set to True."""

        warnings.WarningManager.set_warning_settings(warning_settings)
        pronoun_data = pronoun_data_interface.PronounData(pronoun_data, takes_file_path, warning_settings).get_pd()
        return render_pipeline.GRenderer.render_with_full_rendering_pipeline(
            self.parsed_template, self.used_ids, self.contains_unspecified_ids, pronoun_data
        )
