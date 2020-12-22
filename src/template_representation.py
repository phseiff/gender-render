"""Implements a class representation of parsed gender*render templates, as defined b the specification."""

import typing
import copy

from . import parse_templates
from . import parse_pronoun_data
from . import warnings
from . import errors
from . import gendered_nouns


class GRenderer:
    """Bundles methods that are part of the rendering pipeline."""
    @staticmethod
    def id_resolution(
            # regarding the given template:
            parsed_template: parse_templates.ParsedTemplateRefined,
            ids_used_in_template: typing.FrozenSet[str],
            template_contains_unspecified_ids: bool,

            # regarding the given pronoun data:
            grpd: parse_pronoun_data.GRPD) -> (parse_templates.ParsedTemplateRefined, parse_pronoun_data.GRPD):
        """Takes a parsed template (as returned by the GRParser-pipeline), a set of all ids used in the template, a
        boolean indicating whether the template contains tags with unspecified ids, and the pronoun data to render it.
        Performs the id resolution steps described by the specification, with the corresponding errors, and returns
        the modified template and grpd.
        No modifications are performed in-place."""

        ids_matched_without_modification = False

        # create deep copies of input values to later modify them:
        new_template = copy.deepcopy(parsed_template)
        new_grpd = copy.deepcopy(grpd)

        # only individual pronoun data is given:
        grpd_is_actually_idpd = "" in grpd
        if grpd_is_actually_idpd:

            # no ids are used in the template:
            if len(ids_used_in_template) == 0:
                new_grpd = {"usr": grpd[""]}
                for i in range(len(new_template)):
                    if not i % 2:  # <- is a tag element
                        new_template[i]["id"] = "usr"

            # all tags have the same id:
            elif len(ids_used_in_template) == 1:
                single_id_in_template, = ids_used_in_template
                new_grpd = {single_id_in_template: grpd[""]}

            # there is more than one id used in the template:
            else:
                raise errors.IdResolutionError("The given template contains more than one id, but the given pronoun data is "
                                               + "individual pronoun data, meaning it has no specified id.")

        # the grpd contains only one id:
        elif len(grpd) == 1:

            # no ids are used in the template:
            if len(ids_used_in_template) == 0:
                for i in range(len(new_template)):
                    if not i % 2:  # <- is a tag element
                        new_template[i]["id"] = list(grpd.keys())[0]

            # all tags have the same id:
            elif len(ids_used_in_template) == 1:
                if list(ids_used_in_template)[0] != list(grpd.keys())[0]:
                    raise errors.IdResolutionError("The pronoun contains only pronouns for one id, and the template also "
                                                   + "contains only one id, but they both differ.")

            # there is more than one id used in the template:
            else:
                raise errors.IdResolutionError("The given template contains exactly one id, but the given pronoun contains "
                                               + "multiple different ids.")

        # the grpd contains more than one id:
        else:

            # all tags have ids assigned:
            if not template_contains_unspecified_ids:
                if not frozenset(grpd.keys()).issuperset(ids_used_in_template):
                    raise errors.IdResolutionError("All tags have ids assigned (more than one id, in summa) and the pronoun "
                                                   + "data contains several ids as well, but they do not match.")
                else:
                    ids_matched_without_modification = True

            # not all tags have ids assigned:
            else:
                if len(grpd) != len(ids_used_in_template) + 1:
                    raise errors.IdResolutionError("Some tags don't have ids, and the amount of different ids used in the "
                                                   + "template does not equal the amount of ids in the pronoun data, minus "
                                                   + "one.")
                else:
                    # there is one id more in the pronoun data than there is in the template:
                    if frozenset(grpd.keys()).issuperset(ids_used_in_template):
                        missing_id_value = list(frozenset(grpd.keys()) - ids_used_in_template)[0]
                        for i in range(len(new_template)):
                            if not i % 2:  # <- is a tag
                                if "id" not in new_template[i]:
                                    new_template[i]["id"] = missing_id_value
                    else:
                        raise errors.IdResolutionError("The template contains tags without an id value and the pronoun data "
                                                       + "contains one more id than the template, but the ids of template and "
                                                       + "pronoun data do not match.")

        # raise a warning if template or pronoun data had to be modified:
        if not ids_matched_without_modification:
            warnings.WarningManager.raise_warning(None, warnings.IdMatchingNecessary)

        return new_template, new_grpd

    @staticmethod
    def render_final_context_values(parsed_template: parse_templates.ParsedTemplateRefined, grpd: parse_pronoun_data.GRPD) -> str:
        """Accepts a parsed template with and a piece of gender*render pronoun data, both with matching id values,
        and returns the rendered template as a string.
        This should be the last step in the rendering pipeline."""

        result = ""
        for i in range(len(parsed_template)):
            if not i % 2:  # <- is a string
                result += parsed_template[i]
            else:  # <- is a tag
                id_value = parsed_template[i]["id"]
                canonical_context_value = parsed_template[i]["context"]
                if type(canonical_context_value) is str:
                    # render tag by looking it up in the individual pronoun data of the individual:
                    try:
                        result += grpd[id_value][canonical_context_value]
                    except KeyError:
                        raise errors.MissingInformationError("A tag in the template required the \""
                                                             + canonical_context_value + "\"-attribute of individual \""
                                                             + id_value + "\", but their individual pronoun data does "
                                                             + "not define this attribute.")
                elif type(canonical_context_value) is gendered_nouns.GenderedNoun:
                    # render tag by correctly gendering the noun it represents.
                    result += canonical_context_value.render_noun(gender)



# Template interface:


class Template:
    """Represents a parsed and preprocessed version of a gender*render template."""

    def __init__(self, template, takes_file_path=False,
                 warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):
        """Return a parsed and preprocessed version of a gender*render template. If takes_file_path is set to False,
        template is interpreted as the template itself; otherwise, it is interpreted as a path to the template."""

        if takes_file_path:
            template = open("template", "r").read()

        warnings.WarningManager.set_warning_settings(warning_settings)

        # get data from the parsed template:
        self.parsed_template = parse_templates.GRParser.full_parsing_pipeline(template)
        self.used_ids = parse_templates.GRParser.get_all_specified_id_values(self.parsed_template)
        self.contains_unspecified_ids = parse_templates.GRParser.pronoun_data_contains_unspecified_ids(self.parsed_template)

    def render(self, pronoun_data, takes_file_path=False,
               warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):
        """Returns a rendered string. pronoun_data must be either a dict, a string of JSON gender*render pronoun data,
        or a file path to a .grpd/.grpd file if takes_file_path is set to True."""

        warnings.WarningManager.set_warning_settings(warning_settings)
