"""
Implementation of the *global capitalization system* (a concept explained in-depth in the specification), which
analyses and understands capitalization of a tag's context value, stores it into a special section of the tag, and
re-applies said capitalization to the value the  tag is rendered to.

The types of capitalization are as follows:

name            | example
----------------|--------
lower-case      | foobar
capitalized     | Foobar
all-caps        | FOOBAR
studly-caps     | FoObAR
alt-studly-caps | fOoBaR

ToDo: Thoroughly test this module (best to start with this).
"""

from collections import namedtuple, OrderedDict
from typing import Dict, NamedTuple, Callable, Union, List

from . import errors


# Helper functions
# - these functions are tolerant versions of str.isupper() and str.islower(), in that they don't return False if there
#   are no cased characters.

def isupper(s: str) -> bool:
    return all((not c.islower()) for c in s)


def islower(s: str) -> bool:
    return all((not c.isupper()) for c in s)


# Define types for capitalization methods:

CapitalizationMethod = namedtuple("CapitalizationMethod", "is_applied apply")

CapitalizationMethodTable = Dict[str, NamedTuple("CapitalizationMethod", [
    ("apply", Callable[[str], str]),
    ("is_applied", Callable[[str], bool])
])]


# Define Capitalization methods:

# note that dicts are ordered in their insertion order starting with Python 3.6!
# the functions in this dict assume that `is_applied` is never used on "", since context values are never empty.
# `apply` does take this possibility into account, though.

CAPITALIZATION_TABLE: CapitalizationMethodTable = OrderedDict([
    ("lower-case", CapitalizationMethod(
        apply=lambda s: s.lower(),
        is_applied=lambda s: islower(s)
    )),
    ("capitalized", CapitalizationMethod(
        apply=lambda s: (s[0].upper() + s[1:].lower()) if len(s) > 0 else "",
        is_applied=lambda s: isupper(s[0]) and islower(s[1:])
    )),
    ("all-caps", CapitalizationMethod(
        apply=lambda s: s.upper(),
        is_applied=lambda s: isupper(s)
    )),
    ("studly-caps", CapitalizationMethod(
        apply=lambda s: "".join([(s[i].lower() if i % 2 else s[i].upper()) for i in range(len(s))]),
        is_applied=lambda s: all((islower(s[i]) if i % 2 else isupper(s[i])) for i in range(len(s)))
    )),
    ("alt-studly-caps", CapitalizationMethod(
        apply=lambda s: "".join([(s[i].upper() if i % 2 else s[i].lower()) for i in range(len(s))]),
        is_applied=lambda s: all((isupper(s[i]) if i % 2 else islower(s[i])) for i in range(len(s)))
    )),
])


# Funktionen:


def get_capitalization_from_context_value(context_value: str) -> str:
    """Returns the capitalization type of a context value, and raises an error if it matches none."""
    for capitalization_type_name, capitalization_method in CAPITALIZATION_TABLE.items():
        if capitalization_method.is_applied(context_value):
            return capitalization_type_name
    raise errors.InvalidCapitalizationError("A tag has the context value '" + context_value + "'.\n"
                                            + "This does not fit any allowed capitalization type.\n"
                                            + "Refer to the specification to learn how to use capitalization in tags.")


def assign_and_check_capitalization_value_of_tag(tag: Dict[str, Union[str, List[str]]]):
    """Assigns a tag (with one context value) (given in the same format as the format they have in
    `parse_templates.ParsedTemplateRefined`) a capitalization value if it does not have one yet, and raises an
    `errors.InvalidCapitalizationError` should it find issues with the tag's capitalization value or its context value's
    capitalization, and makes the tag's context value lower-case."""

    # raise an error if capitalization value is specified, yet invalid:
    if "capitalization" in tag and tag["capitalization"] not in CAPITALIZATION_TABLE:
        raise errors.InvalidCapitalizationError("A tag has an explicitly specified capitalization value of '"
                                                + tag["capitalization"] + "'.\nThis is not a valid value.")

    # raise an error if context value is capitalized, yet in an invalid way:
    capitalization_of_context_value = get_capitalization_from_context_value(tag["context"])

    # raise an error if the capitalization value is specified, plus implied using semantic sugar:
    if capitalization_of_context_value != "lower-case" and "capitalization" in tag:
        raise errors.InvalidCapitalizationError("A tag explicitly specified its capitalization value as '"
                                                + tag["capitalization"] + "', but has already has capitalization in"
                                                + " its context value '" + tag["context"] + "'.")

    # assign the tag a capitalization value derived from semantic sugar if it doesn't have one already:
    if "capitalization" not in tag:
        tag["capitalization"] = capitalization_of_context_value

    # make context value lower-case:
    tag["context"] = tag["context"].lower()


def apply_capitalization_to_tag(tag: Dict[str, Union[str, List[str]]]) -> str:
    """Applies capitalization to tag's context value (which should store the rendered version of the tag) in accordance
    to the tag's capitalization value, and returns the correctly capitalized finished context value.
    This is supposed to be called during the rendering process when the tag has its rendered value, minus proper
    capitalization, already stored in its context value (a design decision that isn't made by the spec, but by this
    implementation since it comes in handy)."""
    return CAPITALIZATION_TABLE[tag["capitalization"]].apply(tag["context"])
