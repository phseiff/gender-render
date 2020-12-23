"""
The interface to gender*render pronoun data representations presented to the user.
"""

from typing import Union

from . import warnings
from .parse_pronoun_data import IDPD, GRPD, GRPDParser


# a class representation for pronoun data, as defined by the spec:


class PronounData:
    """A representation for pronoun data as defined by the specification."""
    def __init__(self, pronoun_data: Union[str, GRPD, IDPD], takes_file_path=False,
                 warning_settings: warnings.WarningSettingType = warnings.ENABLE_DEFAULT_WARNINGS):

        warnings.WarningManager.set_warning_settings(warning_settings)

        # read from file (if necessary) and parse from JSON to a dict:
        if takes_file_path:
            pd_as_str = open(pronoun_data, "r").read()
        else:
            pd_as_str = pronoun_data
        if type(pronoun_data) is PronounData:
            self.grpd = pronoun_data.get_pd()
            return
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

    def get_pd(self):
        """Returns the PronounData representations actual pronoun data structure."""
        return self.grpd

    def is_idpd(self):
        """Checks whether it is a representation of individual pronoun data rather than gender*render pronoun data."""
        return list(self.grpd.keys()) == [""]
