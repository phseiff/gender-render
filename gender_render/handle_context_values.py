"""
Functions that regard gender*render pronoun data's properties and attributes and their relationship to
context-values of tags.
"""

from typing import Dict, Union

from . import errors
from . import warnings
from . import gender_nouns

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
        ["surname", "Doe", "name", "family-names"],
        ["personal-name", "Jean", "first-name"],

        # properties of individual pronoun data:
        ["gender-addressing"],
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
        "gender-addressing": {"false", "true", "f", "t"},
        "gender-nouns": {"female", "male", "neutral"}
    }
    """A mapping of all (canonical) pronoun data properties that only allow some selected values to sets of these
    values."""

    default_values = {
        "gender-addressing": "t",
        "gender-nouns": "neutral"
    }
    """A mapping of all (canonical) pronoun data properties who have default values to their default values."""

    @staticmethod
    def get_value(grpd: GRPD, id: str, property_name: str) -> str:
        """Returns the value of property_name of the given id in the given grpd, and raises the correct error if this
        id does not have this value defined and there is no default value.
        If there is a default value to use, however, this default value is returned and a warning is risen.
        This does not check whether the value assigned by the GRPD is allowed for its property, since this should be
        done by the pd parser on pd initialisation time instead of every time the pd is usd to render a template."""
        if property_name in grpd[id]:
            return grpd[id][property_name]
        else:
            if property_name not in ContextValues.default_values:
                raise errors.MissingInformationError("A tag in the template required the \"" + property_name
                                                     + "\"-attribute of individual \"" + id + "\", but their "
                                                     + "individual pronoun data does not define this attribute.")
            else:
                warnings.WarningManager.raise_warning("Rendering a template requires the default value of the \""
                                                      + property_name + "\"-property of individuum \"" + id + "\", but "
                                                      + "this individuum has this value undefined, so its default had "
                                                      + "to be used.", warnings.DefaultValueUsedWarning)
                return ContextValues.default_values[property_name]

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
    def property_maps_directly_between_template_and_pronoun_data(property_name: str) -> bool:
        """Checks whether this canonical property name can be mapped between template and individual pronoun data
        directly without any additional calculations whatsoever."""
        if type(property_name) is not str:
            return False
        return (
                property_name in ContextValues.canonical_properties_that_directly_map_between_template_and_pronoun_data
                or (property_name.startswith("<") and property_name.endswith(">"))
        )

    @staticmethod
    def is_a_custom_value(property_name: str) -> bool:
        """Returns whether the (not necessarily canonical) property is a custom property.
        This function is made for pronoun data analysis, not tag analysis."""
        return property_name not in ContextValues.properties_to_canonical_property

    @staticmethod
    def uses_special_custom_value_syntax(property_name: str) -> bool:
        """Returns whether the property uses the special syntax for making custom properties in individual pronoun data
        to be distinguishable from standard attributes."""
        return property_name.startswith("<") and property_name.endswith(">") or property_name.startswith("_")

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
    def get_canonical(property_name: str, is_from_tag=True) -> Union[str, gender_nouns.GenderedNoun]:
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
                    return gender_nouns.GenderedNoun(property_name)
            else:
                return ContextValues.get_canonical_of_custom_property(property_name)

# initialize all derived data generated in this submodule:


ContextValues.initialize()
