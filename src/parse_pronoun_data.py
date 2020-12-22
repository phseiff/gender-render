"""Functions that regard gender*render pronoun data and its attributes/properties."""

from typing import Union, Dict, Generic, Any
import json

from . import errors
from . import warnings
from . import gendered_nouns

# some type definitions:


IDPD = Dict[str, str]
GRPD = Dict[str, IDPD]

# values for context sections:


class ContextValues:
    """Defines values for context sections/ attributes for individual pronoun data as well as methods to compare them
    (which is not trivial since there are multiple words ("properties") for every attribute."""

    properties = [
        # context values of gender*render tags:
        ["subject", "they", "subj"],
        ["object", "them", "obj"],
        ["dpossessive", "their", "dposs"],
        ["ipossessive", "theirs", "iposs"],
        ["reflexive", "themself", "reflex"],

        ["address", "Mr_s", "Mr", "Mrs"],
        ["surname", "Smith", "name", "family-names"],
        ["personal-name", "Avery", "first-name"],

        # properties of individual pronoun data:
        ["gendered-addressing"],
        ["gender-nouns"]
    ]
    """A list of lists, each one containing all properties corresponding to one certain attribute.
    The first value is always the canonical value (the one that pronoun data should ideally use), the second value
    the intuitive one (the one with the best language flow when used in a template), and the third one may be the
    shortest form, but there is no specific rule to this."""

    properties_to_canonical_property = dict()
    """Maps every property to a "canonical property". Canonical properties are a concept used by this implementation to
    check two properties for equal meaning; if they both have the same canonical property, their meaning is equal."""

    canonical_properties_that_directly_map_between_template_and_pronoun_data = [
        "subject", "object", "dpossessive", "ipossessive", "reflexive", "address", "surname", "personal-name"
    ]
    """A list of canonical properties that map directly between template and individual pronoun data."""

    properties_that_allow_only_some_values_in_pd = {
        "gendered-addressing": {"false", "true", "f", "t"},
        "gender-nouns": {"female", "male", "neutral"}
    }
    """A mapping of all (canonical) pronoun data properties that only allow some selected values to sets of these
    values."""

    @staticmethod
    def value_is_allowed(canonical_property_name: str, value: str) -> bool:
        """Returns whether the given canonical property name allows the given value (in the individual pronoun data;
        this is not about the templates)"""
        if canonical_property_name in ContextValues.properties_that_allow_only_some_values_in_pd:
            if value not in ContextValues.properties_that_allow_only_some_values_in_pd[canonical_property_name]:
                return False
        return True

    @staticmethod
    def initialize():
        """Initializes the data bundled with ContextValues. """
        for property_list in ContextValues.properties:
            for p in property_list:
                ContextValues.properties_to_canonical_property[p] = property_list[0]

    @staticmethod
    def check_if_canonical_property_may_have_certain_value(property_name: str, property_value: str) -> bool:
        """Checks if canonical property property_name may have a certain value assigned in a piece of individual
        pronoun data."""
        if property_name in ContextValues.properties_that_allow_only_some_values_in_pd:
            if property_value not in ContextValues.properties_that_allow_only_some_values_in_pd[property_name]:
                return False
        return True

    @staticmethod
    def property_maps_directly_between_template_and_pronoun_data(property_name: str) -> bool:
        """Checks whether this property name can be mapped between template and individual pronoun data directly
        without any additional calculations whatsoever."""
        return (
                property_name in ContextValues.canonical_properties_that_directly_map_between_template_and_pronoun_data
                or (property_name.startswith("<") and property_name.endswith(">"))
        )

    @staticmethod
    def is_a_custom_property_defined_in_a_tag(property_name: str) -> bool:
        """Returns whether the property is a custom property using the syntax of tags, which is the
        "<property_name>"-syntax."""
        return property_name.startswith("<") and property_name.endswith(">")

    @staticmethod
    def get_canonical_of_custom_property(property_name: str) -> str:
        """Returns the canonical of a custom property, which happens to be the "<property_name>"-syntax."""
        if property_name.startswith("_"):
            return "<" + property_name[1:] + ">"
        elif property_name.startswith("<") and property_name.endswith(">"):
            return property_name
        else:
            return "<" + property_name + ">"

    @staticmethod
    def get_canonical(property_name: str, is_from_tag=True) -> Union[str, gendered_nouns.GenderedNoun]:
        """Returns the canonical version for a context value or pronoun data property.
        If is_from_tag is True, the method assumes that the value is from a context section (unknown names are nouns).
        Otherwise, it assumes unknown names are custom attributes.
        The canonical version of custom attributes is the "<property_name>"-syntax."""
        if property_name in ContextValues.properties_to_canonical_property:
            return ContextValues.properties_to_canonical_property[property_name]
        else:
            if is_from_tag:
                if ContextValues.is_a_custom_property_defined_in_a_tag(property_name):
                    return ContextValues.get_canonical_of_custom_property(property_name)
                else:
                    return gendered_nouns.GenderedNoun(property_name)
            else:
                return ContextValues.get_canonical_of_custom_property(property_name)

# functions for parsing individual pronoun data:


class GRPDParser:
    """Bundles various methods for parsing gender*render pronoun data in a pipeline together."""

    @staticmethod
    def type_of_pd(pd: Union[GRPD, IDPD]) -> Union[GRPD, IDPD]:
        """Returns GRPD or IDPD, depending on what type (if any) of pronoun data the given string is.
        Raises an error if it is neither of these two."""
        # ToDo: Remove the restrictions for id names from spec and define \ as an escape character more broad.
        #  However, specify that ids may not be empty strings.
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
                        "\"\" is not a valid id value in a piece of gender*render pronoun. data")
                return GRPD
            elif all_values_are_strings:
                return IDPD
        else:
            raise errors.InvalidPDError(
                "This piece of pronoun data is neither individual pronoun data nor gender*render pronoun data."
            )

    @staticmethod
    def pd_string_to_dict(pd: str) -> dict:
        """Parses a JSON string into a dict and returns it."""
        try:
            pd_dict = json.loads(pd)
        except json.decoder.JSONDecodeError:
            raise errors.InvalidPDError("The given pronoun data (given as a string) is not a valid piece of JSON data.")
        return pd_dict

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
        elif GRPDParser.type_of_pd(pd) is IDPD:
            return {"": pd}

    @staticmethod
    def grpd_dict_to_canonical_grpd_dict(pd: GRPD) -> GRPD:
        """Takes a gender*render pronoun data dict and returns it with every property made canonical.
        Raises a DoubledInformationError if a piece of idpd contains two properties for the same attribute."""
        result = dict()
        for id in pd:
            new_idpd = dict()
            for gr_property, value in new_idpd.items():
                canonical_context_value = ContextValues.get_canonical(gr_property, is_from_tag=False)
                if canonical_context_value not in new_idpd:
                    new_idpd[canonical_context_value] = value
                else:
                    raise errors.DoubledInformationError("The individual pronoun data for id \"" + id + "\" defines "
                                                         + "multiple values for the \"" + canonical_context_value
                                                         + "\" attribute, using different properties. Only one is "
                                                         + "allowed!")
                if not ContextValues.value_is_allowed(canonical_context_value, value):
                    raise errors.InvalidInformationError("The individual pronoun data for id \"" + id + "\" defines "
                                                         + "\"" + value + "\" as the value for \""
                                                         + canonical_context_value + "\" even though this attribute "
                                                         + "does not allow this warning.")
            result[id] = new_idpd
        return result

    @staticmethod
    def return_canonical_grpd_if_all_values_are_valid(pd: GRPD) -> GRPD:
        """Takes a gender*render pronoun data dic and raises an error if a property with a defined set of allowed
        values has a non-allowed value; otherwise, returns the pronoun data."""
        for idpd in pd.values():
            for property_name, property_value in idpd.items():
                if not ContextValues.check_if_canonical_property_may_have_certain_value(property_name, property_value):
                    raise errors.InvalidPDError("Individual pronoun data property \"" + property_name
                                                + "\" may not have value \"" + property_value + "\".")
        return pd

    @staticmethod
    def full_parsing_pipeline(pd: dict) -> GRPD:
        """Parses a dict into a valid piece of grpd following the pipeline defined by GRPDParser, and raises an error if
        this turns out to be impossible."""
        pd = GRPDParser.return_pd_if_it_is_valid(pd)
        pd = GRPDParser.pd_dict_to_grpd_dict(pd)
        pd = GRPDParser.grpd_dict_to_canonical_grpd_dict(pd)
        pd = GRPDParser.return_canonical_grpd_if_all_values_are_valid(pd)
        return pd

# a class representation for pronoun data, as defined by the spec:


class PronounData:
    """A representation for pronoun data as defined by the specification."""
    def __init__(self, pronoun_data: Union[str, dict], takes_file_path=False):
        # read from file (if necessary) and parse from JSON to a dict:
        if takes_file_path:
            pd_as_str = open(pronoun_data, "r").read()
        else:
            pd_as_str = pronoun_data
        if type(pronoun_data) is str:
            pd_as_dict = GRPDParser.pd_string_to_dict(pd_as_str)
        else:
            pd_as_dict = pd_as_str

        # raise warning if the wrong file format was chosen:
        if takes_file_path:
            file_format = pronoun_data.split(".")[-1].lower()
            content_format = "grpd" if GRPDParser.type_of_pd(pd_as_dict) is GRPD else "idpd"
            if file_format != content_format:
                warnings.WarningManager.raise_warning(
                    "The file format ." + file_format + " contains " + content_format + " data. "
                    + "This kind of data should e contained in ." + content_format + " files instead.",
                    warnings.UnexpectedFileFormatWarning
                )

        self.grpd = GRPDParser.full_parsing_pipeline(pronoun_data)

    def is_idpd(self):
        """Checks whether it is a representation of individual pronoun data rather than gender*render pronoun data."""
        return list(self.grpd.keys()) == [""]

# initialize all derived data declared in this submodule:


ContextValues.initialize()
