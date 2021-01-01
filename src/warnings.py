"""Defines the warnings specified by the spec.

To enable and disable warnings, pass a set of all warnings you want enabled to the "enable_warnings"-parameter of any
of the interfaces defined in the specifications. All warnings are declared as classes in this submodule.

By default, all warnings are enabled.

Ready-made sets of values for the "enable_warnings"-parameter include:

- ENABLE_ALL_WARNINGS: a set of all warnings
- ENABLE_DEFAULT_WARNINGS: a set of all warnings enabled by default
- DISABLE_ALL_WARNINGS: an empty set (disables all warnings)
- ENABLE_ALL_LOGGING: a set of all warning classes that enable types of logging rather than warnings.

Please note that classes that enable logging rather than actual warnings are not included in the
gender_render.ENABLE_ALL_WARNINGS set. Every type of warning that would be raised regardless of input at initialization
time of the module is considered logging rather than warning.

When calling a function, method or class that isn't specified as a public interface by the specification (currently only
render_template, Template and PronounData), the warning behavior is unreliable; you therefore shouldn't do this unless
you explicitly define your preferred warning settings with `WarningManager.set_warning_settings`.
"""

import warnings as ws
import threading
import typing
import inspect

# General Warning Classes:


class GRWarning(Warning):
    """The base class of all gender*render-warnings.
    All other custom warnings are derived from this one."""
    pass


class GRLogging(Warning):
    """The base class for all warnings that are actually not warnings, but logs that enable or disable certain types of
    additional logging.
    These classes are mostly implementation-specific."""
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
    """A noun that refers to a type of person or profession was found outside of any tag.
    This is potentially bad because that noun might be gender-dependant."""
    # ToDo: There is actually no implementation to search for this yet; make an issue if you want to discuss it!
    pass


class FreeGenderedPersonNounWarning(FreeUngenderedPersonNounWarning):
    """A noun that refers to a type of person or profession and is not neutral was found outside of any tag.
    This is probably harmfull if this noun refers to a person whose gender should be determined by pronoun data."""
    # ToDo: There is actually no implementation to search for this yet; make an issue if you want to discuss it!
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


class FreePronounFoundWarning(GRWarning):
    """A (non-neo) pronoun is found freely outside any
    gender*render-tag."""
    # ToDo: There is actually no implementation to search for this yet; make an issue if you want to discuss it!
    pass


class IdMatchingNecessaryWarning(GRWarning):
    """Not every tag has an id, or the pronoun data is individual pronoun data, so some matching had to be done.
    This is intended behavior and completely fine.
    This warning is only raised to inform you in case this was accidental. If you don't know what it means, you need
    not worry about it and can safely ignore or disable it."""
    pass


class UnexpectedFileFormatWarning(GRWarning):
    """The file name specified to Template() or Template().render() does not follow the file extension naming
    convention of this specification."""
    pass


class DefaultValueUsedWarning(GRWarning):
    """An attribute with a default value was looked up in a piece of individual pronoun data, but not found, so its
    default value was used. This is in itself not a problem and perfectly fine behavior; this warning is only raised
    to inform you in case you forgot to define the property or pythonically prefer explicit to implicit."""
    # This warning is not part of the specification since it is too specific of a design decision to expect every
    #  implementation to follow it.
    pass


class GenderedNounsBuildFromWebWarning(GRWarning):
    """The data containing the gendered and especially neutral versions of all english hyponyms for "person" could not
    be found; therefore, it will be downloaded and saved from the internet now. This should only happen once per
    installation and only when initializing the module for the first time, and it should not happen at all with the PyPi
    installation."""
    # This warning is not part of the specification since it is too dependent on this implementation's architecture to
    #  expect every implementation to need it.
    pass


class BuildingGenderedNounDataLogging(GRLogging):
    """This class enables/disables the logging of information when building the gendered-noun-data from which the
    gendered versions of nouns are read."""
    pass


class GRSyntaxParsingLogging(GRLogging):
    """This class enables/disables the logging of state traversion, characters and the step-by-step transforming result
    value of the part of template parsing that parses according to """
    pass

# A helper function to find all warnings in the module:


def get_all_subclasses(class_object):
    """Returns a list of all subclasses of a given class that are defined in the global scope."""
    return [globals()[w] for w in globals() if inspect.isclass(globals()[w]) and issubclass(globals()[w], class_object)]


# Define warning types:

WarningType = typing.Type[typing.Union[GRWarning, GRLogging]]
WarningSettingType = typing.Union[typing.Set[WarningType], typing.FrozenSet[WarningType]]

# Define standard values for all warnings enables/ all warnings disabled/ default:


ENABLE_ALL_LOGGING: WarningSettingType = frozenset(get_all_subclasses(GRLogging))
ENABLE_ALL_WARNINGS: WarningSettingType = frozenset(get_all_subclasses(GRWarning))
DISABLE_ALL_WARNINGS: WarningSettingType = frozenset()

ENABLE_DEFAULT_WARNINGS: WarningSettingType = ENABLE_ALL_WARNINGS

# WarningManager:


class WarningManager:
    """A bundle of functions to handle warning handling."""
    warning_settings_by_thread_id = dict()

    @staticmethod
    def set_warning_settings(warning_settings: WarningSettingType):
        """Sets the warning settings to warning_settings for the current thread (thread-save)."""
        WarningManager.warning_settings_by_thread_id[threading.get_ident()] = warning_settings

    @staticmethod
    def raise_warning(text: typing.Union[str, None], warning_type: WarningType):
        """Raises the given warning type with the given text if it is enabled for the current thread."""
        if text is None:
            text = warning_type.__doc__
        if threading.get_ident() not in WarningManager.warning_settings_by_thread_id:
            WarningManager.warning_settings_by_thread_id[threading.get_ident()] = ENABLE_DEFAULT_WARNINGS
        if warning_type in WarningManager.warning_settings_by_thread_id[threading.get_ident()]:
            ws.warn(text, warning_type)
        # ToDo: Make a pull request if you want children of GRLogging to use the logging-module rather than the warnings
        #  module. Note that this may cause the need to change the unittests, and may not require any changes except to
        #  this method and the GRLogging-objects parent class.
        # ToDo: Feel free to make a pull request if you know how to suppress line- and file information in warnings.
        #  or replace it with the lines from where it was logged
        #  (https://stackoverflow.com/questions/2654113/how-to-get-the-callers-method-name-in-the-called-method), but
        #  there would be some design decisions to be made about this since inspect.stack() tends to be very slow,
        #  amongst other things.
