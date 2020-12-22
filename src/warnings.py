"""Defines the warnings specified by the spec."""

import warnings
import threading
import typing

# General Warning Class:


class GRWarning(Warning):
    """The base class of all gender*render-warnings.
    All other custom warnings are derived from this one."""
    pass

# Warning Classes:


class NotAWordWarning(GRWarning):
    """The value of a Gendered Noun-tag is not a word known in the
    english (or implementation-specific) language."""
    pass


class NotANounWarning(NotAWordWarning):
    """The value of a Gendered Noun-tag is not a noun known in the
    english language."""
    pass


class NotAPersonNounWarning(NotANounWarning):
    """The value of a Gendered Noun-tag is not a noun known in the
    english language that refers to a person or a title."""
    pass


class FreeUngenderedPersonNounWarning(GRWarning):
    """A noun that refers to a type of person or profession was found
    outside of any tag.
    This is potentially bad because that noun might be gender-dependant."""
    pass


class NounGenderingGuessingsWarning(GRWarning):
    """Raised if a noun will be gendered, but based on automated guesses at the correctly gendered version of the noun
    rather than hardcoded values.
    This warning type is not listed in the specification since it is highly implementation-dependant and should not
    be necessary in a perfect implementation."""
    pass


class UnknownPropertyWarning(GRWarning):
    """A custom property in a piece of individual pronoun data is not
    using the special syntax for custom properties ( property name
    or <property name> rather than just property name). Using the
    special syntax is preferable to ensure that the custom property
    is not named equal to a property introduced in a later version
    or addition to this specification."""
    pass


class FreePronounFound(GRWarning):
    """A (non-neo) pronoun is found freely outside any
    gender*reder-tag."""
    pass


class UnexpectedFileFormatWarning(GRWarning):
    """The file name specified to Template() or Template().render() does not follow the file extension naming
    convention of this specification."""
    pass


class IdMatchingNecessary(GRWarning):
    """Not every tag has an id, or the pronoun data is individual pronoun data, so some matching had to be done.
    This is intended behavior and completely fine.
    This warning is only raised to inform you in case this was accidental. If you don't know what it means, you need
    not worry about it and can safely ignore or disable it."""
    pass


class DefaultValueUsed(GRWarning):
    """An attribute with a default value was looked up in a piece of individual pronoun data, but not found, so its
    default value was used. This is in itself not a problem and perfectly fine behavior; this warning is only raised
    to inform you in case you forgot to define the property or pythonically prefer explicit to implicit."""
    pass


# Define warning types:

WarningType = typing.Type[GRWarning]
WarningSettingType = typing.Union[typing.Set[WarningType], typing.FrozenSet[WarningType]]

# Define standard values for all warnings enables/ all warnings disabled/ default:

all_warnings = [
    NotAPersonNounWarning, NotANounWarning, NotAWordWarning, FreeUngenderedPersonNounWarning, NounGenderingGuessingsWarning,
    UnknownPropertyWarning, FreePronounFound, UnexpectedFileFormatWarning, IdMatchingNecessary, DefaultValueUsed]

ENABLE_ALL_WARNINGS: WarningSettingType = frozenset(all_warnings)
DISABLE_ALL_WARNINGS: WarningSettingType = frozenset()

ENABLE_DEFAULT_WARNINGS: WarningSettingType = ENABLE_ALL_WARNINGS

# WarningManager:


class WarningManager:
    """A bundle of functions to handle warning handling."""
    warning_settings_by_thread_id = dict()

    @staticmethod
    def set_warning_settings(warning_settings: WarningSettingType):
        WarningManager.warning_settings_by_thread_id[threading.get_ident()] = warning_settings

    @staticmethod
    def raise_warning(text: typing.Union[str, None], warning_type: WarningType):
        if text is None:
            text = warning_type.__doc__
        if warning_type in WarningManager.warning_settings_by_thread_id[threading.get_ident()]:
            warnings.warn(text, warning_type)
