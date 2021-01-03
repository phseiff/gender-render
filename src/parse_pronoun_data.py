"""
Contains functions for gender*render pronoun data.
"""

import json
from typing import Union

from . import errors
from . import warnings
from .handle_context_values import ContextValues, IDPD, GRPD

# functions for parsing individual pronoun data:


class GRPDParser:
    """Bundles various methods for parsing gender*render pronoun data in a pipeline together."""

    @staticmethod
    def pd_string_to_dict(pd: str) -> dict:
        """Parses a JSON string into a dict and returns it."""
        try:
            pd_dict = json.loads(pd)
        except json.decoder.JSONDecodeError:
            raise errors.InvalidPDError("The given pronoun data (given as a string) is not a valid piece of JSON data.")
        return pd_dict

    @staticmethod
    def type_of_pd(pd: Union[GRPD, IDPD]) -> Union[GRPD, IDPD]:
        """Returns GRPD or IDPD, depending on what type (if any) of pronoun data the given string is.
        Raises an error if it is neither of these two."""
        if type(pd) is dict:
            all_values_are_strings = True
            all_values_are_dicts = True
            for value in pd.values():
                if type(value) is not str:
                    all_values_are_strings = False
                if type(value) is not dict:
                    all_values_are_dicts = False
            if all_values_are_dicts:
                for idpd in pd.values():
                    for v in idpd.values():
                        if type(v) is not str:
                            raise errors.InvalidPDError(
                                "A property of a piece of individual pronoun data is assigned a non-string value.")
                if "" in pd:
                    raise errors.InvalidPDError(
                        "\"\" is not a valid id value in a piece of gender*render pronoun data")
                return GRPD
            elif all_values_are_strings:
                return IDPD
            else:
                raise errors.InvalidPDError(
                    "The values of all top-level key-value-pairs of the given pronoun data are neither all objects, nor"
                    + " are they all strings, but rather, a mixture of multiple types. This is neither allowed for a"
                    + " piece of individual pronoun data (has only string values), nor a piece of gender*render pronoun"
                    + " data (which has only object values), and is therefore invalid."
                )
        else:
            raise errors.InvalidPDError(
                "This piece of pronoun data is neither individual pronoun data nor gender*render pronoun data."
            )

    @staticmethod
    def return_pd_if_it_is_valid(pd: dict) -> Union[GRPD, IDPD]:
        """Takes a dict, raises an error if it is neither a piece of gender*render pronoun data nor a piece of
        individual pronoun data and returns it otherwise."""
        try:
            GRPDParser.type_of_pd(pd)
        except errors.InvalidPDError:
            raise errors.InvalidPDError("The given JSON object is not a valid piece of pronoun data.")
        return pd

    @staticmethod
    def pd_dict_to_grpd_dict(pd: Union[GRPD, IDPD]) -> GRPD:
        """Converts a piece of valid pronoun data to a grpd, in case it is an idpd.
        The returned object may be identical to the given object or reference it."""
        if GRPDParser.type_of_pd(pd) is GRPD:
            return pd
        else:  # GRPDParser.type_of_pd(pd) is IDPD:
            return {"": pd}

    @staticmethod
    def grpd_dict_to_canonical_grpd_dict(pd: GRPD) -> GRPD:
        """Takes a gender*render pronoun data dict and returns it with every property made canonical.
        Raises a DoubledInformationError if a piece of idpd contains two properties for the same attribute.
        Raises a InvalidInformationError if a property has a value it may not have.
        Raises a warning if a custom attribute is not recognizable as such."""
        result = dict()
        for id in pd:
            new_idpd = dict()
            for gr_property, value in pd[id].items():
                canonical_context_value = ContextValues.get_canonical(gr_property, is_from_tag=False)

                # raise an error if two properties for the same attribute exist:
                if canonical_context_value in new_idpd:
                    raise errors.DoubledInformationError("The individual pronoun data for id \"" + id + "\" defines "
                                                         + "multiple values for the \"" + canonical_context_value
                                                         + "\" attribute, using different properties. Only one is "
                                                         + "allowed!")

                # raises an error if an attribute with a limited set of valid values is used and the value is invalid:
                if not ContextValues.value_is_allowed(canonical_context_value, value):
                    raise errors.InvalidInformationError("The individual pronoun data for id \"" + id + "\" defines "
                                                         + "\"" + value + "\" as the value for \""
                                                         + canonical_context_value + "\" even though this attribute "
                                                         + "does not allow this value.")

                # raises a warning if a custom attribute does not use the special syntax for custom properties:
                if (ContextValues.is_a_custom_value(gr_property)
                        and not ContextValues.uses_special_custom_value_syntax(gr_property)):
                    warnings.WarningManager.raise_warning("The individual pronoun data for individual \"" + id + "\" "
                                                          + "contains a custom property, but said property does not use"
                                                          + " special custom property syntax.",
                                                          warnings.UnknownPropertyWarning)
                new_idpd[canonical_context_value] = value
            result[id] = new_idpd
        return result

    @staticmethod
    def full_parsing_pipeline(pd: dict) -> GRPD:
        """Parses a dict into a valid piece of grpd following the pipeline defined by GRPDParser, and raises an error if
        this turns out to be impossible."""
        pd = GRPDParser.return_pd_if_it_is_valid(pd)
        pd = GRPDParser.pd_dict_to_grpd_dict(pd)
        pd = GRPDParser.grpd_dict_to_canonical_grpd_dict(pd)
        return pd
