"""
Contains the functions to render templates and pronoun data, bundled together in a class.
This is the submodule where pronoun data and templates finally come together.
"""

import typing
import copy

from . import parse_pronoun_data
from . import parse_templates
from . import warnings
from . import errors
from . import gender_nouns
from .handle_context_values import ContextValues


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
                new_grpd = {"usr": new_grpd[""]}
                for i in range(1, len(new_template), 2):
                    new_template[i]["id"] = "usr"

            # all tags have the same id:
            elif len(ids_used_in_template) == 1 and not template_contains_unspecified_ids:
                single_id_in_template, = ids_used_in_template
                new_grpd = {single_id_in_template: new_grpd[""]}

            # there is more than one id used in the template:
            else:
                raise errors.IdResolutionError("The given template contains more than one id, but the given pronoun "
                                               + "data is individual pronoun data, meaning it has no specified id.")

        # the grpd contains only one id:
        elif len(grpd) == 1:

            # no ids are used in the template:
            if len(ids_used_in_template) == 0:
                for i in range(1, len(new_template), 2):
                    new_template[i]["id"] = list(grpd.keys())[0]

            # all tags have the same id:
            elif len(ids_used_in_template) == 1 and not template_contains_unspecified_ids:
                if list(ids_used_in_template)[0] != list(grpd.keys())[0]:
                    raise errors.IdResolutionError("The pronoun contains only pronouns for one id, and the template "
                                                   + "also contains only one id, but they both differ.")
                else:
                    ids_matched_without_modification = True

            # there is more than one id used in the template:
            else:
                raise errors.IdResolutionError("The given template contains exactly one id, but the given pronoun "
                                               + "contains multiple different ids.")

        # the grpd contains more than one id:
        else:

            # all tags have ids assigned:
            if not template_contains_unspecified_ids:
                if not frozenset(grpd.keys()).issuperset(ids_used_in_template):
                    raise errors.IdResolutionError("All tags have ids assigned (more than one id, in summa) and the "
                                                   + "pronoun data contains several ids as well, but they do not "
                                                   + "match.")
                else:
                    ids_matched_without_modification = True

            # not all tags have ids assigned:
            else:
                if len(grpd) != len(ids_used_in_template) + 1:
                    raise errors.IdResolutionError("Some tags don't have ids, and the amount of different ids used in "
                                                   + "the template does not equal the amount of ids in the pronoun "
                                                   + "data, minus one.")
                else:
                    # there is one id more in the pronoun data than there is in the template:
                    if frozenset(grpd.keys()).issuperset(ids_used_in_template):
                        missing_id_value = list(frozenset(grpd.keys()) - ids_used_in_template)[0]
                        for i in range(1, len(new_template), 2):
                            if "id" not in new_template[i]:
                                new_template[i]["id"] = missing_id_value
                    else:
                        raise errors.IdResolutionError("The template contains tags without an id value and the "
                                                       + "pronoun data contains one more id than the template, but "
                                                       + "the ids of template and pronoun data do not match.")

        # raise a warning if template or pronoun data had to be modified:
        if not ids_matched_without_modification:
            warnings.WarningManager.raise_warning(None, warnings.IdMatchingNecessaryWarning)

        return new_template, new_grpd

    @staticmethod
    def resolve_addressing(parsed_template: parse_templates.ParsedTemplateRefined,
                           grpd: parse_pronoun_data.GRPD) -> (parse_templates.ParsedTemplateRefined,
                                                              parse_pronoun_data.GRPD):
        """Accepts a parsed template with a piece of gender*render pronoun data, both with matching id values,
        and returns a modified copy of the template in which the implications of the gender-addressing property are
        already applied and the grpd."""

        new_template = copy.deepcopy(parsed_template)
        new_grpd = copy.deepcopy(grpd)
        for i in range(1, len(new_template), 2):
            id_value = new_template[i]["id"]
            if new_template[i]["context"] == "address":
                if ContextValues.get_value(grpd, id_value, "gender-addressing") in ("f", "false"):
                    new_template[i]["context"] = "personal-name"

        return new_template, new_grpd

    @staticmethod
    def render_final_context_values(parsed_template: parse_templates.ParsedTemplateRefined,
                                    grpd: parse_pronoun_data.GRPD) -> str:
        """Accepts a parsed template with a piece of gender*render pronoun data, both with matching id values,
        and returns the rendered template as a string.
        This should be the last step in the rendering pipeline."""

        result = ""
        for i in range(len(parsed_template)):
            if not i % 2:  # <- is a string
                result += parsed_template[i]
            else:  # <- is a tag
                id_value = parsed_template[i]["id"]
                context_value = parsed_template[i]["context"]

                if ContextValues.property_maps_directly_between_template_and_pronoun_data(context_value):
                    # render tag by looking it up in the individual pronoun data of the individual:
                    result += ContextValues.get_value(grpd, id_value, context_value)

                else:  # type(context_value) is gender_nouns.GenderedNoun:
                    # render tag by correctly gendering the noun it represents.
                    gender = ContextValues.get_value(grpd, id_value, "gender-nouns")
                    result += context_value.render_noun(gender)

        return result

    @staticmethod
    def render_with_full_rendering_pipeline(
            # regarding the given template:
            parsed_template: parse_templates.ParsedTemplateRefined,
            ids_used_in_template: typing.FrozenSet[str],
            template_contains_unspecified_ids: bool,

            # regarding the given pronoun data:
            grpd: parse_pronoun_data.GRPD) -> str:
        """Takes a parsed template, a set of ids used in the template, a boolean specifying whether there are
        tags without specified ids in the template, and a piece of the grpd, and runs the full set of functions defined
        by GRenderer on it.
        Returns the rendered template."""

        parsed_template, grpd = GRenderer.id_resolution(parsed_template, ids_used_in_template,
                                                        template_contains_unspecified_ids, grpd)
        parsed_template, grpd = GRenderer.resolve_addressing(parsed_template, grpd)
        result = GRenderer.render_final_context_values(parsed_template, grpd)

        return result
